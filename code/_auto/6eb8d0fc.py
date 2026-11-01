# @quantlab/output: 6eb8d0fc
class IPOFirstDayPredictor:
    """新股首日涨幅预测器"""

    def __init__(self, ipo_data: pd.DataFrame, market_data: pd.DataFrame):
        self.data = ipo_data
        self.market = market_data

    def engineer_features(self) -> pd.DataFrame:
        """构建预测特征"""
        df = self.data.copy()

        # 估值因子
        df['pe_discount'] = 1 - df['pe_ratio'] / df['industry_pe']
        df['pb_ratio_zscore'] = (df['pb_ratio'] - df['pb_ratio'].mean()) / df['pb_ratio'].std()

        # 认购热度
        df['log_subscription_ratio'] = np.log1p(df['online_oversubscription_ratio'])

        # 公司质量
        df['revenue_growth_3y'] = df['revenue_cagr_3y']
        df['profit_growth_3y'] = df['profit_cagr_3y']
        df['rd_ratio'] = df.get('rd_expense_ratio', 0)

        # 发行规模
        df['log_issue_amount'] = np.log(df['issue_price'] * df['issue_shares'])

        # 市场环境
        df['market_return_20d'] = df['list_date'].apply(
            lambda d: self._get_market_return_before(d, 20)
        )
        df['recent_ipo_avg_return'] = df['list_date'].apply(
            lambda d: self._get_recent_ipo_return(d, 60)
        )

        # 板块虚拟变量
        df = pd.get_dummies(df, columns=['board'], prefix='board')

        return df

    def _get_market_return_before(self, date, window: int) -> float:
        """获取给定日期前window天的市场收益"""
        end = self.market.index.searchsorted(date)
        start = max(0, end - window)
        if start >= end:
            return 0
        return self.market.iloc[start:end]['return'].sum()

    def _get_recent_ipo_return(self, date, window: int) -> float:
        """获取最近窗口内的新股平均收益"""
        recent = self.data[
            (self.data['list_date'] < date) &
            (self.data['list_date'] >= date - pd.Timedelta(days=window))
        ]
        if len(recent) == 0:
            return 0
        return recent['first_day_return'].mean()

    def train_model(self):
        """训练首日涨幅预测模型"""
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.model_selection import TimeSeriesSplit

        features = self.engineer_features()

        # 只使用已上市的IPO作为训练数据
        train_data = features[features['is_listed'] == 1].dropna()

        feature_cols = [c for c in train_data.columns
                       if c not in ['code', 'name', 'ipo_date', 'list_date',
                                   'first_day_return', 'is_break', 'is_listed']]

        X = train_data[feature_cols].select_dtypes(include=[np.number])
        y = train_data['first_day_return']

        tscv = TimeSeriesSplit(n_splits=5)

        model = GradientBoostingRegressor(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            random_state=42
        )
        model.fit(X, y)

        # 特征重要性
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

        return {
            'model': model,
            'feature_importance': feature_importance,
            'features': feature_cols
        }

    def predict_and_rank(self, upcoming_ipos: pd.DataFrame) -> pd.DataFrame:
        """预测即将发行的新股首日收益并排名"""
        result = self.train_model()

        features = self.engineer_features()

        upcoming = features[features['is_listed'] == 0]
        if len(upcoming) == 0:
            return pd.DataFrame()

        X = upcoming[result['features']].select_dtypes(include=[np.number])

        predictions = result['model'].predict(X.fillna(0))

        upcoming['predicted_return'] = predictions
        upcoming['rank'] = predictions.argsort()[::-1] + 1  # 1为最优

        # 风险标签
        upcoming['risk_label'] = pd.cut(
            predictions,
            bins=[-np.inf, -0.05, 0, 0.05, np.inf],
            labels=['HIGH_RISK', 'CAUTION', 'MODERATE', 'ATTRACTIVE']
        )

        return upcoming[['code', 'name', 'predicted_return', 'rank', 'risk_label']]

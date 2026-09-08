# @quantlab/output: e08f6003
continuous = pd.concat([group.iloc[:,1:].sum().idxmax() for _, group in monthly_data.groupby(pd.Grouper(freq='M'))])

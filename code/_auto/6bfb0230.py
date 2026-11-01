# @quantlab/output: 6bfb0230
rank_change = df['rank'].pct_change()
df['expected_sales'] = -rank_change * base_sales

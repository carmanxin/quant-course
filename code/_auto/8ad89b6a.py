# @quantlab/output: 8ad89b6a
import networkx as nx
import matplotlib.pyplot as plt

# 构建量化生态网络图
G = nx.DiGraph()

# 核心参与者
nodes = {
    '量化对冲基金': {'color': '#e74c3c', 'size': 3000},
    '自营交易公司': {'color': '#e74c3c', 'size': 2500},
    '银行做市商': {'color': '#3498db', 'size': 2500},
    '因子工厂': {'color': '#e74c3c', 'size': 2000},
    '数据供应商': {'color': '#2ecc71', 'size': 2000},
    '交易所': {'color': '#f39c12', 'size': 3000},
    '监管机构': {'color': '#9b59b6', 'size': 2000},
    '投资者': {'color': '#1abc9c', 'size': 2500},
    '经纪商': {'color': '#3498db', 'size': 2000},
    '技术平台': {'color': '#2ecc71', 'size': 2000},
}

for name, attr in nodes.items():
    G.add_node(name, **attr)

# 连接关系
edges = [
    ('投资者', '量化对冲基金'), ('量化对冲基金', '经纪商'),
    ('经纪商', '交易所'), ('投资者', '自营交易公司'),
    ('自营交易公司', '交易所'), ('交易所', '数据供应商'),
    ('数据供应商', '量化对冲基金'), ('数据供应商', '自营交易公司'),
    ('因子工厂', '量化对冲基金'), ('监管机构', '交易所'),
    ('技术平台', '量化对冲基金'), ('技术平台', '自营交易公司'),
    ('自营交易公司', '银行做市商'),
]

G.add_edges_from(edges)

# 绘制
pos = nx.spring_layout(G, seed=42)
colors = [G.nodes[n]['color'] for n in G.nodes]
sizes = [G.nodes[n]['size'] for n in G.nodes]

plt.figure(figsize=(14, 10))
nx.draw(G, pos, with_labels=True, node_color=colors, node_size=sizes,
        font_size=10, font_weight='bold', edge_color='gray',
        arrows=True, arrowsize=20, alpha=0.85,
        connectionstyle='arc3,rad=0.1')
plt.title('量化交易生态系统', fontsize=16, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.show()

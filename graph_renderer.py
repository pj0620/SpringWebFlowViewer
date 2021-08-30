import networkx as nx
import matplotlib.pyplot as plt
import pylab

render_settings = {
    "node_size": 2000,
    "edge_cmap": plt.cm.Reds,
    "with_labels": True,
    "node_shape": "o"
}

def render(G, colors):
    pos = nx.spectral_layout(G)
    nx.draw(G, node_color=colors, **render_settings)
    plt.savefig('plotgraph.png', dpi=300, bbox_inches='tight')
    plt.show()

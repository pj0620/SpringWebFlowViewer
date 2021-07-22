import networkx as nx
import matplotlib.pyplot as plt

render_settings = {
    "node_size": 2000,
    "edge_cmap": plt.cm.Reds,
    "with_labels": True,
    "node_shape": "o"
}

def render(G, colors):
    # play with this value to change the graph layout
    #  see __all__ list in 'networkx/drawing/layout.py'
    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, node_color=colors, pos=pos, **render_settings)
    # plt.savefig('flow.png', dpi=300, bbox_inches='tight')
    plt.show()

import networkx as nx
import matplotlib.pyplot as plt
from utils.namespace_utils import shorten_uri


def visualize_graph(graph):
    G = nx.DiGraph()
    node_labels = {}

    # Count node occurrences to determine node size
    node_counts = {}

    # Collect all predicates to analyze
    all_predicates = set()

    for s, p, o in graph:
        s_str = str(s)
        o_str = str(o)
        p_str = shorten_uri(p, graph.namespace_manager)

        G.add_edge(s_str, o_str, label=p_str)
        all_predicates.add(p_str.lower())

        # Count node occurrences
        node_counts[s_str] = node_counts.get(s_str, 0) + 1
        node_counts[o_str] = node_counts.get(o_str, 0) + 1

        node_labels[s_str] = shorten_uri(s, graph.namespace_manager)
        node_labels[o_str] = shorten_uri(o, graph.namespace_manager)

    # Automatically categorize predicates
    type_keywords = ['type', 'subclassof', 'instanceof']
    property_keywords = ['has', 'is', 'of', 'belongs', 'related', 'connected', 'linked',
                        'part', 'member', 'contains', 'in', 'at', 'on', 'by']

    # Use a hierarchical layout for better organization
    pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)

    # Calculate node sizes based on their importance (number of connections)
    node_sizes = {node: 300 + (count * 30) for node, count in node_counts.items()}

    # Draw nodes with varying sizes
    # nx.draw_networkx_nodes(G, pos,
    #                       node_size=[node_sizes[node] for node in G.nodes()],
    #                       node_color='#7ec8e3',
    #                       edgecolors='black',
    #                       node_shape='s',  # Use square shape for all nodes
    #                       linewidths=1.0,  # Consistent border width
    #                       alpha=0.8)

    # Group edges by type for better visualization
    type_edges = []
    property_edges = []
    other_edges = []

    for u, v, data in G.edges(data=True):
        label_lower = data['label'].lower()

        # Check if this is a type-related edge
        if any(keyword in label_lower for keyword in type_keywords):
            type_edges.append((u, v))
        # Check if this is a property-related edge
        elif any(keyword in label_lower for keyword in property_keywords):
            property_edges.append((u, v))
        # Otherwise, it's an "other" edge
        else:
            other_edges.append((u, v))

    # Check for bidirectional edges
    bidirectional_pairs = set()
    for u, v in G.edges():
        if G.has_edge(v, u):
            # Ensure we only add each pair once (in canonical order)
            pair = tuple(sorted([u, v]))
            bidirectional_pairs.add(pair)

    # Draw edges with different styles based on type
    # Type edges (blue, dashed)
    nx.draw_networkx_edges(G, pos, edgelist=type_edges,
                          arrows=True, arrowsize=15,
                          edge_color='blue',
                          width=1.0,
                          style='dashed',
                          alpha=0.7,
                          arrowstyle='-|>')

    # Property edges (red, solid)
    # For bidirectional edges, use curved lines
    curved_property_edges = [(u, v) for u, v in property_edges
                            if tuple(sorted([u, v])) in bidirectional_pairs]
    straight_property_edges = [e for e in property_edges if e not in curved_property_edges]

    # Draw curved property edges
    nx.draw_networkx_edges(G, pos, edgelist=curved_property_edges,
                          arrows=True, arrowsize=15,
                          edge_color='red',
                          width=1.5,
                          connectionstyle='arc3,rad=0.2',  # Curved edges
                          alpha=0.8,
                          arrowstyle='-|>')

    # Draw straight property edges
    nx.draw_networkx_edges(G, pos, edgelist=straight_property_edges,
                          arrows=True, arrowsize=15,
                          edge_color='red',
                          width=1.5,
                          alpha=0.8,
                          arrowstyle='-|>')

    # Other edges (gray)
    # For bidirectional edges, use curved lines
    curved_other_edges = [(u, v) for u, v in other_edges
                         if tuple(sorted([u, v])) in bidirectional_pairs]
    straight_other_edges = [e for e in other_edges if e not in curved_other_edges]

    # Draw curved other edges
    nx.draw_networkx_edges(G, pos, edgelist=curved_other_edges,
                          arrows=True, arrowsize=15,
                          edge_color='gray',
                          width=1.0,
                          connectionstyle='arc3,rad=0.2',  # Curved edges
                          alpha=0.6,
                          arrowstyle='-|>')

    # Draw straight other edges
    nx.draw_networkx_edges(G, pos, edgelist=straight_other_edges,
                          arrows=True, arrowsize=15,
                          edge_color='gray',
                          width=1.0,
                          alpha=0.6,
                          arrowstyle='-|>')

    # Draw edge labels with better positioning
    edge_labels = nx.get_edge_attributes(G, 'label')

    # Draw labels for type edges
    type_edge_labels = {(u, v): edge_labels[(u, v)] for u, v in type_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=type_edge_labels,
                                font_color='blue', font_size=8,
                                alpha=0.7,
                                label_pos=0.5)

    # Draw labels for property edges
    property_edge_labels = {(u, v): edge_labels[(u, v)] for u, v in property_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=property_edge_labels,
                                font_color='darkred', font_size=8,
                                alpha=0.8,
                                label_pos=0.3)

    # Draw labels for other edges
    other_edge_labels = {(u, v): edge_labels[(u, v)] for u, v in other_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=other_edge_labels,
                                font_color='black', font_size=8,
                                alpha=0.6,
                                label_pos=0.5)

    # Draw node labels with background for better readability
    # for node, (x, y) in pos.items():
    #     label = node_labels[node]
    #     plt.text(x, y, label,
    #             fontsize=9, ha='center', va='center',
    #             bbox=dict(boxstyle='round,pad=0.3',
    #                      facecolor='white',
    #                      edgecolor='gray',
    #                      alpha=0.8))

    for node, (x, y) in pos.items():
        label = node_labels[node]
        plt.text(x, y, label,
                 fontsize=9,
                 ha='center', va='center',
                 bbox=dict(boxstyle='round,pad=0.4',
                           facecolor='#7ec8e3',
                           edgecolor='black',
                           linewidth=1.0,
                           alpha=0.9))

    plt.title("RDF Graph Visualization")
    plt.axis('off')
    plt.tight_layout()
    
    # Add a legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='blue', lw=1, linestyle='dashed', label='Type Relation'),
        Line2D([0], [0], color='red', lw=1.5, label='Property Relation'),
        Line2D([0], [0], color='gray', lw=1, label='Other Relation')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.show()

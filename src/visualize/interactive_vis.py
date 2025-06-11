import dash
from dash import html
import dash_cytoscape as cyto
from rdflib.term import Literal
from utils.namespace_utils import shorten_uri


CHAR_WIDTH_PX = 6
PADDING_PX = 6

def visualize_graph(graph):
    elements = []
    node_ids = set()

    for s in graph.subjects():
        s_str = str(s)
        if s_str not in node_ids:
            label = graph.qname(s) if not isinstance(s, Literal) else str(s)
            est_diameter = len(label) * CHAR_WIDTH_PX + PADDING_PX
            elements.append({'data': {'id': s_str, 'label': label, 'size': est_diameter}})
            node_ids.add(s_str)

    for s, p, o in graph:
        s_str = str(s)
        o_str = str(o)
        pred_str = str(p)

        if isinstance(o, Literal):
            o_label = f'"{o}"'
        else:
            o_label = shorten_uri(o, graph.namespace_manager)

        if o_str not in node_ids:
            label = graph.qname(o) if not isinstance(o, Literal) else str(o)
            est_diameter = len(label) * CHAR_WIDTH_PX + PADDING_PX
            elements.append({'data': {'id': o_str, 'label': label, 'size': est_diameter}})
            node_ids.add(o_str)

        label = shorten_uri(p, graph.namespace_manager)

        elements.append({
            'data': {
                'source': s_str,
                'target': o_str,
                'label': label,
                'predicate_uri': pred_str
            }
        })

    stylesheet = [
        {'selector': 'node', 'style': {'label': 'data(label)', 'font-size': '10px',
                                       'background-color': '#e6e6fa', 'color': '#580f41',
                                       'width': 'data(size)', 'height': 'data(size)', 'shape': 'ellipse',
                                       'text-valign': 'center',
                                       'text-halign': 'center',
                                       }},
        {'selector': 'edge', 'style': {'label': 'data(label)', 'line-color': '#888',
                                       'target-arrow-color': '#888', 'target-arrow-shape': 'vee',
                                       'curve-style': 'bezier', 'width': 2, 'font-size': '10px',
                                       'text-rotation': 'autorotate', 'text-margin-y': -10}},
    ]

    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.H1("Interactive RDF Graph with Cytoscape"),
        cyto.Cytoscape(
            id='cytoscape',
            elements=elements,
            layout={'name': 'cose'},
            stylesheet=stylesheet,
            style={'width': '100vw', 'height': '100vh', 'border': '1px solid #ccc'},
            boxSelectionEnabled=False,
            autolock=False,
            userZoomingEnabled=True,
        )
    ])

    app.run(debug=True)

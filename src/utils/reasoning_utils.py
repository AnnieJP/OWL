from rdflib import Graph, URIRef

def augment_inverse_properties(graph, inverse_pairs):
    """
    Augments a graph by adding inverse relationship triples.
    
    Args:
        graph: An RDFLib Graph object to augment
        inverse_pairs: Dictionary mapping property URIs to their inverse property URIs
    
    Returns:
        int: Number of triples added
    """
    added_count = 0
    for s, p, o in list(graph):
        p_str = str(p)
        if p_str in inverse_pairs:
            inverse_p = URIRef(inverse_pairs[p_str])
            # Add the inverse relationship if it doesn't exist
            if (o, inverse_p, s) not in graph:
                graph.add((o, inverse_p, s))
                added_count += 1
    
    return added_count

def augment_symmetric_properties(graph, symmetric_props):
    """
    Augments a graph by adding symmetric relationship triples.

    Args:
        graph: An RDFLib Graph object to augment
        symmetric_props: Set of URIRefs representing symmetric properties

    Returns:
        int: Number of triples added
    """
    added_count = 0
    for s, p, o in list(graph):
        if p in symmetric_props:
            if (o, p, s) not in graph:
                graph.add((o, p, s))
                added_count += 1
    return added_count
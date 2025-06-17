import os
from rdflib import Graph, URIRef, Literal, RDF, OWL
from owlready2 import get_ontology, sync_reasoner_hermit
import tempfile
from utils.reasoning_utils import augment_inverse_properties, augment_symmetric_properties
from utils.logging_utils import logger
from input.csv_to_ttl import CSVConverter

def convert_ttl_to_owl(ttl_path):
    """
    Converts a Turtle (.ttl) file to RDF/XML (.owl) format so Owlready2 can read it.
    Returns the path to the generated .owl file.
    """
    
    g = Graph()
    # Use file:// URI format for RDFlib
    g.parse(ttl_path, format="turtle")

    owl_path = ttl_path.replace(".ttl", ".owl")
    g.serialize(destination=owl_path, format="xml")

    logger.info("✅ Converted Turtle file to RDF/XML for reasoning.")
    return owl_path

def apply_reasoning(owl_path):
    """
    Applies OWL reasoning using Owlready2 and HermiT, returning inferred triples.
    """
    if owl_path.endswith(".csv"):

        converter = CSVConverter(owl_path, base_namespace="http://example.org/")
        ttl_path = converter.convert()
        g = converter.graph
        owl_path = ttl_path

    if owl_path.endswith(".ttl"):
        owl_path = convert_ttl_to_owl(owl_path)

    logger.info(f"🧠 Loading ontology from {owl_path} and performing reasoning...")

    # First, load the original graph to preserve namespaces and check structure
    original_graph = Graph()
    original_graph.parse(owl_path)
    logger.info(f"Original graph contains {len(original_graph)} triples")

    # Find inverse property definitions
    owl_ns = "http://www.w3.org/2002/07/owl#"
    inverse_pairs = {}
    for s, p, o in original_graph:
        if p == URIRef(f"{owl_ns}inverseOf"):
            inverse_pairs[str(s)] = str(o)
            inverse_pairs[str(o)] = str(s)

    symmetric_properties = set()
    for s, p, o in original_graph.triples((None, RDF.type, OWL.SymmetricProperty)):
        symmetric_properties.add(s)

    logger.info(f"🔁 Symmetric Properties found: {symmetric_properties}")

    # Load ontology and run reasoner
    onto = get_ontology(f"file://{os.path.abspath(owl_path)}").load()

    try:
        with onto:
            sync_reasoner_hermit(infer_property_values=True)
        logger.info("✅ Reasoning completed successfully")
    except Exception as e:
        logger.error(f"❌ Error during reasoning: {e}")
        logger.info("Reasoning failed. Returning original graph.")
        return original_graph  # Return original graph if reasoning fails

    # Save the inferred ontology to a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".owl", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    onto.save(temp_path)

    # Parse the inferred ontology into a new graph
    inferred_graph = Graph()
    inferred_graph.parse(temp_path)
    logger.info(f"Inferred graph contains {len(inferred_graph)} triples")

    # Create a filtered graph with only the data triples
    filtered_graph = Graph()

    # Copy all namespaces
    for prefix, namespace in inferred_graph.namespaces():
        filtered_graph.bind(prefix, namespace)

    # Define namespaces to filter
    rdfs_ns = "http://www.w3.org/2000/01/rdf-schema#"
    rdf_ns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

    # Add all triples from the inferred graph that are not ontology structure
    for s, p, o in inferred_graph:
        p_str = str(p)
        o_str = str(o)

        # Skip all OWL-related triples
        if p_str.startswith(owl_ns) or o_str.startswith(owl_ns):
            continue

        # Skip RDFS-related triples
        if p_str.startswith(rdfs_ns):
            continue

        # Skip RDF type assertions for classes
        if p == URIRef(f"{rdf_ns}type") and (
            o_str.startswith(owl_ns) or o_str.startswith(rdfs_ns)
        ):
            continue

        # Keep everything else
        filtered_graph.add((s, p, o))

    symmetric_added = augment_symmetric_properties(filtered_graph, symmetric_properties)
    if symmetric_added > 0:
        logger.info(f"✅ Manually added {symmetric_added} symmetric relationships")

    # Apply property augmentation
    inverse_added = augment_inverse_properties(filtered_graph, inverse_pairs)
    if inverse_added > 0:
        logger.info(f"✅ Manually added {inverse_added} inverse relationships")
    


    # Clean up the temporary file
    os.unlink(temp_path)

    logger.info(f"Final filtered graph contains {len(filtered_graph)} triples")
    return filtered_graph
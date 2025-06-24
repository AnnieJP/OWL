# input/triple_loader.py

from rdflib import URIRef, Literal, Graph
import os
from utils.logging_utils import logger
from input.csv_to_ttl import CSVConverter

def load_from_file(filename, graph_manager):
    """
    Load RDF data from a file into the graph manager.
    Supports .ttl (Turtle) and .csv files.
    """
    if filename.lower().endswith('.ttl'):
        try:
            temp_graph = Graph()
            logger.info(f"Parsing {filename} as Turtle format")
            temp_graph.parse(filename, format='turtle')

            # Add all triples to the graph manager
            for s, p, o in temp_graph:
                graph_manager.get_graph().add((s, p, o))

            logger.info(f"✅ Loaded {len(temp_graph)} triples from {filename}")
            return

        except Exception as e:
            logger.error(f"❌ Error parsing Turtle file {filename}: {e}")
            exit(1)

    elif filename.lower().endswith('.csv'):
        try:
            logger.info(f"Parsing {filename} as CSV format")

            
            # Create TTL filename with same base name as CSV
            base_name = os.path.splitext(filename)[0]
            ttl_filename = f"{base_name}.ttl"
            
            # Convert CSV to TTL
            converter = CSVConverter(filename)
            ttl_filename = converter.convert()
            temp_graph = converter.graph
            
            # Add all triples to the graph manager
            for s, p, o in temp_graph:
                graph_manager.get_graph().add((s, p, o))
            
            logger.info(f"✅ Loaded {len(temp_graph)} triples from {filename}")
            logger.info(f"✅ Saved TTL representation to {ttl_filename}")
            return
            
        except Exception as e:
            logger.error(f"❌ Error parsing CSV file {filename}: {e}")
            exit(1)

    else:
        logger.error(f"❌ Unsupported file format: {filename}")
        logger.error("   Please use .ttl or .csv files")
        exit(1)
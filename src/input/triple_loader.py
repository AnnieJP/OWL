# input/triple_loader.py

from rdflib import URIRef, Literal, Graph
import os
import tempfile

def load_from_file(filename, graph_manager):
    """
    Load RDF data from a file into the graph manager.
    Supports .ttl (Turtle) and .csv files.
    """
    if filename.lower().endswith('.ttl'):
        try:
            temp_graph = Graph()
            print(f"Parsing {filename} as Turtle format")
            temp_graph.parse(filename, format='turtle')

            # Add all triples to the graph manager
            for s, p, o in temp_graph:
                graph_manager.get_graph().add((s, p, o))

            print(f"✅ Loaded {len(temp_graph)} triples from {filename}")
            return

        except Exception as e:
            print(f"❌ Error parsing Turtle file {filename}: {e}")
            exit(1)

    elif filename.lower().endswith('.csv'):
        try:
            print(f"Parsing {filename} as CSV format")
            from input.csv_to_ttl import csv_file_to_ttl
            
            # Create TTL filename with same base name as CSV
            base_name = os.path.splitext(filename)[0]
            ttl_filename = f"{base_name}.ttl"
            
            # Convert CSV to TTL
            temp_graph = csv_file_to_ttl(filename, ttl_filename)
            
            # Add all triples to the graph manager
            for s, p, o in temp_graph:
                graph_manager.get_graph().add((s, p, o))
            
            print(f"✅ Loaded {len(temp_graph)} triples from {filename}")
            print(f"✅ Saved TTL representation to {ttl_filename}")
            return
            
        except Exception as e:
            print(f"❌ Error parsing CSV file {filename}: {e}")
            exit(1)

    else:
        print(f"❌ Unsupported file format: {filename}")
        print("   Please use .ttl or .csv files")
        exit(1)
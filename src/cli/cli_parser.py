# cli/cli_parser.py

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="RDF Triple Visualizer CLI")

    input_group = parser.add_mutually_exclusive_group(required=True)
    
    input_group.add_argument(
        "-f", "--file",
        help="Input file with RDF triples"
    )
    
    input_group.add_argument(
        "-r", "--reason",
        help="Run reasoning on an OWL/TTL file (provide file path)"
    )

    parser.add_argument(
        "-i", "--interactive",
        action='store_true',
        help="Enable interactive Dash visualization (otherwise matplotlib is used)"
    )

    parser.add_argument(
        "-q", "--query",
        help="Optional SPARQL query to run on the RDF graph before visualizing"
    )

    parser.add_argument(
        "-c", "--config",
        help="Path to config file to generate RDF (instead of providing triples directly)"
    )

    return parser.parse_args()
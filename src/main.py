from cli.cli_parser import parse_args
from core.graph_manager import GraphManager
from input.triple_loader import load_from_file
import visualize.interactive_vis as i
import visualize.static_vis as v
from core.reasoning import apply_reasoning
from utils.logging_utils import logger

def main():
    args = parse_args()
    graph_manager = GraphManager()

    # Reasoning mode takes precedence and skips other input
    if args.reason:
        inferred_triples = apply_reasoning(args.reason)
            
        for triple in inferred_triples:
            graph_manager.get_graph().add(triple)
    elif args.file:
        load_from_file(args.file, graph_manager)
    else:
        logger.error("Please provide an input file with the -f/--file option")
        exit(1)

    g = graph_manager.get_graph()

    # Visualize
    if args.interactive:
        i.visualize_graph(g)
    else:
        v.visualize_graph(g)

if __name__ == "__main__":
    main()

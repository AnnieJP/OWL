import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD

def csv_file_to_ttl(file_path: str, output_file: str, base_namespace: str = "http://example.org/"):
    """
    Convert a CSV file to Turtle RDF format.
    
    The CSV should follow these conventions:
    - First column is the subject identifier
    - Column names can include type information:
      - name@string: datatype property with string type
      - worksIn:Department: object property referencing Department class
      - manager:@Employee: object property explicitly referencing Employee class
    
    Args:
        file_path: Path to the CSV file
        output_file: Path to save the TTL file
        base_namespace: Base URI for the generated RDF
        
    Returns:
        rdflib.Graph object containing the RDF data
    """
    # Load CSV
    df = pd.read_csv(file_path)

    # Namespaces
    EX = Namespace(base_namespace)
    g = Graph()
    g.bind("", EX)

    # Datatype map
    datatype_map = {
        "string": XSD.string,
        "integer": XSD.integer,
        "float": XSD.float,
        "boolean": XSD.boolean
    }

    headers = list(df.columns)
    subject_col = headers[0]
    property_defs = {}

    for col in headers[1:]:
        prop_name = col.strip()
        dtype = None
        obj_class = None

        if ":@" in col:
            # Object property with explicit class
            prop_name, class_name = col.split(":@")
            prop_name = prop_name.strip()
            obj_class = class_name.strip()

        elif "@" in col:
            # Datatype property
            prop_name, type_name = col.split("@")
            prop_name = prop_name.strip()
            dtype = datatype_map.get(type_name.strip(), XSD.string)

        elif ":" in col:
            # Object property with implicit class
            prop_name, class_name = col.split(":")
            prop_name = prop_name.strip()
            obj_class = class_name.strip()

        property_defs[col] = {
            "predicate": EX[prop_name],
            "datatype": dtype,
            "object_class": obj_class
        }

    # Convert rows to RDF
    for _, row in df.iterrows():
        subject_uri = EX[str(row[subject_col])]
        g.add((subject_uri, RDF.type, EX[subject_col])) # default top class

        for col in headers[1:]:
            val = row[col]
            if pd.isna(val):
                continue

            pred = property_defs[col]["predicate"]
            dtype = property_defs[col]["datatype"]
            obj_cls = property_defs[col]["object_class"]

            if dtype:
                g.add((subject_uri, pred, Literal(val, datatype=dtype)))
            elif obj_cls:
                object_uri = EX[str(val)]
                g.add((subject_uri, pred, object_uri))
                g.add((object_uri, RDF.type, EX[obj_cls]))
            else:
                g.add((subject_uri, pred, Literal(val, datatype=XSD.string)))

    g.serialize(destination=output_file, format="turtle")
    return g
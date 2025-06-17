import os
import pandas as pd
from rdflib import Graph, Literal, Namespace, XSD, RDF, OWL, RDFS
from utils.logging_utils import logger

class CSVConverter:

    type_map = {
        "symmetric": OWL.SymmetricProperty,
        "functional": OWL.FunctionalProperty,
        "inverseFunctional": OWL.InverseFunctionalProperty,
        "transitive": OWL.TransitiveProperty,
        "reflexive": OWL.ReflexiveProperty,
        "irreflexive": OWL.IrreflexiveProperty,
        "asymmetric": OWL.AsymmetricProperty
    }

    datatype_map = {
        "string": XSD.string,
        "integer": XSD.integer,
        "float": XSD.float,
        "boolean": XSD.boolean
    }

    annotation_map = {
        "domain": RDFS.domain,
        "range": RDFS.range,
        "inverseOf": OWL.inverseOf,
        "subPropertyOf": RDFS.subPropertyOf,
        "equivalentProperty": OWL.equivalentProperty
    }

    def __init__(self, file_path, base_namespace = "http://example.org/"):
        self.file_path = file_path
        self.base_namespace = base_namespace
        self.output_file = self._derive_output_path()
        self.df = pd.read_csv(self.file_path)
        self.graph = Graph()
        self.ns = Namespace(self.base_namespace)
        self.graph.bind("", self.ns)
        self.property_defs = {}
        self.subject_col = None
        self._parse_headers()

    def _derive_output_path(self):
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        logger.info(f"Deriving output path for {base_name}")
        return os.path.join(os.path.dirname(self.file_path), f"{base_name}.ttl")

    def _parse_headers(self):
        headers = list(self.df.columns)
        self.subject_col = headers[0]

        for col in headers[1:]:
            prop_name = col.strip()
            dtype = None
            obj_class = None

            if "@" in col:
                prop_name, type_name = col.split("@")
                prop_name = prop_name.strip()
                dtype = self.datatype_map.get(type_name.strip(), XSD.string)

            elif ":" in col:
                prop_name, class_name = col.split(":")
                prop_name = prop_name.strip()
                obj_class = class_name.strip()

            self.property_defs[col] = {
                "predicate": self.ns[prop_name],
                "datatype": dtype,
                "object_class": obj_class
            }

    def _build_graph(self):
        g = Graph()
        g.bind("", self.ns)

        for _, row in self.df.iterrows():
            subject_uri = self.ns[str(row[self.subject_col])]
            g.add((subject_uri, RDF.type, self.ns[self.subject_col]))

            for col in list(self.df.columns)[1:]:
                val = row[col]
                if pd.isna(val):
                    continue

                pred = self.property_defs[col]["predicate"]
                dtype = self.property_defs[col]["datatype"]
                obj_cls = self.property_defs[col]["object_class"]

                if dtype:
                    g.add((subject_uri, pred, Literal(val, datatype=dtype)))
                elif obj_cls:
                    object_uri = self.ns[str(val)]
                    g.add((subject_uri, pred, object_uri))
                    g.add((object_uri, RDF.type, self.ns[obj_cls]))
                else:
                    g.add((subject_uri, pred, Literal(val, datatype=XSD.string)))

        return g

    def convert(self, output_file: str = None):
        if output_file is None:
            output_file = self.output_file
        g = self._build_graph()
        g.serialize(destination=output_file, format="turtle")
        return output_file




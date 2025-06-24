import os
import pandas as pd
from rdflib import Graph, Literal, Namespace, XSD, RDF, OWL, RDFS

class CSVConverter:

    def __init__(self, file_path, base_namespace="http://example.org/"):
        self.file_path = file_path
        self.base_namespace = base_namespace
        self.output_file = self._derive_output_path()
        self.df = pd.read_csv(self.file_path)
        self.graph = Graph()
        self.ns = Namespace(self.base_namespace)
        self.graph.bind("", self.ns)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("xsd", XSD)
        self.graph.bind("rdf", RDF)

        self.annotation_map = {
            "domain": RDFS.domain,
            "range": RDFS.range
        }

        self.property_type_map = {
            "functional": OWL.FunctionalProperty,
            "symmetric": OWL.SymmetricProperty,
            "transitive": OWL.TransitiveProperty,
            "reflexive": OWL.ReflexiveProperty,
            "irreflexive": OWL.IrreflexiveProperty,
            "asymmetric": OWL.AsymmetricProperty,
            "inverseFunctional": OWL.InverseFunctionalProperty
        }

        self.data_type_map = {
            "string": XSD.string,
            "integer": XSD.integer,
            "float": XSD.float,
            "boolean": XSD.boolean,
            "date": XSD.date,
            "dateTime": XSD.dateTime
        }

        self.property_defs = {}
        self.subject_col = None
        self._parse_headers()

    def _derive_output_path(self):
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        return os.path.join(os.path.dirname(self.file_path), f"{base_name}.ttl")

    def _parse_headers(self):
        headers = list(self.df.columns)
        self.subject_col = headers[0]
        self.graph.add((self.ns[self.subject_col], RDF.type, OWL.Class))

        metadata_row = self.df.iloc[0] if len(self.df) > 0 else None

        for col in headers[1:]:
            prop_name = col.strip()
            dtype = None
            obj_class = None

            if "@" in col:
                prop_name, type_name = col.split("@")
                prop_name = prop_name.strip()
                dtype = self.data_type_map.get(type_name.strip(), XSD.string)
            elif ":" in col:
                prop_name, class_name = col.split(":")
                prop_name = prop_name.strip()
                obj_class = class_name.strip()
                self.graph.add((self.ns[obj_class], RDF.type, OWL.Class))

            pred_uri = self.ns[prop_name]

            if dtype:
                self.graph.add((pred_uri, RDF.type, OWL.DatatypeProperty))
            elif obj_class:
                self.graph.add((pred_uri, RDF.type, OWL.ObjectProperty))
            else:
                self.graph.add((pred_uri, RDF.type, RDF.Property))

            self.property_defs[col] = {
                "predicate": pred_uri,
                "datatype": dtype,
                "object_class": obj_class
            }

            if metadata_row is not None:
                metadata_value = metadata_row[col]
                if not pd.isna(metadata_value) and str(metadata_value).strip():
                    self._process_property_metadata(pred_uri, metadata_value)

    def _process_property_metadata(self, pred_uri, metadata_str):
        if not isinstance(metadata_str, str) or not metadata_str.strip():
            return

        parts = [part.strip() for part in metadata_str.split('|')]

        for part in parts:
            if ":" in part:
                key, value = part.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key in self.annotation_map:
                    self.graph.add((pred_uri, self.annotation_map[key], self.ns[value]))
                elif key == "inverseOf": #testing process
                    self.graph.add((pred_uri, OWL.inverseOf, self.ns[value]))
                elif key in self.property_type_map:
                    self.graph.add((pred_uri, RDF.type, self.property_type_map[key]))
            else:
                prop_type = part.strip()
                if prop_type in self.property_type_map:
                    self.graph.add((pred_uri, RDF.type, self.property_type_map[prop_type]))

    def _build_graph(self):
        g = self.graph

        for idx, row in self.df.iterrows():
            if idx == 0:
                continue

            if pd.isna(row[self.subject_col]) or str(row[self.subject_col]).strip() == '':
                continue

            subject_id = str(row[self.subject_col])
            subject_uri = self.ns[subject_id]

            g.add((subject_uri, RDF.type, self.ns[self.subject_col]))

            for col in self.df.columns[1:]:
                if pd.isna(row[col]):
                    continue

                value = row[col]
                prop_def = self.property_defs[col]
                pred_uri = prop_def["predicate"]
                dtype = prop_def["datatype"]
                obj_class = prop_def["object_class"]

                if dtype:
                    g.add((subject_uri, pred_uri, Literal(value, datatype=dtype)))
                elif obj_class:
                    object_uri = self.ns[str(value)]
                    g.add((subject_uri, pred_uri, object_uri))
                    g.add((object_uri, RDF.type, self.ns[obj_class]))
                else:
                    g.add((subject_uri, pred_uri, Literal(str(value))))

        return g

    def convert(self, output_file: str = None):
        if output_file is None:
            output_file = self.output_file
        g = self._build_graph()
        g.serialize(destination=output_file, format="turtle")
        return output_file

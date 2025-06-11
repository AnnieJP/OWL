from rdflib.namespace import split_uri

def shorten_uri(uri, ns_manager):
    """
    Returns a QName for the given URI using the graph's namespace manager.
    If the namespace is not bound, attempts to bind it dynamically.
    """
    try:
        return ns_manager.qname(uri)
    except:
        try:
            namespace, name = split_uri(uri)
            prefix = generate_prefix(ns_manager)
            ns_manager.bind(prefix, namespace)
            return ns_manager.qname(uri)
        except Exception:
            return str(uri)

def generate_prefix(ns_manager):
    existing = set(prefix for prefix, _ in ns_manager.namespaces())
    index = 1
    while True:
        candidate = f'ns{index}'
        if candidate not in existing:
            return candidate
        index += 1

import turbopuffer as tpuf

def delete_namespace(namespace_name: str):
    ns = tpuf.Namespace(namespace_name)
    # If an error occurs, this call raises a tpuf.APIError if a retry was not successful.
    ns.delete_all()
    
if __name__ == "__main__":
    delete_namespace("coderag")
    delete_namespace("code-rag")
    delete_namespace("sephora-tiktok-trends")

from config.env import env


def serialize_document_path(document):
    """
    Serialize document path with the configured media domain.

    Args:
        document: Document instance or None

    Returns:
        str: Full URL of the document or None if document is None
    """
    if document and document.document_path:
        url = document.document_path.url
        minio_storage_endpoint = env.str("MINIO_STORAGE_ENDPOINT")
        use_https = env.str("MINIO_STORAGE_USE_HTTPS")

        protocol = "https://" if use_https == "true" else "http://"
        media_domain = f"{protocol}{minio_storage_endpoint}"

        # Remove any existing protocol from the URL
        url = url.replace("http://", "").replace("https://", "")
        # Remove any existing protocol from the storage endpoint
        clean_endpoint = minio_storage_endpoint.replace("http://", "").replace("https://", "")

        # Replace the domain in the URL
        return url.replace(clean_endpoint, media_domain)
    return None

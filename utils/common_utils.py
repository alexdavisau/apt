def normalize_url(url):
    """
    Ensures that the provided URL has a scheme (https:// or http://).
    Defaults to https:// if no scheme is provided.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    # Optionally strip trailing slashes
    url = url.rstrip("/")
    return url
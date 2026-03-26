from urllib.parse import urlparse


def validate_url(url: str) -> str:
    """Validate and normalize a presentation URL. Returns normalized URL or raises ValueError."""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path

    # pitch.com
    if host in ('pitch.com', 'www.pitch.com'):
        parts = path.strip('/').split('/')
        if len(parts) != 2 or parts[0] != 'v':
            raise ValueError(
                "Invalid Pitch URL. Expected format: https://pitch.com/v/your-deck-slug"
            )
        return url

    # Google Slides
    if host == 'docs.google.com':
        if path.startswith('/presentation/d/e/') and '/pub' in path:
            # Normalize: strip query string after /pub
            pub_index = path.index('/pub') + len('/pub')
            normalized_path = path[:pub_index]
            return f"https://docs.google.com{normalized_path}"
        raise ValueError(
            "Invalid Google Slides URL. Only Publish to Web links are supported "
            "(the URL should end with /pub). "
            "Generate one via File > Share > Publish to web."
        )

    # Canva
    if host == 'www.canva.com':
        if path.endswith('/view'):
            return url
        raise ValueError(
            "Invalid Canva URL. Only public view links are supported "
            "(the URL should end with /view)."
        )

    # Figma
    if host == 'www.figma.com':
        if path.startswith('/deck/'):
            return url
        if path.startswith('/slides/'):
            corrected = url.replace('/slides/', '/deck/', 1)
            print(f"Note: corrected Figma URL from /slides/ to /deck/ -> {corrected}")
            return corrected
        raise ValueError(
            "Invalid Figma URL. Expected format: https://www.figma.com/deck/your-deck-id"
        )

    # Papermark
    if 'papermark.com' in host:
        import re
        if not re.search(r'papermark\.com/view/[a-zA-Z0-9]+', url):
            raise ValueError("Papermark URL must be in format: https://www.papermark.com/view/{id}")
        return url

    raise ValueError(
        "Unsupported URL. Supported platforms: pitch.com, Google Slides, Canva, Figma, Papermark"
    )

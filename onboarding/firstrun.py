from onboarding.url_validator import validate_url

EXAMPLE_URLS = [
    "  pitch.com       https://pitch.com/v/your-deck-slug",
    "  Google Slides   https://docs.google.com/presentation/d/e/.../pub",
    "  Canva           https://www.canva.com/design/.../view",
    "  Figma           https://www.figma.com/deck/...",
]


def run_interactive() -> str:
    """Interactive flow when no URL is provided. Returns validated URL."""
    print("pitch-to-pdf: convert any presentation to a searchable PDF\n")

    print("Supported platforms:")
    for line in EXAMPLE_URLS:
        print(line)
    print()

    while True:
        try:
            url = input("Paste the presentation URL: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            raise SystemExit(0)

        if not url:
            print("No URL entered. Please paste a URL from one of the supported platforms.\n")
            continue

        try:
            return validate_url(url)
        except ValueError as e:
            print(f"Error: {e}\n")

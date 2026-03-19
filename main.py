import argparse
import sys
from utils.slide_downloader import SlideDownloader

if __name__ == '__main__':

    # Parsing input args
    parser = argparse.ArgumentParser()
    parser.add_argument('url', nargs='?', help='The url to download the slides from')
    parser.add_argument('-r', '--resolution', help='The slide resolution, HD, 4K or 8K allowed', default='4K')
    parser.add_argument('--disable-headless', action='store_true', dest='disable_headless', help='Disable headless mode')
    parser.add_argument('--skip-ocr', action='store_true', dest='skip_ocr', help='Disable OCR')
    args = parser.parse_args()

    # Warn if Tesseract is missing and OCR is enabled
    if not args.skip_ocr:
        from onboarding.dependencies import check_dependencies, print_dependency_help
        missing = check_dependencies()
        if missing:
            print_dependency_help(missing)
            print("(Run with --skip-ocr to skip OCR and avoid this requirement.)\n")

    # Determine URL (interactive if not provided)
    url = args.url
    if not url:
        from onboarding.firstrun import run_interactive
        url = run_interactive()
    else:
        from onboarding.url_validator import validate_url
        try:
            url = validate_url(url)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Saving the presentation as a PDF
    try:
        sd = SlideDownloader(args.resolution, args.disable_headless)
        pdf_path = sd.download(url)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Running ocr.
    if not args.skip_ocr:
        print('\nRunning OCR... (disable with the flag --skip-ocr)')
        import ocrmypdf
        ocrmypdf.ocr(pdf_path, pdf_path, deskew=True)
        print('OCR finished!')

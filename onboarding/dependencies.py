import platform
import shutil


def check_dependencies() -> list[str]:
    """Returns list of missing dependency descriptions."""
    missing = []
    if not shutil.which('tesseract'):
        missing.append('Tesseract (optional, needed for OCR)')
    return missing


def print_dependency_help(missing: list[str]) -> None:
    """Print platform-specific install instructions for missing deps."""
    if not missing:
        return

    system = platform.system()
    print("\nMissing dependencies:")
    for dep in missing:
        print(f"  - {dep}")

    print()
    if system == 'Darwin':
        print("Install with Homebrew:")
        if any('Tesseract' in d for d in missing):
            print("  brew install tesseract")
    elif system == 'Windows':
        print("Install instructions:")
        if any('Tesseract' in d for d in missing):
            print("  Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
            print("  (or: choco install tesseract)")
    else:
        print("Install with your package manager:")
        if any('Tesseract' in d for d in missing):
            print("  sudo apt install tesseract-ocr     # Debian/Ubuntu")
            print("  sudo dnf install tesseract         # Fedora")

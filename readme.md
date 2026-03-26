# Download PDFs from presentation platforms
Simple python script to download a presentation as searchable PDF.

## Supported platforms
- Pitch.com
- Google Slides' "Publish to Web" mode
- Figma Slides
- Canva
- Papermark

## Usage
Install the requirements and run the script via:
```bash
python main.py url [-r resolution] [--skip-ocr] [--disable-headless]
```

Valid resolutions are HD, 4K and 8K. Default resolution is 4K.
By default runs in headless mode.

## Requirements
Base functionality requires Selenium, Pillow and tqdm. If you want OCR you also need to install ocrmypdf and it's dependencies. If you prefer not to, run the script with the --skip-ocr flag.  
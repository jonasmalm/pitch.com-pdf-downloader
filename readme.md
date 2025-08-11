# Download PDF from Pitch.com
Simple python script to download a presentations as searchable PDF. 

## Supported platforms
- Pitch.com 
- Google Slides' "Publish to Web" mode
- Figma Slides
- Canva

## Usage
Install the requirements and run the script via:
```bash
python main.py url [-r resolution] [--skip-ocr] [--skip-border-removal] [--disable-headless]
```

Valid resolutions are HD, 4K and 8K. Default resolution is 4K.
Border removal removes black borders around the slide, if present, and is by default on.
By default run in headless mode.

## Requirements
Base functionality requires Selenium + Chromedriver, Pillow and tqdm. If you want OCR you also need to install ocrmypdf and it's dependencies. If you prefer not to, run the script with the --skip-ocr flag.  
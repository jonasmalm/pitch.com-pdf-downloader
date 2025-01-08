# Download PDF from Pitch.com
Simple python script to download a presentations as searchable PDF. 

## Supported platforms
- Pitch.com 
- Google Slides' "Publish to Web" mode
- Figma Slides

Previously had support for Canva, but now blocked by bot detection.

## Usage
Install the requirements and run the script via:
```bash
python main.py url [-r resolution] [--skip-ocr]
```

Valid resolutions are HD, 4K and 8K. Default resolution is 4K.

## Requirements
Base functionality requires Selenium + Chromedriver, Pillow and tqdm. If you want OCR you also need to install ocrmypdf and it's dependencies. If you prefer not to, run the script with the --skip-ocr flag.  
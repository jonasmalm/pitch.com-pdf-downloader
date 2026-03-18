import argparse
from utils.slide_downloader import SlideDownloader

if __name__ == '__main__':

    # Parsing input args
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help = 'The url to download the slides from')
    parser.add_argument('-r', '--resolution', help = 'The slide resolution, HD, 4K or 8K allowed', default = '4K')
    parser.add_argument('--disable-headless', action = 'store_true', dest = 'disable_headless', help = 'Disable headless mode')
    parser.add_argument('--skip-ocr', action = 'store_true', dest = 'skip_ocr', help = 'Disable OCR')
    args = parser.parse_args()

    # Saving the presentation as a PDF
    sd = SlideDownloader(args.resolution, args.disable_headless)
    pdf_path = sd.download(args.url)

    # Running ocr. 
    if not args.skip_ocr:
        print('\nRunning OCR... (disable with the flag --skip-ocr)')
        import ocrmypdf
        ocrmypdf.ocr(pdf_path, pdf_path, deskew = True) 
        print('OCR finished!')


    

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from PIL import Image, ImageChops
from io import BytesIO

from tqdm import tqdm
import time

from utils import sources


class SlideDownloader:

    def __init__(self, resolution, disable_headless):

        chrome_options = Options()
        
        if not disable_headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--log-level=3')

        # Setting resolution
        if resolution == 'HD':
            res = 'window-size=1920,1080'
        elif resolution == '4K':
            res = 'window-size=3840,2160'
        elif resolution == '8K':
            res = 'window-size=7680,4320'
        else:
            raise Exception('Only HD, 4K and 8K resolutions allowed!')
        chrome_options.add_argument(res)

        # Adding argument to disable the AutomationControlled flag 
        chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
        
        # Exclude the collection of enable-automation switches 
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        
        # Turn-off userAutomationExtension 
        chrome_options.add_experimental_option("useAutomationExtension", False) 

        # Initializing the driver
        self.driver = webdriver.Chrome(options = chrome_options)

        # Changing the property of the navigator value for webdriver to undefined 
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    

    def _crop_black_borders(self, png):
        """
        Returns the bounding box for cropping black borders from a PNG image.
        """
        img = Image.open(BytesIO(png)).convert("RGB")
        bg = Image.new("RGB", img.size, (0, 0, 0))  # Black background for comparison
        diff = ImageChops.difference(img, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        return bbox if bbox else (0, 0, img.size[0], img.size[1])

    def _apply_consistent_cropping(self, png, bbox):
        """
        Applies the given bounding box to crop an image.
        """
        img = Image.open(BytesIO(png)).convert("RGB")
        return img.crop(bbox)

    def _scrape_slides(self, n_slides, next_btn, slide_selector, source, skip_border_removal = False):
        '''
        Takes a screenshot of all slides and returns a list of pngs

        n_slides: int, the number of slides
        next_btn: clickable element on website to go to the next slide
        slide_selector: arguments to driver.find_element to locate the slide e.g. (By.XPATH, xpath_string)
        source: str, the source platform ('pitch.com', 'figma', etc.)
        skip_border_removal: bool, whether to skip removing black borders around slides
        '''

        png_slides = []
        print('\nScraping slides...')
        for n in tqdm(range(n_slides)):

            # Pitch.com special case: Animations takes multiple clicks
            if source == 'pitch.com':
                while not sources.pitch_at_slide_end(self.driver):
                    self.driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(2)
            
            # Figma special case: Videos takes multiple clicks
            if source == 'figma':
                while not sources.figma_get_slide_number(self.driver) == n + 1:
                    self.driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(1.5)

            slide = self.driver.find_element(*slide_selector)
            png = slide.screenshot_as_png
            png_slides.append(png)

            if n < n_slides - 1:
                # Use JS in case it's hidden
                self.driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(1.5)

        print('Slides scraped!')

        if not skip_border_removal:
            # Find the minimum cropping needed across all slides
            bboxes = [self._crop_black_borders(png) for png in png_slides]
            # Find the largest bbox that fits all slides (min left/top, max right/bottom)
            min_left = min(b[0] for b in bboxes)  # Take min of left edges
            min_top = min(b[1] for b in bboxes)   # Take min of top edges
            max_right = max(b[2] for b in bboxes) # Take max of right edges
            max_bottom = max(b[3] for b in bboxes) # Take max of bottom edges
            consistent_bbox = (min_left, min_top, max_right, max_bottom)
            
            # Apply consistent cropping to all slides
            print('\nApplying consistent cropping...')
            cropped_slides = []
            for png in tqdm(png_slides):
                cropped_img = self._apply_consistent_cropping(png, consistent_bbox)
                buffer = BytesIO()
                cropped_img.save(buffer, format="PNG")
                cropped_slides.append(buffer.getvalue())
            return cropped_slides
        else:
            return png_slides
    
    def _detect_source(self):
        '''
        Detects the source platform by checking for platform-specific indicators in the page content.
        Returns a tuple of (source, params).
        '''
        # Check if it's a pitch.com presentation by looking for pitch.com script tags
        try:
            pitch_scripts = self.driver.find_elements("css selector", "script[src*='pitch.com/static']")
            if pitch_scripts:
                return 'pitch.com', sources.get_pitch_params(self.driver)
        except:
            pass
        
        # Check if it's a pitch.com presentation by URL
        if 'pitch.com' in self.driver.current_url.lower():
            return 'pitch.com', sources.get_pitch_params(self.driver)
        
        # Check other platforms by URL
        if 'canva.com' in self.driver.current_url.lower():
            return 'canva', sources.get_canva_params(self.driver)
        elif 'docs.google.com/presentation/' in self.driver.current_url.lower():
            return 'gslides', sources.get_gslides_params(self.driver)
        elif 'figma.com/deck' in self.driver.current_url.lower():
            return 'figma', sources.get_figma_params(self.driver)
        
        raise Exception('URL not supported...')

    def download(self, url, skip_border_removal):
        '''
        Given an URL, loops over slides to screenshot them and saves a PDF
        '''

        self.driver.get(url)
        time.sleep(10)
        
        # Detect the source platform
        source, params = self._detect_source()
        
        png_slides = self._scrape_slides(
            params['n_slides'], params['next_btn'], params['slide_selector'], 
            skip_border_removal = skip_border_removal, 
            source = source
        )

        # Helper: Loading from memory and converting RGBA to RGB
        def _rgba_to_rgb(png):
            img = Image.open(BytesIO(png))
            img.load()
            background = Image.new('RGB', img.size, (255, 255, 255))

            if img.mode == 'RGBA':
                background.paste(img, mask = img.split()[3])
            else:
                background.paste(img)
            return background

        # Saving the screenshots as a PDF using Pillow
        print('\nConverting RGBA to RGB...')
        images = [_rgba_to_rgb(png) for png in tqdm(png_slides)]
        print('Conversion finished!')

        title = ''.join([char for char in self.driver.title if char.isalpha()])

        output_path = 'decks/' + title + '.pdf'

        print('\nSaving deck as "' + output_path + '"...')
        images[0].save(
            output_path, "PDF", resolution = 100.0, save_all = True, append_images = images[1:]
        )
        print('Deck saved!')

        self.driver.close()

        return output_path









    
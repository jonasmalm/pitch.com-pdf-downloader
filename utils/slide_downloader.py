from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from PIL import Image
from io import BytesIO

from tqdm import tqdm
import time

from utils import sources


class SlideDownloader:

    def __init__(self, resolution):

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
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
    

    def _scrape_slides(self, n_slides, next_btn, slide_selector, pitch_dot_com = False):
        '''
        Takes a screenshot of all slides and returns a list of pngs

        n_slides: int, the number of slides
        next_btn: clickable element on website to go to the next slide
        slide_selector: arguments to driver.find_element to locate the slide e.g. (By.XPATH, xpath_string)
        '''

        png_slides = []
        print('\nScraping slides...')
        for n in tqdm(range(n_slides)):

            # Animations in pitch.com ...
            if pitch_dot_com:
                while not sources.pitch_at_slide_end(self.driver):
                    self.driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(1.5)

            slide = self.driver.find_element(*slide_selector)
            png_slides.append(slide.screenshot_as_png)

            if n < n_slides - 1:
                # Use JS in case it's hidden
                self.driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(1.5)

        print('Slides scraped!')
        return png_slides
    
    def download(self, url):
        '''
        Given an URL, loops over slides to screenshot them and saves a PDF
        '''

        self.driver.get(url)
        time.sleep(10)
        
        pitch = False
        if 'pitch.com' in url.lower():
            params = sources.get_pitch_params(self.driver)
            pitch = True
        elif 'canva.com' in url.lower():
            params = sources.get_canva_params(self.driver)
        elif 'docs.google.com/presentation/' in url.lower():
            params = sources.get_gslides_params(self.driver)
        else:
            raise Exception('URL not supported...')
        
        png_slides = self._scrape_slides(params['n_slides'], params['next_btn'], params['slide_selector'], pitch_dot_com = pitch)

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









    
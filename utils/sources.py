from selenium.webdriver.common.by import By
import time

def get_canva_params(driver):
    '''
    Preprocesses Canva and returns params to find all slides
    '''

    # Accept cookies
    buttons = driver.find_elements(By.TAG_NAME, 'button')
    for b in buttons:
        if 'Accept' in b.text:
            b.click()
            time.sleep(1)
            break

    n_slides = driver.find_elements(By.XPATH, '//*[@aria-valuemax]')[0].get_property('ariaValueMax')
    n_slides = int(n_slides)

    # Hiding the footer & header (otherwise visible in slide)
    footer = driver.find_elements(By.TAG_NAME, 'footer')[0]
    header = driver.find_elements(By.TAG_NAME, 'header')[0]
    driver.execute_script("arguments[0].style.opacity = 0;", footer)
    driver.execute_script("arguments[0].style.opacity = 0;", header)

    next_btn = driver.find_element(By.XPATH, '//button[@aria-label="Next page"]')
    if next_btn.text != '':
        raise Exception('Could not find the next button...')
    
    params = dict(
        n_slides = n_slides,
        next_btn = next_btn,
        slide_selector = (By.XPATH, '//*[contains(@style, "translate")]')
    )

    return params


def get_pitch_params(driver):
    '''
    Preprocesses Pitch.com and returns params to find all slides
    '''

    # Cookie accept - do not accept tracking
    btn = driver.find_elements(By.XPATH, '//button[@type="text"]')
    if len(btn) > 0:
        btn = btn[0]
        btn.click()
        time.sleep(1)
        no_tracking = driver.find_elements(By.XPATH, '//input[@name="engagement"]')[0]
        no_tracking.click()
        time.sleep(1)
        confirm = driver.find_elements(By.XPATH, '//button[@type="submit"]')[0]
        confirm.click()
        time.sleep(1)
    
    # Deleting the popup shown at the end of the presentation
    try:
        driver.execute_script("document.getElementsByClassName('player-branding-popover')[0].remove();")
    except Exception:
        print('Could not remove branding popover...')

    n_slides = len(driver.find_elements(By.CLASS_NAME, 'dash'))

    # Named differently at times?
    btns = driver.find_elements(By.CLASS_NAME, 'ng-player-v2--button')
    if len(btns) == 0:
        btns = driver.find_elements(By.CLASS_NAME, 'player-v2--button')
    next_btn = btns[1]

    params = dict(
        n_slides = n_slides,
        next_btn = next_btn,
        slide_selector = (By.CLASS_NAME, 'slide-wrapper')
    )

    return params

# Check if we're at the end of the current slide (gradually adding elements)
def pitch_at_slide_end(driver):

    current_dash = driver.find_element(By.CSS_SELECTOR, '.dash.selected [aria-valuenow]')

    aria_valuenow = current_dash.get_attribute('aria-valuenow')

    return aria_valuenow == '100'



def get_gslides_params(driver):

    '''
    Preprocesses Google Slides and returns params to find all slides
    '''

    slide_parent = driver.find_element(By.CLASS_NAME, 'sketchyViewerContent')

    n_slides_button = driver.find_elements(By.CSS_SELECTOR, "[aria-setsize]")[0]
    n_slides = n_slides_button.get_attribute('aria-setsize')
    
    return dict(
        n_slides = int(n_slides),
        next_btn = slide_parent,
        slide_selector = (By.CLASS_NAME, 'punch-viewer-svgpage-svgcontainer')
    )

def get_figma_params(driver):

    '''
    Preprocesses Figma presentation and returns params to find all slides
    '''

    # Removing the header so it doesn't show up on slides
    header = driver.find_elements(By.CSS_SELECTOR, '[aria-label="Prototype controls"]')
    if header:
        driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
        """, header[0])

    next_btn = driver.find_elements(By.CSS_SELECTOR, '[aria-label="Next frame"]')[0]

    slide_no = driver.find_elements(By.CSS_SELECTOR, '[class*="toolbelt_label"]')[0]
    slide_no_text = slide_no.get_attribute('innerText')
    n_slides = slide_no_text.split('/')[1].strip()


    return dict(
        n_slides = int(n_slides),
        next_btn = next_btn,
        slide_selector = (By.TAG_NAME, 'canvas') 

    )

def get_papermark_params(driver):
    '''
    Preprocesses Papermark and returns params to find all slides
    '''
    spans = driver.find_elements(By.CSS_SELECTOR, 'div.bg-gray-900.text-white span')
    n_slides = int(spans[-1].text) - 1
    next_btn = driver.find_element(By.CSS_SELECTOR, 'div.group.absolute.right-0 button')

    # Hide nav buttons, slide counter, and watermark so they don't appear in screenshots
    driver.execute_script("""
        // Left nav button
        var left = document.querySelector('div.group.absolute.left-0');
        if (left) left.style.visibility = 'hidden';
        // Right nav button
        var right = document.querySelector('div.group.absolute.right-0');
        if (right) right.style.visibility = 'hidden';
        // Slide counter
        var counter = document.querySelector('div.bg-gray-900.text-white');
        if (counter) counter.style.visibility = 'hidden';
        // Papermark watermark
        var watermark = document.querySelector('a[href*="utm_campaign=poweredby"]');
        if (watermark) watermark.closest('div.absolute.bottom-0.right-0').style.visibility = 'hidden';
    """)

    # Target the visible slide img (parent div has 'flex' class; hidden slides have 'hidden' class)
    slide_selector = (By.XPATH, '//div[contains(@class,"viewer-container") and not(contains(@class,"hidden"))]//img')
    return dict(
        n_slides=n_slides,
        next_btn=next_btn,
        slide_selector=slide_selector,
    )


def papermark_get_slide_number(driver):
    spans = driver.find_elements(By.CSS_SELECTOR, 'div.bg-gray-900.text-white span')
    return int(spans[0].text)


def figma_get_slide_number(driver):

    '''
    Check if we're at the expected slide (Clicking next on a slide with video starts video and doesn't move to next slide)
    '''

    slide_no = driver.find_elements(By.CSS_SELECTOR, '[class*="toolbelt_label"]')[0]
    slide_no_text = slide_no.get_attribute('innerText')
    current_slide = slide_no_text.split('/')[0].strip()

    current_slide = int(current_slide)

    return current_slide

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
        print('Found wrong next button...')
        print(next_btn.text)
        raise Exception('Wrong next button!')
    
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

    content = driver.find_element(By.CLASS_NAME, 'punch-viewer-container')

    n_slides_button = driver.find_elements(By.CSS_SELECTOR, "[aria-setsize]")[0]
    n_slides = n_slides_button.get_attribute('aria-setsize')
    
    return dict(
        n_slides = int(n_slides),
        next_btn = content,
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
    print('Slide selector contents: ', slide_no_text)
    n_slides = slide_no_text.split('/')[1].strip()


    return dict(
        n_slides = int(n_slides),
        next_btn = next_btn,
        slide_selector = (By.TAG_NAME, 'canvas') 

    )

def figma_get_slide_number(driver):

    '''
    Check if we're at the expected slide (Clicking next on a slide with video starts video and doesn't move to next slide)
    '''

    slide_no = driver.find_elements(By.CSS_SELECTOR, '[class*="toolbelt_label"]')[0]
    slide_no_text = slide_no.get_attribute('innerText')
    current_slide = slide_no_text.split('/')[0].strip()

    current_slide = int(current_slide)

    return current_slide

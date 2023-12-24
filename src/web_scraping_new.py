from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import re
import time
"""
import speech_recognition as sr
import pyttsx3 
e = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()
speak("Which medicine do you want?")

    def sentence_recog():
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Listening...")
            r.pause_threshold = 1
            try:
                audio = r.listen(source, timeout=10)
                input_sentence = r.recognize_google(audio, language="en-in")
                print(f'You said: "{input_sentence}"')
                return input_sentence
            except sr.UnknownValueError:
                print("Sorry, I did not hear your request. Please try again.")
                return ""
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
"""

class WebScraping:
    apollo_products = {}
    pharmeasy_products = {}
    tata1mg_products = {}

    def __init__(self,medicine_names) -> None:
        self.meds_names = medicine_names        
        self.driver = self.get_webdriver()

    def scrape(self):
        time1 = time.time()
        self.parse_apollo_products()
        time2 = time.time()
        print(f"Apollo: {time2-time1}")
        time1 = time.time()
        self.parse_pharmeasy_products()
        time2 = time.time()
        print(f"Pharmeasy: {time2-time1}")
        time1 = time.time()
        self.parse_tata1mg_products()
        time2 = time.time()
        print(f"1mg: {time2-time1}")
        self.driver.quit()


    def get_webdriver(options=None):
        browsers = [
            (webdriver.Edge, EdgeOptions),
            (webdriver.Chrome, ChromeOptions),
            (webdriver.Firefox, FirefoxOptions),
            (webdriver.Safari, None),  # Safari does not require additional options
            (webdriver.Ie, None),  # Internet Explorer does not require additional options
        ]

        for browser, options_class in browsers:
            try:
                options = options_class()
                options.add_argument("--headless")

                if browser == webdriver.Chrome:
                    options.use_chromium = True
                driver = browser(options=options)
                return driver
            except WebDriverException:
                continue
        raise WebDriverException("No suitable web browser found")

    def parse_tata1mg_products(self):
        self.driver=self.get_webdriver()
        url = "https://www.1mg.com/search/all?name="
        for i in self.meds_names:
            url = url + i + "%20"
        
        self.driver.get(url)

        wait = WebDriverWait(self.driver, 10)
        price_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='style__price-tag___']")))

        product_name_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='style__product-description___']")))

        product_description = []
        for product_name_element in product_name_elements:
            try:
                text = (product_name_element.text.splitlines()[1]).replace('\n',' ')
                product_description.append(text)
            except IndexError:
                product_description.append("No description available")

        product_links=[]
        try:
            product_boxes =WebDriverWait(self.driver,5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='col-xs-12 style__container___cTDz0']")))
            for product_box in product_boxes:
                product_link_element = product_box.find_element(By.CSS_SELECTOR, "a")
                product_link = product_link_element.get_attribute("href") if product_link_element else ""
                product_links.append(product_link)
        except:
            for product_name_element in product_name_elements:
                product_links.append(f"https://www.1mg.com/search/all?name={i}")

        for price_element, product_name_element, description,product_link in zip(price_elements, product_name_elements, product_description,product_links):
            split = product_name_element.text.splitlines()
            product_name = split[0]

            self.tata1mg_products[product_name.strip()] = {
           "price": price_element.text.strip("MRP₹").strip("₹"),
                "link": product_link,
            }

    def parse_apollo_products(self):
        self.driver = self.get_webdriver()
        for i in self.meds_names:   
            url = f"https://www.apollopharmacy.in/search-medicines/{i}"

            self.driver.get(url)

            wait = WebDriverWait(self.driver, 5)
            price_elements = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div[class*='ProductCard_priceGroup__4D4k0']")
                )
            )

            product_name_elements = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "p[class*='ProductCard_productName__vXoqs']")
                )
            )
            product_boxes= WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div[class*='ProductCard_pdHeader__ANDKh']")
                )
            )

            product_links = []
            for product_box in product_boxes:
                product_link_element = product_box.find_element(
                    By.CSS_SELECTOR, "a[class*='ProductCard_proDesMain__4D8VV']"
                )
                product_link = (
                    product_link_element.get_attribute("href") if product_link_element else ""
                )
                product_links.append(product_link)

            product_description = []
            for product_name_element in product_name_elements:
                try:
                    text = (product_name_element.text.splitlines()[0]).replace("\n", " ")
                    product_description.append(text)
                except IndexError:
                    product_description.append("No description available")

            for price_element, product_name_element, description, product_link in zip(
                price_elements, product_name_elements, product_description, product_links
            ):
                split = product_name_element.text.splitlines()
                product_name = split[0]

                self.apollo_products[product_name.strip()] = {
                    "description": description,
                    "price": re.search("₹([\d.]+)", price_element.text).group(1),
                    "link": product_link,
                }

    def parse_pharmeasy_products(self):
        self.driver= self.get_webdriver()
    
        url = "https://pharmeasy.in/search/all?name="
        for i in self.meds_names:
            url = url + i + "%20"   
        
        self.driver.get(url)

        wait = WebDriverWait(self.driver, 5)
        price_elements = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div[class*='ProductCard_ourPrice__yDytt']")
            )
        )

        product_name_elements = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "h1[class*='ProductCard_medicineName__8Ydfq']")
            )
        )

        product_boxes = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div[class*='ProductCard_medicineUnitContainer__cBkHl']")
            )
        )

        product_links = []
        for product_box in product_boxes:
            try:
                product_link_element = product_box.find_element(By.CSS_SELECTOR, "a")
                product_link = (
                    product_link_element.get_attribute("href")
                    if product_link_element
                    else ""
                )
                product_links.append(product_link)
            except:
                product_links.append(
                    f"https://pharmeasy.in/search/all?name={i}"
                )

        product_description = []
        for product_name_element in product_name_elements:
            try:
                text = (product_name_element.text.splitlines()[0]).replace("\n", " ")
                product_description.append(text)
            except IndexError:
                product_description.append("No description available")

        for price_element, product_name_element, description, product_link in zip(
            price_elements, product_name_elements, product_description, product_links
        ):
            split = product_name_element.text.splitlines()
            product_name = split[0]

            self.pharmeasy_products[product_name.strip()] = {
                "description": description,
                "price": price_element.text.strip("MRP₹").strip("₹").strip("*"),
                "link": product_link,
            }
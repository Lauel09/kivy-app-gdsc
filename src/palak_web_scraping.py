from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as WebWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import re
import time

# Global variables
term_to_search = input("Name of the medicine to search:-")
tata1mg_products = {}
apollo_products = {}
pharmeasy_products = {}
apollo_time = 0
pharmeasy_time = 0
tata1mg_time = 0
driver = None

def init_webdriver(options=None):
    global driver
    browsers = [
        (webdriver.Firefox, FirefoxOptions),
        (webdriver.Chrome, ChromeOptions),
        (webdriver.Edge, EdgeOptions),
        (webdriver.Safari, None),  # Safari does not require additional options
        (webdriver.Ie, None),  # Internet Explorer does not require additional options
    ]

    # Try to find a suitable browser
    # If none is found, raise an exception
    for browser, options_class in browsers:
        try:
            options = options_class()
            options.add_argument("--headless")

            if browser == webdriver.Chrome:
                options.use_chromium = True

            driver = browser(options=options)
            # Exit if the browser is found
            return
        # If the browser is not installed, continue to the next one
        except WebDriverException:
            continue
    raise WebDriverException("No suitable web browser found")

def parse_tata1mg_products():
    url = f"https://www.1mg.com/search/all?name={term_to_search}"
    driver.get(url)
    wait = WebWait(driver, 20)  # Increase the timeout to 20 seconds
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
        product_boxes =WebWait(driver,5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='col-xs-12 style__container___cTDz0']")))
        for product_box in product_boxes:
            product_link_element = product_box.find_element(By.CSS_SELECTOR, "a")
            product_link = product_link_element.get_attribute("href") if product_link_element else ""
            product_links.append(product_link)
    except:
        for product_name_element in product_name_elements:
            product_links.append(f"https://www.1mself.g.com/search/all?name={term_to_search}")
    for price_element, product_name_element, description,product_link in zip(price_elements, product_name_elements, product_description,product_links):
        split = product_name_element.text.splitlines()
        product_name = split[0]
        tata1mg_products[product_name.strip()] = {
            "description": description,
            "price": price_element.text.strip("MRP₹").strip("₹"),
            "link": product_link,
        }
def parse_apollo_products():
    url = f"https://www.apollopharmacy.in/search-self.medicines/{term_to_search}"
    driver.get(url)
    wait = WebWait(driver, 20)  # Increase the timeout to 20 seconds
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
    product_boxes = WebWait(driver, 20).until(
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
    apollo_product = {}
    for price_element, product_name_element, description, product_link in zip(
        price_elements, product_name_elements, product_description, product_links
    ):
        split = product_name_element.text.splitlines()
        product_name = split[0]
        apollo_product[product_name.strip()] = {
            "description": description,
            "price": re.search("₹([\d.]+)", price_element.text).group(1),
            "link": product_link,
        }
def parse_pharmeasy_products():
    url = f"https://pharmeasy.in/search/all?name=self.{term_to_search}"
    driver.get(url)
    wait = WebWait(driver, 20)  # Increase the timeout to 20 seconds
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
    product_boxes = WebWait(driver, 20).until(
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
                f"https://pharmeasy.in/search/allself.?name={term_to_search}"
            )
    product_description = []
    for product_name_element in product_name_elements:
        try:
            text = (product_name_element.text.splitlines()[0]).replace("\n", " ")
            product_description.append(text)
        except IndexError:
            product_description.append("No description available")
    pharmeasy_product = {}
    for price_element, product_name_element, description, product_link in zip(
        price_elements, product_name_elements, product_description, product_links
    ):
        split = product_name_element.text.splitlines()
        product_name = split[0]
        pharmeasy_product[product_name.strip()] = {
            "description": description,
            "price": price_element.text.strip("MRP₹").strip("₹").strip("*"),
            "link": product_link,
        }

if __name__ == "__main__":
    init_webdriver()
    start_tata1mg = time.time()
    parse_tata1mg_products(term_to_search)
    end_tata1mg = time.time()
    tata1mg_time = end_tata1mg - start_tata1mg
    start_apollo = time.time()
    parse_apollo_products(term_to_search)
    end_apollo = time.time()
    apollo_time = end_apollo - start_apollo
    start_pharmeasy = time.time()
    parse_pharmeasy_products(term_to_search)
    end_pharmeasy = time.time()
    pharmeasy_time = end_pharmeasy - start_pharmeasy
    print(tata1mg_products)
    print(apollo_products)
    print(pharmeasy_products)
    print("Time taken by tata1mg is:-",tata1mg_time)
    print("Time taken by apollo is:-",apollo_time)
    print("Time taken by pharmeasy is:-",pharmeasy_time)
    driver.quit()

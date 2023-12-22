from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as WebWait
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import re
from selenium.webdriver import Firefox, Chrome, Edge, Safari, Ie

class WebScraping():
    med_name = ""
    apollo_product = {}
    pharmeasy_product = {}
    tata1mg_products = {}
    driver = None

    def __init__(self, med_name) -> None:
        self.med_name = med_name
        

    def init_webdriver(self,options=None):
        browsers = [
            (Firefox, FirefoxOptions),
            (Chrome, ChromeOptions),
            (Edge, EdgeOptions),
            (Safari, None),  # Safari does not require additional options
            (Ie, None),  # Internet Explorer does not require additional options
        ]

        # Try to find a suitable browser
        # If none is found, raise an exception
        for browser, options_class in browsers:
            try:
                options = options_class()
                options.add_argument("--headless")
                if browser == Chrome:
                    options.use_chromium = True

                self.driver = browser(options=options)
                # Exit if the browser is found
                return
            # If the browser is not installed, continue to the next one
            except WebDriverException:
                continue
        raise WebDriverException("No suitable web browser found")


    def parse_tata1mg_products(self):
        url = f"https://www.1mg.com/search/all?name={self.med_name}"
        self.driver.get(url)
        wait = WebWait(self.driver, 20)  # Increase the timeout to 20 seconds
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
            product_boxes =WebWait(self.driver,5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='col-xs-12 style__container___cTDz0']")))
            for product_box in product_boxes:
                product_link_element = product_box.find_element(By.CSS_SELECTOR, "a")
                product_link = product_link_element.get_attribute("href") if product_link_element else ""
                product_links.append(product_link)
        except:
            for product_name_element in product_name_elements:
                product_links.append(f"https://www.1mself.g.com/search/all?name={self.med_name}")
        for price_element, product_name_element, description,product_link in zip(price_elements, product_name_elements, product_description,product_links):
            split = product_name_element.text.splitlines()
            product_name = split[0]
            self.tata1mg_products[product_name.strip()] = {
                "description": description,
                "price": price_element.text.strip("MRP₹").strip("₹"),
                "link": product_link,
            }


    def parse_apollo_products(self):
        url = f"https://www.apollopharmacy.in/search-self.medicines/{self.med_name}"

        self.driver.get(url)

        wait = WebWait(self.driver, 20)  # Increase the timeout to 20 seconds
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

        product_boxes = WebWait(self.driver, 20).until(
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

        self.apollo_product = {}
        for price_element, product_name_element, description, product_link in zip(
            price_elements, product_name_elements, product_description, product_links
        ):
            split = product_name_element.text.splitlines()
            product_name = split[0]

            self.apollo_product[product_name.strip()] = {
                "description": description,
                "price": re.search("₹([\d.]+)", price_element.text).group(1),
                "link": product_link,
            }


    def parse_pharmeasy_products(self):
        url = f"https://pharmeasy.in/search/all?name=self.{self.med_name}"

        self.driver.get(url)

        wait = WebWait(self.driver, 20)  # Increase the timeout to 20 seconds
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
        product_boxes = WebWait(self.driver, 20).until(
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
                    f"https://pharmeasy.in/search/allself.?name={self.med_name}"
                )

        product_description = []
        for product_name_element in product_name_elements:
            try:
                text = (product_name_element.text.splitlines()[0]).replace("\n", " ")
                product_description.append(text)
            except IndexError:
                product_description.append("No description available")

        self.pharmeasy_product = {}
        for price_element, product_name_element, description, product_link in zip(
            price_elements, product_name_elements, product_description, product_links
        ):
            split = product_name_element.text.splitlines()
            product_name = split[0]

            self.pharmeasy_product[product_name.strip()] = {
                "description": description,
                "price": price_element.text.strip("MRP₹").strip("₹").strip("*"),
                "link": product_link,
            }

if __name__ == "__main__":
    web_scraping = WebScraping("paracetamol")
    web_scraping.init_webdriver()
    web_scraping.parse_tata1mg_products()
    web_scraping.parse_pharmeasy_products()
    web_scraping.parse_apollo_products()
    print(web_scraping.tata1mg_products)
    print(web_scraping.pharmeasy_product)
    print(web_scraping.apollo_product)
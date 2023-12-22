#!/home/sol/Documents/django_hackathon/.venv/bin/python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import EdgeOptions


options = EdgeOptions()
pref = {
    "profile.managed_default_content_settings.images": 2,
    "javascript.enabled": False
}
options.use_chromium = True
options.add_argument("headless")
options.add_experimental_option("prefs",pref)

driver = webdriver.Edge(options=options)
driver.set_script_timeout(10)
#driver.set_window_position(0,0)
term_to_search = input("Name of the medecine to search:-")
tata1mg_products = {}
apollo_products = {}


def parse_tata1mg_products():
    url = f"https://www.1mg.com/search/all?name={term_to_search}"

    driver.get(url)

    # Wait until the price and product name elements are loaded
    wait = WebDriverWait(driver, 5)
    price_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='style__price-tag___']")))

    # So a point to be noted is that this code works with style-product-description and not style__pro-title___
    product_name_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='style__product-description___']")))


    # This never works with the HTML extraction
    # product_name_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='style__pro-title___']")))

    # Print the price and product name of each product
    product_description = []
    for i in product_name_elements:
        text = (i.text.splitlines()[1]).replace('\n',' ')
        product_description.append(text)

    counter = 0
    for price_element, product_name_element in zip(price_elements, product_name_elements):
        split = product_name_element.text.splitlines()
        product_name = split[0]
        
        tata1mg_products[product_name.strip()] = [product_description[counter],price_element.text.strip("MRP₹").strip("₹")]
        counter += 1

# Here we will parse the apollo products
def parse_apollo_products():
    pass


if __name__ == "__main__":
    parse_apollo_products()
    parse_tata1mg_products()
    print(tata1mg_products,apollo_products)

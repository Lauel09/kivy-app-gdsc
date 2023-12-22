from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait


# This checks whether these browsers are installed on your system or not
# If not, then it raises an error
# If yes, then it returns the driver object
def get_webdriver(options):
    browsers = ["Chrome", "Firefox", "Edge"]
    for browser in browsers:
        try:
            driver = getattr(webdriver, browser)(options=options)
            return driver
        except WebDriverException:
            raise WebDriverException("No supported browser found")
    
    

def save_html_content(url, filename):
    try:
        options = webdriver.EdgeOptions()
        # Required if we want to pass the headless argument to the web driver
        options.use_chromium = True
        options.add_argument("headless")
        driver = driver.get(url)

        # Sleep to allow time for dynamic content to load (adjust as needed)
        time.sleep(5)
        wait = WebDriverWait(driver,10)

        with open(filename, "w", encoding="utf-8") as file:
            print("Saving HTML content to file...")
            file.write(driver.page_source)

        driver.quit()  # Close the browser
        print(f"HTML content saved to {filename}")

    except Exception as e:
        print(f"An error occurred: {e}")


def extract_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    product_boxes = soup.find_all("div", class_="col-xs-12 style__container___cTDz0")

    if product_boxes:
        product_links = []
        product_sizes = []
        product_names = []
        product_prices = []
        product_reviews = []

        for product_box in product_boxes:
            product_size_div = product_box.find(
                "div", class_="style__pack-size___254Cd"
            )
            product_size = product_size_div.text.strip() if product_size_div else ""

            product_name_div = product_box.find(
                "span", class_="style__pro-title___3zxNC"
            )
            product_name = product_name_div.text.strip() if product_name_div else ""

            product_price_div = product_box.find(
                "div", class_="style__price-tag___B2csA"
            )
            product_price = product_price_div.text.strip() if product_price_div else ""

            product_review_span = product_box.find(
                "span", class_="CardRatingDetail__weight-700___27w9q"
            )
            product_review = (
                product_review_span.text.strip() if product_review_span else ""
            )

            short_product_link = (
                product_box.find("a")["href"] if product_box.find("a") else ""
            )
            product_link=f"https://www.1mg.com{short_product_link}"

            product_links.append(product_link)
            product_sizes.append(product_size)
            product_names.append(product_name)
            product_prices.append(product_price)
            product_reviews.append(product_review)

    else:
        product_boxes = soup.find_all("div", class_="col-md-3 col-sm-4 col-xs-6 style__container___jkjS2")

        product_links = []
        product_sizes = []
        product_names = []
        product_prices = []
        product_reviews = []

        for product_box in product_boxes:
            product_size_div = product_box.find(
                "div", class_="style__pack-size___3jScl"
            )
            product_size = product_size_div.text.strip() if product_size_div else ""

            product_name_div = product_box.find(
                "div", class_="style__pro-title___3G3rr"
            )
            product_name = product_name_div.text.strip() if product_name_div else ""

            product_price_div = product_box.find(
                "div", class_="style__price-tag___KzOkY"
            )
            product_price = product_price_div.text.strip() if product_price_div else ""

            product_review_span = product_box.find(
                "span", class_="CardRatingDetail__weight-700___27w9q"
            )
            product_review = (
                product_review_span.text.strip() if product_review_span else ""
            )

            product_link = (
                product_box.find("a")["href"] if product_box.find("a") else ""
            )

            product_links.append(product_link)
            product_sizes.append(product_size)
            product_names.append(product_name)
            product_prices.append(product_price)
            product_reviews.append(product_review)

    data = {
        "Product_link": product_links,
        "Product_size": product_sizes,
        "Product_name": product_names,
        "Product_price": product_prices,
        "Product_review": product_reviews,
    }
    df = pd.DataFrame(data)
    return df


def main():
    med = input("Enter the name of the medicine: ")
    url = f"https://www.1mg.com/search/all?name={med}"
    file = f"{med}.html"

    save_html_content(url, filename=file)

    with open(file, "r", encoding="utf-8") as file:
        html_content = file.read()

    df = extract_data(html_content)
    print(df)

    #Write to Excel file
    df.to_excel(f"output_{med}.xlsx", index=False)
    print(f"Data has been successfully extracted and added to output_{med}.")


if __name__ == "__main__":
    main()

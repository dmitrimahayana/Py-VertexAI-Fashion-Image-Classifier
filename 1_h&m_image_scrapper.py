import os
import time
import urllib.request
import pandas as pd
from playwright.sync_api import sync_playwright, expect
from playwright_stealth import stealth_sync


def define_browser(headless):
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=headless, slow_mo=50)
    page = browser.new_page()
    stealth_sync(page)
    return page, browser

def scrape_data(page, data_dict, row):
    # Select all a tags within the specified structure
    li_elements = page.query_selector_all("li > div.product-item-info")
    counter = 0

    for li in li_elements:
        counter = counter + 1

        # Extract the title
        title = li.query_selector("div > strong > a.product-item-link > span")
        title_img = title.text_content().strip() if title else "No title"

        # Extract the image attribute from the img tag
        img_tag = li.query_selector("div > a > span.product-image-container > span.product-image-wrapper > img")
        image_url = img_tag.get_attribute("data-product-image") if img_tag else "No img_tag"

        # Save Image URL
        image_name = str(counter) + " " + title_img
        folder_path = f"Output/Image/{row['Type']}/"
        is_exist = os.path.exists(folder_path)
        if not is_exist:
            os.makedirs(folder_path)
            print(f"The new directory {folder_path} is created!")
        urllib.request.urlretrieve(image_url, f"{folder_path}{image_name}.png")

        # Extract the price
        price = li.query_selector("div > div > span.old-price")
        price_img = price.text_content().strip() if price else "No price"
        if "Rp" in price_img:
            price_split = price_img.split("Rp")
            price_img = "Rp " + price_split[1]

        # Append to dictionary
        data_dict["Gender"].append(row['Gender'])
        data_dict["ItemType"].append(row['Type'])
        data_dict["ImageName"].append(image_name)
        data_dict["ImageURL"].append(image_url)
        data_dict["ItemTitle"].append(title_img)
        data_dict["Price"].append(price_img)
        print(f"{counter} {row['Gender']} {row['Type']} {title_img} {price_img} {image_url}")
    return data_dict


def iterate_url(df_input, page, output_file):
    # Filter Status is yes
    df_input = df_input[df_input["Status"] == "Yes"]

    # Define dictionary
    data_dict = {
        "Gender": [],
        "ItemType": [],
        "ItemTitle": [],
        "Price": [],
        "ImageName": [],
        "ImageURL": [],
    }

    # Navigate to url
    for index, row in df_input.iterrows():
        url_home = row["URL"]
        page.goto(url_home, timeout=60_000)
        time.sleep(5)

        data_dict = scrape_data(page, data_dict, row)

    # Create dataframe
    df = pd.DataFrame(data_dict)
    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    # Define variable
    headless = False
    input_file = "./Input/Input.xlsx"
    input_sheetname = "h&m"
    output_file = "./Output/h&m.csv"

    # Read Input
    df = pd.read_excel(open(input_file, 'rb'), sheet_name=input_sheetname)

    # Start automation
    page, browser = define_browser(headless)
    iterate_url(df, page, output_file)
    # End automation

    page.close()
    browser.close()

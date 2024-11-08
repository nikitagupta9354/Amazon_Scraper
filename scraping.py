from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pymongo

# Initialize MongoDB client and database
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["amazon_db"]
products_collection = db["products"]

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration

# Initialize the WebDriver with the configured Chrome options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

driver.get("https://www.amazon.in")
all_button = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "hm-icon-label"))
)
all_button.click()
shop_by_category = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, "//div[text()='Shop by Category']"))
)
driver.execute_script("arguments[0].scrollIntoView();", shop_by_category)
see_all_button = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//a[@class='hmenu-item hmenu-compressed-btn']//div[text()='See all']"))
)
see_all_button.click()
time.sleep(3)

# Only 11 to 21 are categories available
for index in range(10, 21):  
    categories = driver.find_elements(By.XPATH, "//ul[contains(@class,'hmenu-visible')]//li/a")
    category = categories[index]
    category_name = category.text.strip()
    if category_name:
        print(f"Category {index + 1}: {category_name}")
        actions = ActionChains(driver)
        actions.move_to_element(category).click().perform()
        print(f"Clicked on Category: {category_name}")
        time.sleep(3)
        
        subcategories = driver.find_elements(By.XPATH, "//ul[contains(@class,'hmenu-visible')]//a[@class='hmenu-item']")
        subcategory_list= []
        for subcategory in subcategories:
            subcategory_name = subcategory.text.strip()
            subcategory_url = subcategory.get_attribute("href")
            if subcategory_url not in subcategory_list:
                subcategory_list.append(subcategory_url)
                print(f"Subcategory: {subcategory_name} - {subcategory_url}")
                
        for url in subcategory_list:
            driver.get(url)
            time.sleep(20) 
            
            product_names= driver.find_elements(By.XPATH, "//span[@class='a-size-base-plus a-color-base a-text-normal']")
            product_prices = driver.find_elements(By.XPATH, "//span[@class='a-price-whole']")
            
            for name, price in zip(product_names, product_prices):
                product_name = name.text.strip()
                product_price = price.text.strip()
                
                if product_name and product_price:
                        # Store product information in MongoDB
                    product_data = {
                            "category": category_name,
                            "product_name": product_name,
                            "product_price": product_price
                        }
                    products_collection.insert_one(product_data)

        # Refresh the page
        driver.refresh()
        print(f"Page refreshed after Category {index + 1}")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 0);")
        
        all_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "hm-icon-label"))
        )
        all_button.click()
        time.sleep(3)
        shop_by_category = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[text()='Shop by Category']"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", shop_by_category)
        see_all_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='hmenu-item hmenu-compressed-btn']//div[text()='See all']"))
        )
        see_all_button.click()
        time.sleep(3)

# Close the browser session
driver.quit()

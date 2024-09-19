import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

# State dictionary with names and their respective link paths
states = {
    "APSRTC": "/online-booking/apsrtc",
    "KERALA RTC": "/online-booking/ksrtc-kerala",
    "TSRTC": "/online-booking/tsrtc",
    "KTCL": "/online-booking/ktcl",
    "RSRTC": "/online-booking/rsrtc",
    "SBSTC": "/online-booking/south-bengal-state-transport-corporation-sbstc",
    "HRTC": "/online-booking/hrtc",
    "ASTC": "/online-booking/astc",
    "UPSRTC": "/online-booking/uttar-pradesh-state-road-transport-corporation-upsrtc",
    "WBTC": "/online-booking/wbtc-ctc"
}

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()

def scroll_to_element(element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)

def handle_popups():
    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]"))
        )
        close_button.click()
    except TimeoutException:
        pass  # No popup to close

def extract_route_data():
    data = []
    wait = WebDriverWait(driver, 15)
    current_page = 1

    while True:
        # Wait until route elements are present
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "route_link")))

        routes = driver.find_elements(By.CLASS_NAME, "route_link")
        for route in routes:
            route_link = route.find_element(By.XPATH, ".//a")
            route_name = route_link.text
            route_url = route_link.get_attribute("href")
            route_data = {
                "Route Name": route_name,
                "Route URL": route_url
            }
            data.append(route_data)

        # Find and click the next page button based on the current page number
        try:
            next_page_number = current_page + 1
            next_button_xpath = f"//div[@class='DC_117_pageTabs ' and text()='{next_page_number}']"
            next_button = driver.find_element(By.XPATH, next_button_xpath)
            if next_button:
                scroll_to_element(next_button)
                next_button.click()
                time.sleep(2)  # Wait for the next page to load
                current_page += 1
            else:
                break
        except Exception as e:
            print(f"No more pages or error occurred on page {current_page}: {e}")
            break

    return data

def extract_bus_details(route_url):
    driver.get(route_url)
    wait = WebDriverWait(driver, 15)

    try:
        # Wait for the "View Buses" button to be clickable
        button_xpath = "//div[@class='button' and contains(text(), 'View Buses')]"
        button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        button.click()

        # Scroll to the bottom of the page
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Collect bus details
        bus_details = []
        bus_items = driver.find_elements(By.CLASS_NAME, "bus-items")
        for bus_item in bus_items:
            bus_data = {
                "Bus Info": bus_item.text
            }
            bus_details.append(bus_data)

        return bus_details

    except Exception as e:
        print(f"An error occurred while extracting bus details: {e}")
        return []

# Main script
all_data = []

try:
    # Navigate to the RTC directory page
    driver.get("https://www.redbus.in/online-booking/rtc-directory")
    wait = WebDriverWait(driver, 15)

    for state, link in states.items():
        try:
            # Click on the state link to go to the state's main page
            state_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[@href='{link}']")))
            scroll_to_element(state_link)  # Scroll to the element before clicking
            state_link.click()

            # Extract route data from all pages
            routes_data = extract_route_data()

            for route in routes_data:
                # Navigate to the route page
                route_url = route["Route URL"]
                bus_details = extract_bus_details(route_url)

                for bus in bus_details:
                    all_data.append({
                        "State": state,
                        "Route Name": route["Route Name"],
                        "Route URL": route["Route URL"],
                        "Bus Details": bus["Bus Info"]
                    })

            # Navigate back to the RTC directory page to select the next state
            driver.get("https://www.redbus.in/online-booking/rtc-directory")
            time.sleep(3)

        except ElementClickInterceptedException as e:
            print(f"Click intercepted on state: {state}. Trying again...")
            handle_popups()  # Attempt to handle any popups
            scroll_to_element(state_link)  # Scroll to the element again
            state_link.click()

finally:
    print("Over")
    driver.quit()

# Convert the collected data to a DataFrame
df = pd.DataFrame(all_data)

# Save to Excel
df.to_excel(r"C:\Users\avr81\Documents\route_links_details.xlsx", index=False)

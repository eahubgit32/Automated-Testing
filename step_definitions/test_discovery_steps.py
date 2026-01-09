import re
import time
from pytest_bdd import scenarios, given, when, then, parsers
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. LINK: Connect this Python file to your Feature file
scenarios('../features/device_discovery.feature')

# Constants
BASE_URL = "http://127.0.0.1:5173"

# --- GIVEN STEPS ---

@given('the user is logged into the AirNav Dashboard')
def login_to_dashboard(browser):
    login_url = f"{BASE_URL}/login"
    browser.get(login_url)
    
    try:
        # 1. Wait for Login Page to Load (Check for username field)
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        
        # 2. Enter Credentials
        # Note: Login page uses IDs 'username' and 'password'
        browser.find_element(By.ID, "username").clear()
        browser.find_element(By.ID, "username").send_keys("admin")
        
        browser.find_element(By.ID, "password").clear()
        browser.find_element(By.ID, "password").send_keys("!frqAIRNAV")

        # 3. Click Login Button
        # We look for a button containing 'Log' or 'Sign' to be safe
        submit_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Log') or contains(text(), 'Sign')]")
        submit_btn.click()

        # 4. Wait for Dashboard Redirect
        WebDriverWait(browser, 10).until(lambda d: "login" not in d.current_url)
        print("Login Successful!")

    except Exception as e:
        print(f"Login Failed: {e}")
        browser.save_screenshot("login_failure.png")
        raise e

@given('the user navigates to the "Device Discovery" page')
def navigate_discovery(browser):
    browser.get(f"{BASE_URL}/add-device")
    time.sleep(2) # Give React a moment to render the form components

@given(parsers.parse('I have a valid SNMPv3 device with IP "{ip}"'))
def valid_device_setup(ip):
    # Just a context step, no action needed
    print(f"Testing with Target IP: {ip}")

# --- WHEN STEPS ---

@when(parsers.parse('I enter the IP address "{ip}"'))
def enter_ip_address(browser, ip):
    # FIXED: Uses the ID 'ipAddress' found in your debug logs
    ip_input = browser.find_element(By.ID, "ipAddress")
    ip_input.clear()
    ip_input.send_keys(ip)

@when(parsers.parse('I enter the SNMP credentials for user "{user}" with auth "{auth}" and priv "{priv}"'))
def enter_credentials(browser, user, auth, priv):
    print(f"[DEBUG] entering creds -> User: {user}, Auth: {auth}, Priv: {priv}")

    # Enter into fields using the IDs we found earlier
    browser.find_element(By.ID, "username").send_keys(user)
    browser.find_element(By.ID, "authPassword").send_keys(auth)
    browser.find_element(By.ID, "privPassword").send_keys(priv)

@when('I click the "Search Device" button')
def click_search(browser):
    try:
        # Robust search for the button (Search or Discover)
        button = browser.find_element(By.XPATH, "//button[contains(text(), 'Search') or contains(text(), 'Discover')]")
        button.click()
    except Exception as e:
        print("Could not find 'Search' button. Saving screenshot.")
        browser.save_screenshot("search_button_fail.png")
        raise e

# --- THEN STEPS ---

@then(parsers.parse('I should see a status message saying "{message}"'))
def verify_message(browser, message):
    time.sleep(3) # Wait for the backend to respond
    
    # Check if the message exists in the page source
    if message in browser.page_source:
        print(f"SUCCESS: Found message '{message}'")
    else:
        # Fail with a screenshot
        browser.save_screenshot("message_fail.png")
        raise AssertionError(f"Expected '{message}' but did not find it on the page.")
import time
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# 1. LINK: Connect this Python file to your Feature file
# Make sure the path matches where your .feature file is located
scenarios('../features/device_discovery.feature')

# Constants
BASE_URL = "http://127.0.0.1:5173"

# ==============================================================================
#                               GIVEN STEPS
# ==============================================================================

@given('the user is logged into the AirNav Dashboard')
def login_to_dashboard(browser):
    """
    Logs the user in as admin.
    """
    login_url = f"{BASE_URL}/login"
    browser.get(login_url)
    
    try:
        # 1. Wait for Login Page
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        
        # 2. Enter Credentials
        browser.find_element(By.ID, "username").clear()
        browser.find_element(By.ID, "username").send_keys("admin")
        
        browser.find_element(By.ID, "password").clear()
        browser.find_element(By.ID, "password").send_keys("!frqAIRNAV")

        # 3. Click Login Button (Looks for 'Login' or 'Sign In')
        submit_btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Log') or contains(text(), 'Sign')]")
        submit_btn.click()

        # 4. Wait for Redirect to Dashboard (URL check)
        WebDriverWait(browser, 15).until(lambda d: "login" not in d.current_url)
        print("SUCCESS: Login Successful!")

    except Exception as e:
        print(f"Login Failed: {e}")
        browser.save_screenshot("login_failure.png")
        raise e

@given('the user navigates to the "Device Discovery" page')
def navigate_discovery(browser):
    """
    Directly navigates to the Add Device / Discovery page.
    """
    browser.get(f"{BASE_URL}/add-device")
    # Give React a moment to render the form components
    time.sleep(2) 

@given(parsers.parse('I have a valid SNMPv3 device with IP "{ip}"'))
def valid_device_setup(ip):
    # Context step - just logging
    print(f"TEST SETUP: Target IP is {ip}")

# ==============================================================================
#                               WHEN STEPS
# ==============================================================================

@when(parsers.parse('I enter the IP address "{ip}"'))
def enter_ip_address(browser, ip):
    try:
        ip_input = browser.find_element(By.ID, "ipAddress")
        ip_input.clear()
        ip_input.send_keys(ip)
    except Exception as e:
        browser.save_screenshot("ip_input_fail.png")
        raise e

@when(parsers.parse('I enter the SNMP credentials for user "{user}" with auth "{auth}" and priv "{priv}"'))
def enter_credentials(browser, user, auth, priv):
    try:
        browser.find_element(By.ID, "username").send_keys(user)
        browser.find_element(By.ID, "authPassword").send_keys(auth)
        browser.find_element(By.ID, "privPassword").send_keys(priv)
    except Exception as e:
        browser.save_screenshot("creds_fail.png")
        raise e

@when('I click the "Search Device" button')
def click_search(browser):
    try:
        # Robust search for the button
        button = browser.find_element(By.XPATH, "//button[contains(text(), 'Search') or contains(text(), 'Discover')]")
        button.click()
    except Exception as e:
        print("Could not find 'Search' button.")
        browser.save_screenshot("search_button_fail.png")
        raise e

# --- DROPDOWN SELECTION LOGIC ---

@when(parsers.parse('I select "{value}" from the Brand dropdown'))
def select_brand(browser, value):
    """Attempts to select a value from the Brand dropdown."""
    print(f"Attempting to select Brand: {value}")
    time.sleep(1) # Wait for UI to stabilize
    try:
        # Try finding a standard HTML <select> near the label "Brand"
        select_elem = browser.find_element(By.XPATH, "//label[contains(text(), 'Brand')]/following::select[1]")
        Select(select_elem).select_by_visible_text(value)
    except:
        # Fallback: Try generic Xpath if exact label fails
        # Assuming it's the FIRST select on the results card
        try:
             selects = browser.find_elements(By.TAG_NAME, "select")
             if len(selects) >= 1:
                 Select(selects[0]).select_by_visible_text(value)
             else:
                 raise Exception("No select elements found")
        except Exception as e:
            browser.save_screenshot("brand_select_fail.png")
            raise e

@when(parsers.parse('I select "{value}" from the Type dropdown'))
def select_type(browser, value):
    print(f"Attempting to select Type: {value}")
    time.sleep(0.5)
    try:
        # Try finding select near label "Type"
        select_elem = browser.find_element(By.XPATH, "//label[contains(text(), 'Type')]/following::select[1]")
        Select(select_elem).select_by_visible_text(value)
    except:
        # Fallback: Assume it's the SECOND select
        try:
             selects = browser.find_elements(By.TAG_NAME, "select")
             if len(selects) >= 2:
                 Select(selects[1]).select_by_visible_text(value)
        except Exception as e:
            browser.save_screenshot("type_select_fail.png")
            raise e

@when(parsers.parse('I select "{value}" from the Model dropdown'))
def select_model(browser, value):
    print(f"Attempting to select Model: {value}")
    time.sleep(0.5)
    try:
        # Try finding select near label "Model"
        select_elem = browser.find_element(By.XPATH, "//label[contains(text(), 'Model')]/following::select[1]")
        Select(select_elem).select_by_visible_text(value)
    except:
        # Fallback: Assume it's the THIRD select
        try:
             selects = browser.find_elements(By.TAG_NAME, "select")
             if len(selects) >= 3:
                 Select(selects[2]).select_by_visible_text(value)
        except Exception as e:
            browser.save_screenshot("model_select_fail.png")
            raise e

# ==============================================================================
#                               THEN STEPS
# ==============================================================================

@then(parsers.parse('I should see a status message saying "{message}"'))
def verify_message(browser, message):
    time.sleep(2)
    if message in browser.page_source:
        print(f"SUCCESS: Found message '{message}'")
    else:
        browser.save_screenshot("message_fail.png")
        raise AssertionError(f"Expected '{message}' but did not find it.")

@then('I should see the "Discovery Results" section')
def verify_results_section(browser):
    """
    Waits for the discovery results card/header to appear.
    """
    print("Waiting for Discovery Results...")
    try:
        # Wait up to 20 seconds for the SNMP scan to finish
        WebDriverWait(browser, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Discovery Results') or contains(text(), 'Device Found')]"))
        )
        print("SUCCESS: Discovery Results section appeared.")
    except Exception as e:
        browser.save_screenshot("results_timeout.png")
        raise AssertionError("Discovery Results did not appear within 20 seconds.") from e

@then('I should see the Hostname in the header')
def verify_hostname_header(browser):
    """Checks for the header like 'Discovery Results: RouterB'"""
    try:
        # Looks for any header tag (h1-h4) containing 'Discovery Results'
        browser.find_element(By.XPATH, "//h1[contains(text(), 'Discovery Results')] | //h2[contains(text(), 'Discovery Results')] | //h3[contains(text(), 'Discovery Results')]")
        print("SUCCESS: Found Hostname Header.")
    except Exception as e:
        browser.save_screenshot("header_fail.png")
        raise AssertionError("Could not find the 'Discovery Results' header.") from e

@then('I should see the "Raw Model ID"')
def verify_raw_model_id(browser):
    """Checks for the label 'Raw Model ID'."""
    try:
        browser.find_element(By.XPATH, "//*[contains(text(), 'Raw Model ID')]")
        print("SUCCESS: Found 'Raw Model ID' field.")
    except Exception as e:
        browser.save_screenshot("model_id_fail.png")
        raise AssertionError("Could not find 'Raw Model ID' on the page.") from e

@then('the "Confirm Add Device" button should be enabled')
def check_confirm_button(browser):
    """Checks if the Confirm button is clickable."""
    try:
        btn = browser.find_element(By.XPATH, "//button[contains(text(), 'Confirm Add Device')]")
        
        if btn.is_enabled():
             print("SUCCESS: Confirm button is enabled.")
        else:
             browser.save_screenshot("btn_disabled.png")
             raise AssertionError("Button exists but is still disabled!")
    except Exception as e:
        browser.save_screenshot("btn_missing.png")
        raise AssertionError("Could not find 'Confirm Add Device' button.") from e
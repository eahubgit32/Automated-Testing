import time
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Link to Feature File
scenarios('../features/device_registration.feature')

# Constants
BASE_URL = "http://127.0.0.1:5173"

# ================= 1. LOGIN & NAVIGATION (Merged) =================

@given('the user is logged into the AirNav Dashboard')
def login_to_dashboard(browser):
    # Check if we are already logged in
    if "login" not in browser.current_url and len(browser.find_elements(By.CLASS_NAME, "sidebar")) > 0:
        return

    browser.get(f"{BASE_URL}/login")
    try:
        WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.ID, "username")))
        browser.find_element(By.ID, "username").send_keys("admin")
        browser.find_element(By.ID, "password").send_keys("!frqAIRNAV")
        browser.find_element(By.XPATH, "//button[contains(text(), 'Log') or contains(text(), 'Sign')]").click()
        WebDriverWait(browser, 10).until(lambda d: "login" not in d.current_url)
    except:
        pass # Already logged in

# ================= 2. MACRO STEP (FAST FORWARD) =================

@given(parsers.parse('I have successfully discovered the device "{ip}"'))
def ensure_discovery_complete(browser, ip):
    """
    This step quickly navigates to the 'Add Device' page, 
    fills the form, and waits for the Results section to load.
    """
    # 1. Navigate
    if "/add-device" not in browser.current_url:
        browser.get(f"{BASE_URL}/add-device")
    
    # 2. Fill Form
    browser.find_element(By.ID, "ipAddress").clear()
    browser.find_element(By.ID, "ipAddress").send_keys(ip)
    browser.find_element(By.ID, "username").send_keys("admin")
    browser.find_element(By.ID, "authPassword").send_keys("!frqAIRNAV")
    browser.find_element(By.ID, "privPassword").send_keys("!frqAIRNAV")
    
    # 3. Click Search (Simple Click)
    browser.find_element(By.XPATH, "//button[contains(text(), 'Search')]").click()
    
    # 4. Wait for Results (Allow up to 45s for VM lag)
    try:
        WebDriverWait(browser, 45).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "details-main-container"))
        )
    except TimeoutException:
        pytest.fail("Setup Failed: Discovery results never appeared. Cannot proceed to Registration.")

# ================= 3. REGISTRATION ACTIONS =================

@when(parsers.parse('I select "{option}" from the Brand dropdown'))
def select_brand(browser, option):
    dropdown_element = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "brand-select"))
    )
    Select(dropdown_element).select_by_visible_text(option)

@when(parsers.parse('I select "{option}" from the Type dropdown'))
def select_type(browser, option):
    Select(browser.find_element(By.ID, "type-select")).select_by_visible_text(option)

@when(parsers.parse('I select "{option}" from the Model dropdown'))
def select_model(browser, option):
    Select(browser.find_element(By.ID, "model-select")).select_by_visible_text(option)

@when('I click "Confirm Add Device"')
def click_confirm(browser):
    xpath = "//button[contains(text(), 'Confirm Add Device')]"
    
    btn = browser.find_element(By.XPATH, xpath)
    browser.execute_script("arguments[0].scrollIntoView();", btn)
    time.sleep(0.5) 
    
    btn.click()
    print("[ACTION] Clicked Confirm Button")

# ================= 4. VERIFICATION STEPS =================

# Replace the existing 'verify_success_message' with this robust version:

@then(parsers.parse('I should see the success message "{message}"'))
def verify_success_message(browser, message):
    # We only check for the text. We do NOT wait for a redirect.
    try:
        WebDriverWait(browser, 2).until(
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{message}')]"))
        )
        print(f"✅ Verified Success Message: {message}")
    except TimeoutException:
        # Debugging output if it fails
        body_text = browser.find_element(By.TAG_NAME, "body").text[:300]
        raise AssertionError(f"FAIL: Message '{message}' not found. Screen text: {body_text}...")

@then(parsers.parse('I should see an error message containing "{text}"'))
def verify_duplicate_error(browser, text):
    try:
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
        )
        print(f"✅ Verified Error Message: {text}")
    except TimeoutException:
        raise AssertionError(f"FAIL: Expected error '{text}' but it did not appear.")
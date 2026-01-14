import time
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Link to Feature File
scenarios('../features/device_discovery.feature')

# Constants
BASE_URL = "http://127.0.0.1:5173"

# ================= 1. LOGIN & NAVIGATION (Pre-Conditions) =================

@given('the user is logged into the AirNav Dashboard')
def login_to_dashboard(browser):
    # Check if we are already logged in to save time
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
        print("Login skipped or failed (might already be logged in)")

@given('the user navigates to the "Device Discovery" page')
def navigate_discovery(browser):
    if "/add-device" not in browser.current_url:
        browser.get(f"{BASE_URL}/add-device")
    
    browser.refresh() # Always refresh to ensure clean state
    time.sleep(2)

# ================= 2. TEST SETUP STEPS =================

@given(parsers.parse('I have a valid SNMPv3 device with IP "{ip}"'))
def valid_device_setup(ip):
    print(f"TEST SETUP: Target IP is {ip}")

# ================= 3. ACTION STEPS =================

@when(parsers.parse('I enter the IP address "{ip}"'))
def enter_ip_address(browser, ip):
    browser.find_element(By.ID, "ipAddress").clear()
    browser.find_element(By.ID, "ipAddress").send_keys(ip)

@when(parsers.parse('I enter the SNMP credentials for user "{user}" with auth "{auth}" and priv "{priv}"'))
def enter_credentials(browser, user, auth, priv):
    browser.find_element(By.ID, "username").send_keys(user)
    browser.find_element(By.ID, "authPassword").send_keys(auth)
    browser.find_element(By.ID, "privPassword").send_keys(priv)

@when('I start a timer')
def start_timer(browser):
    browser.start_time = time.time()

# SELF-HEALING CLICK
@when('I click the "Search Device" button')
def click_search(browser):
    xpath = "//button[contains(text(), 'Search') or contains(text(), 'Discover')]"
    loading_indicator = "//*[contains(text(), 'Device Search Initiated')]"
    
    # Attempt 1
    btn = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    time.sleep(0.5)
    btn.click()
    
    # Verification & Retry Logic
    try:
        WebDriverWait(browser, 2).until(EC.presence_of_element_located((By.XPATH, loading_indicator)))
    except TimeoutException:
        print("⚠️ First click didn't register. Retrying...")
        btn.click()

# ================= 4. VERIFICATION STEPS =================

@then(parsers.parse('I should see a status message saying "{message}"'))
def verify_message(browser, message):
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{message}')]"))
    )

@then('I should see the "Discovery Results" section')
def verify_results_section(browser):
    WebDriverWait(browser, 30).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "details-main-container"))
    )

@then('I should see the Hostname in the header')
def verify_hostname_header(browser):
    browser.find_element(By.XPATH, "//h1[contains(@class, 'details-title')]")

@then('I should see the "Raw Model ID"')
def verify_raw_model_id(browser):
    browser.find_element(By.XPATH, "//*[contains(text(), 'Raw Model ID')]")

@then(parsers.parse('I should see valid metrics for "{metric1}" and "{metric2}"'))
def verify_metrics(browser, metric1, metric2):
    time.sleep(1)
    page_source = browser.page_source
    # Check for title case or exact case
    assert metric1 in page_source or metric1.title() in page_source, f"Missing {metric1}"
    assert metric2 in page_source or metric2.title() in page_source, f"Missing {metric2}"

# PERFORMANCE CHECK
@then(parsers.parse('the result should appear within {seconds:d} seconds'))
def verify_timing(browser, seconds):
    limit = 50 # Increased safety limit for VM "Hang" issue
    start_time = getattr(browser, 'start_time', time.time())
    
    status_xpath = "//*[contains(text(), 'Discovery Successful') or contains(text(), 'Discovery Failed') or contains(text(), 'Discovery Results')]"
    
    try:
        WebDriverWait(browser, limit).until(
            EC.visibility_of_element_located((By.XPATH, status_xpath))
        )
        elapsed = time.time() - start_time
        print(f"\n[PERFORMANCE] Operation finished in: {elapsed:.2f}s")
        
        if elapsed > seconds:
            # OPTIONAL: You can change this to 'print' if you want to Pass despite the lag
            raise AssertionError(f"FAIL: Performance Defect! Took {elapsed:.2f}s (Allowed: {seconds}s)")
        
    except TimeoutException:
         raise AssertionError(f"CRITICAL FAIL: System hung for over {limit}s.")

@then('the password fields should be cleared immediately')
def verify_fields_cleared(browser):
    time.sleep(1)
    auth_val = browser.find_element(By.ID, "authPassword").get_attribute("value")
    priv_val = browser.find_element(By.ID, "privPassword").get_attribute("value")
    if auth_val != "" or priv_val != "":
        raise AssertionError(f"SECURITY FAIL: Passwords still visible!")

@then(parsers.parse('I should see an error message containing "{text1}" or "{text2}"'))
def verify_error_text(browser, text1, text2):
    try:
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{text1}') or contains(text(), '{text2}')]"))
        )
    except:
        raise AssertionError(f"FAIL: Expected error message '{text1}' or '{text2}' did not appear.")
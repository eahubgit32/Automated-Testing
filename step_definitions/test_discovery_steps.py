import time
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Link to Feature File
scenarios('../features/device_discovery.feature')

# Constants
BASE_URL = "http://127.0.0.1:5173"

# ================= GIVEN STEPS =================
@given('the user is logged into the AirNav Dashboard')
def login_to_dashboard(browser):
    login_url = f"{BASE_URL}/login"
    browser.get(login_url)
    try:
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "username")))
        browser.find_element(By.ID, "username").send_keys("admin")
        browser.find_element(By.ID, "password").send_keys("!frqAIRNAV")
        browser.find_element(By.XPATH, "//button[contains(text(), 'Log') or contains(text(), 'Sign')]").click()
        WebDriverWait(browser, 15).until(lambda d: "login" not in d.current_url)
    except Exception as e:
        print(f"Login Failed: {e}")
        raise e

@given('the user navigates to the "Device Discovery" page')
def navigate_discovery(browser):
    browser.get(f"{BASE_URL}/add-device")
    browser.refresh()
    time.sleep(2) # Allow React to bind event listeners

@given(parsers.parse('I have a valid SNMPv3 device with IP "{ip}"'))
def valid_device_setup(ip):
    print(f"TEST SETUP: Target IP is {ip}")

# ================= WHEN STEPS =================
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

# --- FIXED: SELF-HEALING CLICK ---
@when('I click the "Search Device" button')
def click_search(browser):
    xpath = "//button[contains(text(), 'Search') or contains(text(), 'Discover')]"
    loading_indicator = "//*[contains(text(), 'Device Search Initiated')]"
    
    # 1. First Attempt
    btn = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    time.sleep(1) # Humanizer
    btn.click()
    print("[ACTION] Clicked Search Button (Attempt 1)")
    
    # 2. VERIFY: Did it actually work?
    try:
        WebDriverWait(browser, 2).until(
            EC.presence_of_element_located((By.XPATH, loading_indicator))
        )
        print("✅ Click verified: Loading message appeared.")
    except TimeoutException:
        print("⚠️ Click failed (React wasn't ready). Clicking again...")
        # 3. Second Attempt (Retry)
        btn.click()
        WebDriverWait(browser, 2).until(
             EC.presence_of_element_located((By.XPATH, loading_indicator))
        )
        print("✅ Click verified on Attempt 2.")

# ================= THEN STEPS =================

@then(parsers.parse('I should see a status message saying "{message}"'))
def verify_message(browser, message):
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{message}')]"))
        )
    except TimeoutException:
        raise AssertionError(f"FAIL: Message '{message}' not found. Current Page Text:\n{browser.find_element(By.TAG_NAME, 'body').text[:200]}...")

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
    if metric1 not in page_source and metric1.title() not in page_source:
         raise AssertionError(f"Metric {metric1} not found")
    if metric2 not in page_source and metric2.title() not in page_source:
         raise AssertionError(f"Metric {metric2} not found")

# --- FIXED PERFORMANCE CHECK (With Debugging) ---
@then(parsers.parse('the result should appear within {seconds:d} seconds'))
def verify_timing(browser, seconds):
    limit = 45 
    start_time = getattr(browser, 'start_time', time.time())
    
    # Look for Success (Valid IP) OR Failure (Invalid IP)
    status_xpath = "//*[contains(text(), 'Discovery Successful') or contains(text(), 'Discovery Failed') or contains(text(), 'Discovery Results')]"
    
    try:
        WebDriverWait(browser, limit).until(
            EC.visibility_of_element_located((By.XPATH, status_xpath))
        )
        elapsed = time.time() - start_time
        print(f"\n[PERFORMANCE] Operation finished in: {elapsed:.2f}s")
        
        if elapsed > seconds:
            raise AssertionError(f"FAIL: Too Slow! Took {elapsed:.2f}s (Max allowed: {seconds}s)")
        
        print(f"✅ PASS: Performance within limits.")

    except TimeoutException:
        elapsed = time.time() - start_time
        # DEBUG: Print what is actually on the screen if it fails
        body_text = browser.find_element(By.TAG_NAME, "body").text
        print(f"\n[DEBUG] Screen Content at Failure:\n{body_text[:500]}")
        
        raise AssertionError(f"CRITICAL FAIL: System hung for over {elapsed:.2f}s. No Success/Fail message found.")

# ... (Keep Security/Error steps the same) ...
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
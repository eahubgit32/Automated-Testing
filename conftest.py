import pytest
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

@pytest.fixture
def browser():
    # 1. SETUP: Install GeckoDriver for Firefox automatically
    print("\n[Setup] Installing/Updating GeckoDriver (Firefox)...")
    service = FirefoxService(GeckoDriverManager().install())
    
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless") # Uncomment if you want it to run without a GUI window
    
    # Initialize Firefox
    driver = webdriver.Firefox(service=service, options=options)
    
    # Set default wait time
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    # 2. YIELD: Give the driver to the test
    yield driver
    
    # 3. TEARDOWN: Close it
    print("\n[Teardown] Closing Firefox...")
    driver.quit()
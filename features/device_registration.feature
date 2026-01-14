Feature: Device Registration (Block A1-005)
  As an Administrator
  I want to register a discovered device
  So that it is added to the monitoring dashboard

  Background:
    Given the user is logged into the AirNav Dashboard

# --- [TC-A1-005a] Successful Registration ---
  @TC-A1-005a @Registration @HappyPath
  Scenario: Successfully Register a Valid Device
    Given I have successfully discovered the device "192.168.33.254"
    When I select "Cisco" from the Brand dropdown
    And I select "Router" from the Type dropdown
    And I select "Cisco4321" from the Model dropdown
    And I click "Confirm Add Device"
    # 👇 CHANGE THIS LINE to match the actual app text
    Then I should see the success message "registered successfully"

  # --- [TC-A1-005b] Duplicate Registration Check ---
  @TC-A1-005b @Registration @Negative
  Scenario: Attempt to Register a Duplicate Device
    Given I have successfully discovered the device "192.168.33.254"
    When I select "Cisco" from the Brand dropdown
    And I select "Router" from the Type dropdown
    And I select "Cisco4321" from the Model dropdown
    And I click "Confirm Add Device"
    Then I should see an error message containing "already exists"
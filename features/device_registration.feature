Feature: Device Registration (Block A1-005)

  Background:
    Given the user is logged into the AirNav Dashboard
    And the user navigates to the "Device Discovery" page
    And I have successfully discovered the device "192.168.33.254"

  @TC-A1-005a @HappyPath
  Scenario: Successful Device Registration
    When I select "Cisco" from the Brand dropdown
    And I select "Router" from the Type dropdown
    And I select "Cisco4321" from the Model dropdown
    And I click "Confirm Add Device"
    Then I should see the success message "Device Registered Successfully"
    And I should be redirected to the Dashboard


  @TC-A1-005b @Negative
  Scenario: Prevent Duplicate Registration
    # 1. First, ensure the device is ALREADY there (Pre-condition)
    # (In a real test, you might use API to inject it, but here we assume it exists or we try adding it twice)
    
    Given I have a valid SNMPv3 device with IP "192.168.33.254"
    When I enter the IP address "192.168.33.254"
    And I enter the SNMP credentials for user "admin" with auth "!frqAIRNAV" and priv "!frqAIRNAV"
    And I click the "Search Device" button
    And I should see the "Discovery Results" section
    
    # Select Dropdowns to enable button
    When I select "Cisco" from the Brand dropdown
    And I select "Router" from the Type dropdown
    And I select "Cisco 4321" from the Model dropdown
    
    # 2. Try to Add it
    And I click "Confirm Add Device"
    
    # 3. VERIFY ERROR (Adjust text based on your actual app error)
    Then I should see an error message containing "Device with this IP already exists"
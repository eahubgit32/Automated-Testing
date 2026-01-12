# device_discovery.feature

Feature: Network Device Discovery (Block A1)
  As an Administrator
  I want to discover network devices using SNMP
  So that I can see their metrics before registering them

  Background:
    Given the user is logged into the AirNav Dashboard
    And the user navigates to the "Device Discovery" page

  @TC-A1-001b @HighPriority
  Scenario: Verify Discovery Results and Select Model
    Given I have a valid SNMPv3 device with IP "192.168.33.254"
    When I enter the IP address "192.168.33.254"
    And I enter the SNMP credentials for user "admin" with auth "!frqAIRNAV" and priv "!frqAIRNAV"
    And I click the "Search Device" button
    
    # --- VERIFICATION STEPS (Updated for your UI) ---
    Then I should see the "Discovery Results" section
    And I should see the Hostname in the header
    And I should see the "Raw Model ID"
    
    # --- DROPDOWN SELECTION STEPS (New) ---
    When I select "Cisco" from the Brand dropdown
    And I select "Router" from the Type dropdown
    And I select "Cisco4321" from the Model dropdown
    
    # --- FINAL CHECK ---
    Then the "Confirm Add Device" button should be enabled
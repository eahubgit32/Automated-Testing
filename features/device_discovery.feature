Feature: Network Device Discovery (Block A1)
  As an Administrator
  I want to discover network devices using SNMP
  So that I can see their metrics before registering them

  Background:
    Given the user is logged into the AirNav Dashboard
    And the user navigates to the "Device Discovery" page

  # --- [TC-A1-001] Functional & [TC-A1-001b] Data Verification ---
  @TC-A1-001a @TC-A1-001b @HighPriority @HappyPath
  Scenario: Successful Device Discovery and Data Verification
    Given I have a valid SNMPv3 device with IP "192.168.33.254"
    When I enter the IP address "192.168.33.254"
    And I enter the SNMP credentials for user "admin" with auth "!frqAIRNAV" and priv "!frqAIRNAV"
    And I click the "Search Device" button
    Then I should see a status message saying "Device Search Initiated"
    # Verification Steps (TC-A1-001b)
    And I should see the "Discovery Results" section
    And I should see the Hostname in the header
    And I should see the "Raw Model ID"
    And I should see valid metrics for "CPU Usage" and "Memory"

  # --- [TC-A1-002] Performance (Timeouts) ---
  @TC-A1-002a @TC-A1-002b @Performance
  Scenario Outline: Discovery Performance Constraints
    When I enter the IP address "<ip>"
    And I enter the SNMP credentials for user "admin" with auth "!frqAIRNAV" and priv "!frqAIRNAV"
    And I start a timer
    And I click the "Search Device" button
    Then the result should appear within <seconds> seconds
    
    Examples:
      | ip             | seconds | description      |
      | 192.168.33.254 | 15      | Valid Device     |
      | 10.255.255.255 | 10      | Unreachable IP   |

  # --- [TC-A1-003] Security (Field Clearing) ---
  @TC-A1-003a @Security
  Scenario: Security Field Clearing
    When I enter the IP address "192.168.33.254"
    And I enter the SNMP credentials for user "admin" with auth "!frqAIRNAV" and priv "!frqAIRNAV"
    And I click the "Search Device" button
    Then the password fields should be cleared immediately

  # --- [TC-A1-004] Error Handling ---
  @TC-A1-004a @Negative
  Scenario: Error Message Validation (Invalid Auth)
    When I enter the IP address "192.168.33.254"
    And I enter the SNMP credentials for user "admin" with auth "WRONG_PASS" and priv "WRONG_PASS"
    And I click the "Search Device" button
    Then I should see an error message containing "Authentication failure" or "Time-out"
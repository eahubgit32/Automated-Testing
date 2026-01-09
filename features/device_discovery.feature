Feature: Network Device Discovery (Block A1)
  As an Administrator
  I want to discover network devices using SNMP
  So that I can monitor their status and metrics

  Background:
    Given the user is logged into the AirNav Dashboard
    And the user navigates to the "Device Discovery" page

@TC-A1-001a @HighPriority @HappyPath
  Scenario: Successful Device Discovery Initiation
    Given I have a valid SNMPv3 device with IP "192.168.33.254"
    When I enter the IP address "192.168.33.254"
    # CHANGED: We removed the pipe table | | and put data here directly:
    And I enter the SNMP credentials for user "admin" with auth "!frqAIRNAV" and priv "!frqAIRNAV"
    And I click the "Search Device" button
    Then I should see a status message saying "Device Search Initiated"
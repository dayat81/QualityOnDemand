Feature: Proposed change to createSession 400.9 (excerpt, for upstream discussion)

  Background: Common createSession setup
    Given an environment at "apiRoot"
    And the resource "/quality-on-demand/vwip/sessions"
    And the header "Content-Type" is set to "application/json"
    And the header "Authorization" is set to a valid access token
    And the header "x-correlator" complies with the schema at "#/components/schemas/XCorrelator"
    And the request body is set by default to a request body compliant with the schema at "#/components/schemas/CreateSession"

  # Both codes are in the OAS: either is accepted (same approach as the README states for port ranges and accessTokenType)
  @quality_on_demand_createSession_400.9_invalid_duration
  Scenario: Error response when duration is not valid for selected qos profile
    Given the request body property "duration" is set to an invalid duration for the selected qosProfile
    When the request "createSession" is sent
    Then the response status code is 400
    And the response header "x-correlator" has same value as the request header "x-correlator"
    And the response header "Content-Type" is "application/json"
    And the response property "$.status" is 400
    And the response property "$.code" is "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE" or "INVALID_ARGUMENT"
    And the response property "$.message" contains a user friendly text

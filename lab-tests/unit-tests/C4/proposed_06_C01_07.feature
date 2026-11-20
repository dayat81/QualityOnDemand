Feature: Proposed disambiguation of _06 vs C01.07 (excerpt, for upstream discussion)

  Background: Common retrieveQosProfiles setup
    Given an environment at "apiRoot"
    And the resource "/qos-profiles/vwip/retrieve-qos-profiles"
    And the header "Content-Type" is set to "application/json"
    And the header "Authorization" is set to a valid access token

  @qos_profiles_retrieveQosProfiles_06_device_qos_profiles_not_found
  Scenario: Eligible device has no QoS profiles associated
    Given a valid device, provided in the request body or identified by the access token, for which the service is applicable
    And no QoS Profile is associated to that device
    When the request "retrieveQosProfiles" is sent
    Then the response status code is 200
    And the response header "Content-Type" is "application/json"
    And the response body is []

  # When the service is only offered to certain types of devices or subscriptions, e.g. IoT, B2C, etc.
  @qos_profiles_retrieveQosProfiles_C01.07_device_not_supported
  Scenario: Service not available for the device
    Given that the service is not available for all devices commercialized by the operator
    And a valid device, identified by the token or provided in the request body, for which the service is not offered
    When the HTTP "POST" request is sent
    Then the response status code is 422
    And the response property "$.code" is "SERVICE_NOT_APPLICABLE"

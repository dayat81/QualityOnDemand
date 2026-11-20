Feature: Proposed QoS_STATUS_CHANGED scenarios for DURATION_EXPIRED and NETWORK_TERMINATED (excerpt, for upstream discussion)

  Background: Common createSession setup
    Given an environment at "apiRoot"
    And the resource "/quality-on-demand/vwip/sessions"
    And the header "Content-Type" is set to "application/json"
    And the header "Authorization" is set to a valid access token
    And the header "x-correlator" complies with the schema at "#/components/schemas/XCorrelator"
    And the request body is set by default to a request body compliant with the schema at "#/components/schemas/CreateSession"

  # NOTE: 02_3 is already used upstream (private_key_jwt), hence 02_4 and 02_5.
  @quality_on_demand_createSession_02_4_event_duration_expired
  Scenario: Event is received when the session duration expires
    Given a valid testing device supported by the service, identified by the token or provided in the request body
    And the request body property "$.applicationServer" is set to a valid application server
    And the request property "$.qosProfile" is set to a valid QoS Profile as returned by QoS Profiles API
    And the request body property "$.duration" is set to a short valid duration for the selected QoS profile
    And the request property "$.sink" is set to a URL where events can be monitored
    And the request property "$.sinkCredential.credentialType" is set to "ACCESSTOKEN"
    And the request property "$.sinkCredential.accessTokenType" is set to "bearer"
    And the request property "$.sinkCredential.accessToken" is set to a valid access token accepted by the events receiver
    When the request "createSession" is sent
    And the session duration elapses
    Then an event is received at the address of the request property "$.sink"
    And the event header "Authorization" is set to "Bearer " + the value of the request property "$.sinkCredential.accessToken"
    And the event header "Content-Type" is set to "application/cloudevents+json"
    And the event body complies with the OAS schema at "#/components/schemas/EventQosStatusChanged"
    And the event body property "$.id" is unique
    And the event body property "$.type" is set to "org.camaraproject.quality-on-demand.v1.qos-status-changed"
    And the event body property "$.data.sessionId" has the same value as createSession response property "$.sessionId"
    And the event body property "$.data.qosStatus" is "UNAVAILABLE"
    And the event body property "$.data.statusInfo" is "DURATION_EXPIRED"
    And exactly one event with this "$.data.qosStatus" and "$.data.statusInfo" is received for the session

  @quality_on_demand_createSession_02_5_event_network_terminated
  Scenario: Event is received when the network terminates the session
    Given a QoS session has been created successfully and includes a valid sink and sinkCredentials
    When the network terminates the QoS session, or fails to provide it after creation
    Then an event is received at the address of the request property "$.sink"
    And the event body complies with the OAS schema at "#/components/schemas/EventQosStatusChanged"
    And the event body property "$.type" is set to "org.camaraproject.quality-on-demand.v1.qos-status-changed"
    And the event body property "$.data.sessionId" has the same value as createSession response property "$.sessionId"
    And the event body property "$.data.qosStatus" is "UNAVAILABLE"
    And the event body property "$.data.statusInfo" is "NETWORK_TERMINATED"
    And exactly one event with this "$.data.qosStatus" and "$.data.statusInfo" is received for the session

@orderflow @bdd_rq
Feature: Order Processing

Background:
  Given "osr" feature is set in env

  @bdd_testrail=791582
  Scenario Outline: Validate the order flow process with OSR and Manual
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>"
    And order is consolidated and staged
    Then order status matches ORDER_STATUS_AFTER_PICKING config in TSC

       Examples:
        | osr | in-store | manual | variable_weight | service_type|
        | 1   | 0   | 0      | 0               | DELIVERY |
        | 0   | 0   | 1      | 0               | DELIVERY |
        | 1   | 0   | 1      | 0               | DELIVERY |

  @bdd_testrail=791583
  Scenario Outline: Validate the order creation with required fields only
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created and split naturally with required fields and type "<service_type>"

    Then order is in "queued" status
    And view and validate order details json structure
    
    Examples:
    | osr | in-store | manual | variable_weight | service_type|
    | 1   | 0   | 0      | 0               | DELIVERY |

@truckload_flow @bdd_rq
Feature: Truckload
Background:
    Given "truckload" feature is set in env

  @bdd_testrail=791591
  Scenario Outline: Test truckload feature for retailers
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>"
    And order is consolidated and staged
    And user performs Truck Load

    Then order status matches ORDER_STATUS_AFTER_PICKING config in TSC

     Examples:
      | osr | in-store | manual | variable_weight | service_type|
      | 0   | 1   | 1      | 0               | DELIVERY |
      | 0   | 1   | 0      | 0               | DELIVERY |
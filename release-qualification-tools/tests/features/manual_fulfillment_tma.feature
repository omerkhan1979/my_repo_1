@tma_fulfillment @bdd_rq
Feature: TMA Manual fulfillment

  @bdd_testrail=791580
  Scenario Outline: Manual fulfillment for TMA

    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>"
    And order is consolidated and staged with tma

    Then order status matches ORDER_STATUS_AFTER_PICKING config in TSC

     Examples:
      | osr | in-store | manual | variable_weight | service_type|
      | 0   | 0   | 1      | 0               | DELIVERY |



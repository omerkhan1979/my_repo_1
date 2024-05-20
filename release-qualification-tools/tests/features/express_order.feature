@expressorder_flow @bdd_rq
Feature: Express Order

Background:
  Given "express-order" feature is set in env

  @bdd_testrail=791573
  Scenario Outline: Create order for validating the express flow
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>"
    And  order is consolidated and staged

    Then order status matches ORDER_STATUS_AFTER_PICKING config in TSC

    Examples:
      | osr | manual | in-store | variable_weight | service_type   |
      | 0   | 1      | 0   | 0               |   express      |

@host @bdd_rq
Feature: Item with not enough stock

Background:
  Given "mfc_to_host" feature is set in env

  @bdd_testrail=791571
  Scenario Outline: Create order for validating duplicate line item
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment
    When  order is created with zero stock and with type "<service_type>"

    Then product that are not fully available should be fulfilled by host

    Examples:
      | osr | manual | in-store | variable_weight | service_type   |
      | 2   | 0      | 0   | 0               |   DELIVERY      |

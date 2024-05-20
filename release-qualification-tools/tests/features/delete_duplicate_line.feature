@delete_duplicate_line @bdd_rq
Feature: Delete duplicate items

Background:
  Given "delete-duplicate-line-items" feature is set in env

  @bdd_testrail=791571
  Scenario Outline: Create order for validating duplicate line item
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment
    And   duplicate products are added to the order content
    When  order is created with type "<service_type>"
    And  order is consolidated and staged

    Then duplicate items are not included in the order

    Examples:
      | osr | manual | in-store | variable_weight | service_type   |
      | 1   | 1      | 0   | 0               |   DELIVERY      |

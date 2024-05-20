@delete_unrecognized_line @bdd_rq
Feature: Delete unrecognized items

  Background:
    Given "delete-unrecognized-line-items" feature is set in env

  @bdd_testrail=791572
  Scenario Outline: Create order for validating the unrecognized line item
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment
    And   unrecognized products are added to the order content
    When  order is created with type "<service_type>"
    And  order is consolidated and staged

    Then unrecognzied items are not included in the order

    Examples:
      | osr | manual | in-store | variable_weight | service_type   |
      | 1   | 1      | 0   | 0               |   DELIVERY      |
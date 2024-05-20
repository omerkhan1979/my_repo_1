@update_order_before_preprocessing @bdd_rq
Feature: Update Customer Order before processing

Background:
  Given "osr" configuration is set in env

  @bdd_testrail=791600
  Scenario Outline: Update products in the customer order
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>"

    Then Update order by removing one item and validate product count
    And Update order by adding one item and validate product count

    Examples:
      | osr | in-store | manual | variable_weight | service_type |
      | 2   | 0        | 0      | 0               | DELIVERY     |

  @bdd_testrail=791601
  Scenario Outline: Update specific fields of the customer order
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>"

    Then Update order with "<field_name>" and "<field_value>"

     Examples:
      | osr | in-store | manual | variable_weight | service_type | field_name         | field_value   |
      | 1   | 0        | 0      | 0               | DELIVERY     | route-id           | 2             |
      | 1   | 0        | 0      | 0               | DELIVERY     | line-note          | Update line   |
      | 1   | 0        | 0      | 0               | DELIVERY     | order-note         | UO            |
      | 1   | 0        | 0      | 0               | DELIVERY     | requested-quantity | 5             |
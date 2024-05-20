@ordernote @bdd_rq
Feature: Creating orders with the order note field

  Background:
    Given "osr" feature is set in env

  @bdd_testrail=791584
  Scenario Outline: Validate the order creation with the order note field

    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>" and "<order_note>"
    Then  order is in "queued" status
    And order note field is correctly displayed as "<order_note>"

       Examples:
        | osr | in-store | manual | variable_weight | service_type| order_note   |
        | 1   | 0   | 0      | 0               | DELIVERY    | None         |
        | 1   | 0   | 0      | 0               | DELIVERY    | " "          |
        | 1   | 0   | 0      | 0               | DELIVERY    | RANDOM_NOTE  |
@picking_weighted_item @bdd_rq
Feature: Picking weighted items
  Background:
      Given "WEIGHT_AGGREGATED" feature is set in env

  @bdd_testrail=791586
  Scenario Outline: Picking manual and manual_weighted items

    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>"
    And verify the weighted items are aggregated during the picking stage


     Examples:
      | osr | in-store | manual | variable_weight | service_type|
      | 1   | 1   | 0      | 1               | DELIVERY |
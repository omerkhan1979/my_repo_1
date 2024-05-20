@short_pick @bdd_rq
Feature: This feature file covers short picking of product scenarios for diff locations OSR, Manual and In_Store
  Background:
      Given "shortpick" feature is set in env

  @bdd_testrail=644647
  Scenario Outline: Perform in_store picking of an out of stock product and confirm it as shortpick

    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment


    When order is created with zero stock and with type "<service_type>"
    And user processes "<picklist_type>" picklist for zero quantity
    And order status changed to "<status>"
    Then validate the product is short picked and line note updated to out of stock

    Examples:
      | osr | in-store | manual | variable_weight | service_type | picklist_type |status|
      | 0   | 1        | 0     | 0               | DELIVERY     | PRELIM        |served |

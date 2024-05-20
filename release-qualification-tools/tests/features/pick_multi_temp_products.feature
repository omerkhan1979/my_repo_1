@multi_temp_picking @bdd_rq
Feature: Order Picking
  Background:
      Given "multi-temp-osr-picking" feature is set in env

  @bdd_testrail=791585
  Scenario Outline: Picking OSR from multi-temp zone (Ambient and Chilled)

    Given products available with <temp_zone> temp zones in the environment

    When order is created
    And products are picked into the same tote
    And order is consolidated and staged

    Then order status matches ORDER_STATUS_AFTER_PICKING config in TSC

     Examples:
       |temp_zone |
       |ambient,chilled|

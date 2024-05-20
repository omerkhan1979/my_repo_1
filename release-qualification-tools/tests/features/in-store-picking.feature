@ispsflow @bdd_rq
Feature: This feature file covers the in-store picking flow with prelim and delta picklists
  Background:
      Given "in-store-picking" feature is set in env

  @bdd_testrail=791574
  Scenario Outline: Perform an end to end in-store order picking flow

    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>"
    And user processes "<picklist_type>" picklist to completion
    And order is consolidated and staged

    Then order status matches ORDER_STATUS_AFTER_PICKING config in TSC

     Examples:
      | osr | in-store | manual | variable_weight | service_type | picklist_type |
      | 1   | 1   | 0      | 0               | DELIVERY     | PRELIM        |
      | 1   | 1   | 0      | 0               | DELIVERY     | DELTA         |
      | 1   | 1   | 0      | 0               | DELIVERY     | PRELIM,DELTA  |

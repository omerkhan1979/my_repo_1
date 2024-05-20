@ecom_status_update @bdd_rq
Feature: update ecom status after order creation

Background:
  Given "update_ecom_status" feature is set in env

  @bdd_testrail=791571
  Scenario Outline: Create order for validating duplicate line item
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment
    When  order is created with type "<service_type>"
    And ecom status is updated with "<update_ecom_status>"

    Then ecom status after update should be "<expected_ecom_status>"

    Examples:
      | osr | in-store | manual | variable_weight | service_type   | update_ecom_status |expected_ecom_status|
      | 0   | 0      | 2   | 0               |   DELIVERY      |  PickingDownloaded |new|
      | 0   | 0      | 2   | 0               |   DELIVERY      |  CustomerCancelled |cancelled|
      | 0   | 0      | 2   | 0               |   DELIVERY      |  READY_FOR_ACTION | queued|

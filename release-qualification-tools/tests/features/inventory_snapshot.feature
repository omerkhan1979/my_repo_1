@inventory_snapshot @bdd_rq
Feature: This feature file matches the inventory snapshot for a selected product using different endpoints like rint, IMS and newly added inventory manager

  @bdd_testrail=791577
  Scenario: Compare an inventory snapshot between RINT and IMS
    Given inventory snapshot for a product is taken from rint
    And  inventory snapshot for the same product is taken from IMS
    Then quantity in rint is equal the total the quantity in IMS


  @bdd_testrail=791578
  Scenario: Compare an Inventory Snapshot for a product between Inventory Manager and IMS
    Given inventory snapshot for a product is taken from inventory manager
    And  inventory snapshot for the same product is taken from IMS
    Then quantity on-hand in Inventory Manager is equal to Total Quantity in IMS

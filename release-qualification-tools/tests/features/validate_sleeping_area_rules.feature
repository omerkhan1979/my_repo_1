@sleeping_area_rules @bdd_rq
Feature: sleeping areas rules
  Scenario Outline: Validate if a product fall under the correct sleeping area rule

    Given the product catalog with "<temp_zone>" item
    And sleeping area rule with "<sleeping_area>" and "<temp_zone>"
    When product catalog is uploaded
    Then product should fall under sleeping area rule

     Examples:
      | sleeping_area |temp_zone|
      | H   | ambient           |
      | K   | chilled           |
      | A   | frozen            |

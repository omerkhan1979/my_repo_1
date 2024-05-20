@inventory_adjust @bdd_rq
Feature: This feature file explains about inventory adjustment with single and multiple reason codes

  @bdd_testrail=791575
  Scenario Outline: Inventory adjustment

    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment
    When product is adjusted with "<qty>" quantity

    Then check the product "<qty>" is increased after adjustment

     Examples:
      | osr | in-store | manual | variable_weight |qty|
      | 0   | 0   | 1      | 0               |   10|


  @bdd_testrail=791576
  Scenario Outline: Inventory adjustment with reason code

  Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment
  When product is adjusted with "<qty>" with reason code "<reason_code>"

  Then check the product "<qty>" is increased after adjustment with reason code

   Examples:
    | osr | in-store | manual | variable_weight |reason_code |qty |
    | 0   | 0   | 1      | 0               |  CC        |10|
    | 0   | 0   | 1      | 0               |   DA       |-1|
    | 0   | 0   | 1      | 0               |   EX       |-2|
    | 0   | 0   | 1      | 0               |   TH       |-3|


@linenote @bdd_rq
Feature: Add a Line Note to a product in an order

   @bdd_testrail=791579
   Scenario Outline: Ensure that a Line Note is successfully added to a product in an order

     Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

     When order is created with type "<service_type>" and "<line_note>" for the product in order
     Then order is in "queued" status
     And the line_note field for the product in the order is returned as <line_note> via API call

       Examples:
         | osr | in-store | manual | variable_weight | service_type| line_note    |
         | 1   | 0        | 0      | 0               | DELIVERY    | None         |
         | 1   | 0        | 0      | 0               | DELIVERY    | " "          |
         | 1   | 0        | 0      | 0               | DELIVERY    | RANDOM_NOTE  |

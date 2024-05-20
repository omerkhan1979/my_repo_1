@putawaytma @bdd_rq
Feature: This feature file explains about Put Away with and without Purchase Order creation

   Scenario Outline: Create a purchase order and putaway products with and without expiry dates

     @bdd_testrail=791588
     Given Create a purchase order with "<number_of_items>" and "<expiry_date_required>"
       When putaway is performed with one quantity
       Then purchase order line quantity is updated
       And inventory adjustment is recorded correctly

         Examples:
           | number_of_items | expiry_date_required |
           |   1 | False                             |
           | 1   | True                              |


    Scenario: Putaway products with daily DSD
      @bdd_testrail=791598
      Given daily DSD purchase order is created with one manual product
      When putaway is performed with one quantity
      Then purchase order line quantity is updated
      And inventory is adjusted with reason code "IB"
      Then purchase order status is "started"
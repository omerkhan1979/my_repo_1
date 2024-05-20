@decanting_without_po_dsd @bdd_rq
Feature: Decant products in the OSR without Purchase Order (PO) creation. Also known as Decanting Direct to Store Delivery (DSD)

   @bdd_testrail=791570
   Scenario Outline: Decant products without creating a Purchase Order.

     Given DSD item is decanted to OSR sleeping area "<number_of_items>"

     When decanting operation is performed with "<number_of_items>"
     Then verify that decanting operation is successful
     And decanting status is "in_progress"

       Examples:
        | number_of_items |
        | 1               |
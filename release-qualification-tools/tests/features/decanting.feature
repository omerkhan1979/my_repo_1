@decanting @bdd_rq
Feature:  Decanting products in OSR

   @bdd_testrail=791568
   Scenario Outline: Create a Purchase Order and decant products with and without expiry date

     Given Create a purchase order with "<number_of_items>" and "<expiry_date_required>"

     When decanting is performed for products in the purchase order with "<expiry_date_required>"
     Then verify that decanting operation is successful
     And purchase order status is "completed"
     And purchase order line quantity is updated
     And inventory adjustment is recorded correctly


       Examples:
        | number_of_items | expiry_date_required |
        | 1               | "True"               |
        | 2               | "True"               |
        | 4               | "False"              |
        | 8               | "False"              |


   @bdd_testrail=791569
   Scenario: Decant multiple purchase orders with one tote against a purchase order

     Given Create a purchase order via RINT API

     When decanting is performed for items in multiple purchase orders
     Then verify that decanting operation is successful
     And purchase order status is "in_progress"
     And purchase order line quantity is updated
     And all items in purchase order are received
     And inventory adjustment is recorded correctly



   @bdd_testrail=791570
   Scenario: Decant products without creating a Purchase Order

     Given item is ready for decanting in OSR sleeping area

     When decanting operation is performed without a purchase order
     Then verify that decanting operation is successful
     And purchase order status is "in_progress"
     And inventory is adjusted with reason code "ST"
     And inventory adjustment is recorded correctly


   @bdd_testrail=791570
   Scenario : Decant products with Daily DSD.
     Given  daily DSD item is ready for decanting

     When decanting operation is performed for DSD item
     Then verify that decanting operation is successful
     And inventory is adjusted with reason code "IB"
     And purchase order line quantity is updated
     And inventory adjustment is recorded correctly

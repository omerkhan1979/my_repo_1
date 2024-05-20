@po @bdd_rq
Feature: Purchase Order Management with Multiple Operations

  @bdd_testrail=791561
  Scenario: Create a purchase order via RINT API

    Given purchase order is created
    When the Purchase Order is filled by decanting the product
    Then verify that the Purchase Order appears in the distiller


  @bdd_testrail=791563
  Scenario: Create a Purchase Order via RINT file-upload API

    Given purchase order is created via RINT file-upload API
    When the Purchase Order is filled by decanting the product
    Then verify that the Purchase Order appears in the distiller


  @bdd_testrail=791564
  Scenario: Create a Purchase Order from file provided via GCP Bucket

    Given purchase order file available for upload
    When purchase order file uploaded via GCP
    Then verify that the Purchase Order appears in the distiller


  @bdd_testrail=791565
  Scenario Outline: Create Purchase Orders for MFCs via Secure File Transfer Protocol (SFTP)

    Given TOM location code "<MFC_Type>"
    When purchase order is created with SFTP
    Then verify that the Purchase Order appears in the distiller

  Examples:
    | MFC_Type |
    | WF0001   |


  @bdd_testrail=791566
  Scenario Outline: Create a Purchase Order for a Direct-to-store-delivery (DSD) file

    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment
    When a Purchase Order DSD file is created and processed
    Then verify that the Purchase Orders are present in the response from the Decanting service

  Examples:
      | osr | in-store | manual | variable_weight |
      | 1   | 0   | 0      | 0               |


  @bdd_testrail=791567
  Scenario Outline: Verify that Purchase Orders is closed

    Given the retailer MFC site is enabled in the environment
    And purchase order is created
    When get the purchase order which is created and in status "<status>"
    Then close the purchase order
  Examples:
      | status|
      | completed |


  Scenario: Receive inventory against an already existing purchase order

    Given purchase order is available for the day
    When the Purchase Order is filled by decanting the product
    Then the purchase order status is changed to "started"
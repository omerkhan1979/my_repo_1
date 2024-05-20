@product_catalog_upload @bdd_rq
Feature: Product catalog upload with all versions and upload methods

  @bdd_testrail=791587
  Scenario Outline: Upload a Product Catalog to a GCP bucket, and via Secure File Transfer Protocol (SFTP)

    Given product catalog version <pc_version> is available to upload


     When product catalog file with version <pc_version> is uploaded via GCP
     And  product catalog file with version <pc_version> is uploaded via SFTP
     Then verify that the product catalog revision value is updated

       Examples:
         | pc_version |
         | v6         |
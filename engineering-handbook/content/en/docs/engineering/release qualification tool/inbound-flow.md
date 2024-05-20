---
title: "Inbound"
linkTitle: "Inbound"
weight: 3
description: >-
    Inbound
---

# Inbound flow
The instructions below will guide you on how the inbound flow within takeoff infrastructure works and what part the RQ tools plays within it.

Main parts of inbound flow are purchase order (PO) and products of which it consists. Purchase order - is an entity which describes the products and their amounts that are to be added to the MFC.

The flow itself can be divided into two self-explanatory parts:
1. Purchase Order creation
2. Decanting

## Purchase order  
Purchase order is a list of products accompanied by quantities along with some metadata like location ID, delivery date, etc. 
Products can be of two types: 
* **Manual** - these products end up on a shelf to be further picked by an agent upon order consolidation
* **OSR** - products designated for the OSR machine, which will pull them automatically when the need arises.
Also, there are multiple modifiers for the items such as 
* **Ambient/Chilled** - this is the temperature regime for the items;
* **Chemical** - items which can not be put in totes with other products
* **Expirable** - items which have a short timespan until they go bad   
It can be created in multiple ways depending on a retailer:

1. JSON via Decanting API
2. Uploading a JSON to Google Bucket
3. Creating via GOLD software

GOLD is a third party stock-management software and working with it is a rather cumbersome experience. Information on how to  further information can be found [here](https://takeofftech.atlassian.net/wiki/spaces/takeoff/pages/684326913/Create+Purchase+Order+Gold+Central).

Decanting API call is done via **v2/purchase-order/add** endpoint, e.g. on [MAF](https://ds-qai.maf.takeofftech.io/index.html#/Purchase%20order/post_api_v2_purchase_order_add)

Google bucket is a GCP utility tool that is configured to forward received JSON files to a decanting API, for  further processing.

Within the RQ tool, the creation method is based on the retailer and you shall get a relevant prompt depending on the retailer you pick. For example, for MAF, where PO is created via Google Bucket, you are will be met with two prompts specifying amount of each type of product:

When everything is settled, the following prompt will invite you to start the decanting. 

## Decanting
Decanting involves several flows, depending on a PO that you are currently given. 
As it was previously mentioned, OSR is a machine which has numerous buckets of a particular items and it can send these buckets out on demand when we are doing the outbound work: assembling customer’s orders for delivery. The bucket rides to the picking station where responsible person takes the items from OSR buckets into the tote designated for client.

In case of OSR products in your PO, information about OSR products will be shown including barcode, TOM id, etc. Also, there will be a link to decanting UI, which is automatically composed depending on your flow settings. Th next logical step would be to follow the link.

First thing to do here there, as you have probably guessed, login. Testing account works here, although some env/retailer peculiarities may be present. When done, you will be presented with a choice of what you want to do with this particular tool. Since RQ tool covers everything inbound (i.e. PO creation and decanting) first choice, a decanting with a PO, is our guy. 


Afterwards, you shall be presented with a windows asking for a barcode, but lacking in input fields. In there, you can just start typing your PO id and press ENTER upon finishing
Once in the UI you will be presented with a 4-sectioned panel, ready to accept your products. Depending on your PO composition, the size of the tote can be increased or decreased by 2 items using the + or - buttons on the sides. 

Once you are settled with your tote size, you can proceed with the tote consolidation. In order to add product to the tote, click one of the panels and press [Manually Enter the UPC] - this is the barcode of the products which were added to the PO, either manually or automatically, and can be found in console.  
Next, you can verify that the product matches the one requested by PO and adjust the amount you would like to have in your decanted tote. Also, the product properties like chilled, chemical, etc. can be adjusted here. 
When all the necessary adjustments are made, and products are added, you can click [finish tote], and proceed to manual items.

## Put-Away

In the real world, this stage takes care of products which can not be put into OSR. This can happen due to numerous reasons, which are not the topic of this guide. However, it is important to mention that the source of these products are shelves within the store itself, and when the need arises, employees of the MFC go into the store, locate the items and place them on a shelf so they can be added to the customer’s orders.

This stage is mainly done on a mobile device. If this is your first time with this process, make sure you have Takeoff Mobile installed and that you're logged into the right environment. If you need help with this, go to the [Zendesk Takeoff Mobile](https://support.takeoff.com/hc/en-us/articles/4419282741393-Takeoff-Mobile-Accessing-Takeoff-Mobile) guide.

!The section that piques our interest in this case is **Put-Away**.  Processing of items with the aid of Takeoff Mobile is basically the same, but the good thing is, now you can utilize the scanning capabilities of the device and avoid any keyboard entry. 

When you reach this stage within the script, it should generate and open a web-page in your browser with all the barcodes required for this PO, and if you are lucky they will be in correct order. 
The logic of the process starts with the product and depending on the product a number of POs will be suggested where that product is mentioned. 
Then, you need to scan a shelf where this product is to be put. The barcode for shelf has a distinct haphazard structure, so you won’t miss it. 
When you are done with all the products within the PO. 

## Meta
So, now you have all the products decanted and/or put-away. There are two options you are facing: 
1. Abandon the PO
2. Close it

In natural environment, wild POs are usually closed.  When the flow is about to end, the script shall give you a link to TOM UI. There is little to nothing happening when the PO is closed, but for the sake of experiment, you can do so as well.

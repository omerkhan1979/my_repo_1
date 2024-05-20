---
title: "Outbound"
linkTitle: "Outbound"
weight: 4
description: >-
    Outbound flow guide
---


# Outbound flow

Greetings to you, fellow employee!

In this article we will be discussing a functionality of the system which is basically the essence of what we do here at takeoff, which is order consolidation and further dispatch to the customer. 

There is a myriad of things and processes happenings which are involved within this flow. Some of them are exposed and can be interacted with, while some have a rather background nature and are only implied. 

The most comprehensible way to play with this flow is currently expressed in Release Qualification Tool and the depth of our discussion for each and every thing will be dictated by that tool as well. 

## Setup
Upon launching of the script, you shall be greeted with a classic retailer-env-location question. It is _recommended_ to pick a QAI environment, just for stability’s sake, however your task may require something else. Don’t be shy in this case and launch the script.
## Product selection
As we have discussed in the previous article, the product storage can have two main forms:
* OSR
* Manual shelf

In real life, this choice is omitted, since orders are formed by customers which couldn’t be less concerned about the origin of their items. However, when making such an experiment, we need to make sure we know the difference and why does it matter. Also, the products can have multiple properties, such as being weighted, chilled, chemical, etc. 

When we are done with environment, we will be able to decide the composition of our order in terms of origin and the fact of being weighted.

## Picking and… Picking 
That concludes the formation of the order and it is put on tracks. First and foremost thing to do for an order is to split it. The split process is responsible for transitioning of the order from status `Draft` into `New`. Also, as the name implies, the order’s products are divided into two aforementioned categories `OSR` and `manual`. OSR items will be discussed later, now let us deal with the manual items. 

The order must be queued for picking in an appriopriate timespan. These timespans are referred to as [waves](https://takeofftech.atlassian.net/wiki/spaces/FUL/pages/2409791511/Order+Wave+Management+OWM+Microservice).

At that point within the script execution you may have noticed something being mentioned in the console, which is called picklist. That is basically an array of items from manual source. Such items are also called batch-items. When there is an incoming order within the system, batch items are processed right by being picked in the store and put on a shelf for quick access within the core of the MFC. This is done for items which can not be stored in OSR, due to reasons such as having an expiration date, peculiar or irregular dimensions or something else. When picklist is ready, it is destined to be picked. Once the script is done with forming picklists, you will be responsible for doing that. 
Now that we have a **picklist**, which we need to **pick**, the PowerRangers of Takeoff need the last element - **Takeoff Mobile**. This is an application for your Zebra, which is used by MFC employees for various tasks.

In Takeoff Mobile, we need a section called **In-Store Picking**. The status of the picklist can be seen in TOM UI. However, be aware that at any moment in time there may be multiple picklists waiting for their hero, and the way to order them on the first-to-come-first-to-serve basis is called a picking queue. There is a step within the script which clears the queue via an endpoint so that you can pick your own order. 

Once ready, press Enter and you’ll be shown a page with barcodes. Now close your eyes and imagine yourself in a canned goods isle beeping some beans. Then you take those beans to the cargo section of the store and put them on a shelf (Takeoff Mobile -> **Put away** -> **From store**). 

It is important to mention some important milestones that occur within the  of a functioning MFC. There are two main events:
* Cutoff time
* Stage-by-date time

When done, you may go to TOM and close the picklist.
## OSR time
OSR is an automated cell based product storage which can yield a tote with a bunch of particular items on demand. The typical outbound flow where the OSR is engaged looks like this:
* An operator is standing by the picking station with a box determined for the customer and there’s a screen in front of the person.
* Totes with one type of items per tote come out on a conveyor belt as per the details of the order 
* The operator moves necessary amount of items to the customer tote and marks his accomplishments on the screen

That is basically it. 
Since there is no opportunity to have an OSR in the office for the needs of development and testing, let alone having one at home during these trying times, there is something called an OSR emulator. It inherits capabilities of the OSR to store and yield items on demand.

Within this step you are to scan three things: address of the item, staging locations ant totes.
If you’re done with the process, you did good. That concludes the outbound order flow. In case you have any questions left, please visit confluence, there’s a ton of useful information you might find useful.  


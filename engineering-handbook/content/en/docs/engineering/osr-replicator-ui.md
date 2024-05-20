---
title: "OSR Replicator Front-end"
linkTitle: "OSR Replicator Front-end"
date: 2022-01-13
weight: 5
description: >
---
## Authorization/Login/Logout
---
The authorization mechanism has been implemented in accordance with OAuth standard, including:
* *Full-fledged Login page*
* *Securing all functional endpoints*
* *FormData exchange*

Also, we utilize both **cookie-** and **header-based** authorization:

* **Header** authorization frequently is using for testing purposes.  
* **Cookie** authorization is the main flow used for both internal and external API calls.  

In our case cookies are httpOnly. Hence, 
Cookies are not accessible by JavaScript (they are set up by the server, and are sent with every client request)
When writing code with using some endpoints, developer doesn't care about authorization in code. All is handled by browser

OSR UI has auto-logout mechanism. When auth token is expired, the user is redirected to the login page automatically. Token is valid for 30 minutes. 
After that all tries to get pages directly will fail, until the user logs back in.

Login page lives here (indicated the pattern):  
`https://osr-emu-{location}-{retailer}-{env}.tom.takeoff.com/login`  
Here you can find a direct link to the vault in [1Password](https://takeoff.1password.com/vaults/details/elloy56yngy6k2jrs2yey3v5pu). 
(Remember - all takeoff employees has access to 1Password service). This vault store login/password for OSR Replicator FE.

---
## Admin page
---

On admin page you can set up the **OSR Replicator** according to your needs.  
Here is the list of settings:
##### Log Level
Depending on what amount of logging info you want to be displayed, there are several options
  * **DEBUG**
  * **INFO**
  * **CRITICAL**
  * **ERROR**
  * **WARNING**  

##### Emulate Delay 
This option helps to make orders' processing time close to "real" OSR. There are also few options:
  1. **None**. Means that all orders will be processed as soon as they are received by OSR Replicator
  2. **Medium**. Or also can be names as "slight delay". Means that all orders will be processed with minimal delay (about 1-2sec per action), to give some time Takeoff software receive responses and provide new data 
  3. **Prod**. This options emulates "real" delays that happen on the real OSR (e.g. picking time for 1 particular item can take up to 10 seconds, etc.)  

##### Shortpick and Cancelled items.
  * **Shortpick** in brief, means when you picked only some qty of items in the order. All another items you will need to pick manually. (Detailed info about shortpick implementation you can find by the [link](/docs/engineering/shortpick))  
  * **Cancelled** When this item is added to the order, this orders will be cancelled with an error. (More detailed info you can find in the *Orders* section of this file)  
These items already have predefined values, but you can choose your own depending on which items you expected in your order.
Presence of this item in the order will trigger corresponding flow of **OSR Replicator**.  

##### Mode selector. 
Here are two options:
  * **Automatic**. Means that all items in the orders, will be picked automatically.
  * **Manual**. Means that actions are needed from your side to pick items (More info you can find below, in the *Orders* section of this page).  


---
## Orders page
---
This page created specially to make it easier to test specific OSR flows and be able to control each step of OSR picking.
By default **“manual mode”** switcher **always off**, so all OSR magic works automatically (generate containers, item pick, generate file, etc).

This is useful for specific tests to check behaviour and investigate/test edge-cases.

<img src="/images/en/docs/Engineering/OSRR/OSRR1.png" width="200" height="150" />

As soon as you switch manual mode **ON** - all orders will wait for taking actions with them (either pick or cancel specific order/product).

Below Manual mode you’ll see a window with a **list of available** orders to pick.

And below that - **list** of processed orders (it will be filled during your interaction).

(Here **"Order Processed"** means that all necessary interaction with order - done.)

![STEP2](/images/en/docs/Engineering/OSRR/OSRR2.png)

So, you select order and press on **“Start WPO”** button.
On the main screen you can list of orders available to select.
Upon click on order - you can “Pick” this order and proceed with products containing in this order.
By pressing on **"Cancel"** button you initiate **Cancelled** flow (MOD 71).  

What does it mean?  
It means that is generated an error which informs that something is wrong with OSR (physically) and declines this order.

![STEP3](/images/en/docs/Engineering/OSRR/OSRR3.png)

When you pick order then you can pick/cancel a product.
Upon click on product you can see it details below on the main window.

All this changes reflected in the order details page on Tom UI (picked by OSR).


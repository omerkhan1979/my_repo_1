---
title: "Locations Redesign: Site ID"
linkTitle: "Site ID"
weight: 1
date: 2022-08-15
description: >
    *Site Identification*
---

## 1. Rebrand "mfc" to "site"

Takeoff business model has been built around concept MFC. 
MFC stands for Micro Fulfillment Center - place where fulfillment and picking happens.
Current MFC design has automatic fulfillment, manual fulfillment and sometimes in-store fulfillment capabilities.
While MFC with both manual and automatic fulfillment is most popular choice, there are possible configurations without manual or automatic option.
In order do not lock ourselves on initial MFC design, or specific MFC configuration, proposed to rename `mfc` to `site`.
Site is not too abstract term, still semantically good to describe different configurations, like MFCs, CFCs, darkstores or sites with two OSRs.

## 2. Single site-id

As we move towards Takeoff Platform, the plans to have one multitenant production environment (`prod.tom.takeoff.com`), which handles all sites across all retailers. 
Currently, we can use pair `<retailer_id, site_id>` to uniquely identify facility which handles operations. The proposed approach to replace pair with one id, which is globally unique across all retailers. We still should have the ability to retrieve `retailer_id` by `site_id`.  

Single Site ID makes usage patterns much simpler in the target multitenant architecture.

## 3. Usage of site-id

We must understand site-id usage scenarios, to be able to define identification scheme, which meets all criteria and limitations.

### 3.1 Restful API

Takeoff Restful APIs serve resources.

For example, site-id may be parent resource  
`/api/sites/${site-id}/orders/${order-id}`  

For example, site-id may be query path param  
`/decanting&site-id=${site-id}`  

...

Site-id must be URI-safe and contain only unreserved characters according to [RFC3986](https://www.ietf.org/rfc/rfc3986.txt)

### 3.2 Infrastructure

Infrastructure components contain reference to `site-id`.

For example, bifrost mfc-based components are named  
`bifrost-${site-id}`  

For example, Google Pub/Sub topics and other resource may refer to site  
`uat-inventory-snapshot-conduttore-${site-id}`

...

GCP and Kubernetes resource names are subject to limitations, e.g [Pub/Sub Resource Names](https://cloud.google.com/pubsub/docs/admin#resource_names), [Kubernetes Name constraints](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/)

### 3.3 Database

Domain entities are mapped to database tables and can have `site_id` as a column, indicate which site this entity belongs to.

```
orders
--------
order_id
site_id
items[]
...
```

...

Modern databases allow any unicode value in the text columns.

### 3.4 Application Code

Application code consist of functions, which often operates in context of site.  
Refer to site as `site-id`.  
Discouraged namings `mfc-id`, `store-id`, `location` or something else.

## 4. Requirements for site-id

- Globally unique across all retailers
- Does not contain Retailer or Site identifiable information
- Random
- URI safe

## 5. ID Scheme

```[a-z0-9]{6}```

### 5.1 Why not UUID?

There is no need to use complex random scheme like UUID.
Their primary benefit is extremely rare probability of collisions. 
However, UUID is too long for usage in URI path and may be subject for limitations, when used in name concatenations. 

### 5.2 Random Short String

Instead of UUID, proposed to use random short strings.

Each site will be automatically assigned random 6-chars alphanumeric identifier `[a-z0-9]{6}`.
Such scheme allow reference over 2 billion identifiers, relatively low probability of collisions and concise and easy to use in communications.

Few examples:

```
n4aqh5
c1pwb7
kpq3gt
k3ohjz
muyt8e
c31hsx
gfp15f
2xly96
mlo3my
4iiqfp
```

### 5.3 Code Sample

Oversimplified approach

```
var letters = []rune("abcdefghijklmnopqrstuvwxyz0123456789")

func GenerateSiteId() string {
    b := make([]rune, 6)
    for i := range b {
        b[i] = letters[rand.Intn(len(letters))]
    }
    return string(b)
}
```

### 5.4 Collisions

The main drawback using random short string scheme is a non-zero number of collisions.

#### 5.4.1 Birthday Paradox

For example, due to [Birthday Paradox](https://en.wikipedia.org/wiki/Birthday_problem)
We need roughly ~50K identifiers generated for the 2 Billion keyspace, so the collision probability for new ID becomes more than 50%.

Collision cap of 50K is enough to cover all grocery supermarkets in US.

#### 5.4.2 Collision Resolution

Collisions are not really a problem for sites. 
Sites are not created frequently and their keyspace is low.

Collision resolution strategy could be as simple as, if we have collision, regenerate id.

In case of unexpected growth of the number of site identifiers and higher rate of collisions. ID scheme may be extended to 7,8 or more characters, in safe, non-conflicting manner.

For example, using 8 characters scheme, collision cap raises from 50K to 1.5M

## 6. Open Questions?

Q: Do we need ability to regenerate ID when system generated abusive content, e.g `f*ck21`?  

Q: Do we need to have the same id for the same site on the prod and uat?  

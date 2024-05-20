---
title: "Terminology"
linkTitle: "Terminology"
weight: 8
date: 2021-11-01

description: >
   Terminology reference
---

To maintain consistency across our APIs, domains should develop terminology that
can be consistently used. For example "totes", "containers", "crates" and "cases" are
often used interchangeably. There may be subtle differences in where these terms
are used however. APIs should pick the most general applicable synonym, but
[precedent]({{< relref path="007-precedent.md" >}}) may dictate a different
choice.

To make this concrete, if you were modeling an API around dogs, you might
refer to the different kinds of dogs as "canines", "animals" or "dogs". If you
are in a scientific environment "canines" might be more appropriate than "dogs".
On the other hand, if the API only talks about dogs, it is likely "animals"
would be too generic and should be avoided.

When picking names to use in your APIs, consider these sources for anything
not covered by this guide. They're not authoritative, but useful. If you find some
additional Takeoff specific terminology, please contribute to this guide!

- [Google AIP - 2716 - Standard terms in
  names](https://github.com/aip-dev/google.aip.dev/blob/master/aip/apps/2716.md)
- [Google API Design's "standard"
  fields](https://cloud.google.com/apis/design/standard_fields)
- [Schema.org](https://schema.org)

The rest of this document contains Takeoff terminology:

1. **Retailer**

  A retailer is the organization that has a relationship with Takeoff and owns
  sites.

  Historically we would refer to retailers by code names. This should be
  discouraged in favor of the actual retailer name or their ID. Of course, for
  the purposes of integrating with legacy deployments it is required.

  During discussion you will hear people use various synonyms for retailers, including: 
  "clients", "chains", "banners", or "brands".

  When refering to a specific retailer, you may occasionally hear references to
  particular brands or banners (e.g. Jewel Osco instead of Albertsons). In
  APIs we should always refer to retailers according to the retailer ID
  specification defined by the _TO BE DEVELOPED SPECIFICATION_. For instance
  Albertsons is `WHATEVER-THEIR-VALUE-IS`. All other forms of identification
  (e.g. code names, abreviations, etc) are deprecated in APIs naming
  convnetions, including in domain names.

2. **Site**

  A site is a place where retailers are storing goods and utilize Takeoff's
  technology to prepare orders. Sites can have many different shapes and sizes.
  Some may have an OSR, some may not. Some may have manual areas, some may not.

  There are many alternative names for sites. Some are particular _kinds_ of
  sites, others are just synonyms. Here's a list of alternative names, and how
  they relate to `site`:

  - **MFC**: Micro-fulfillment Center. As the name hints it is a _small_
    footprint location, usually implied to contain an OSR. Occasionally people
    will refer to an `AMFC` - or "automated" micro-fulfillment center.
  - **Location**: A very generic term, which could mean anything! Try to remove
    it from your vocabulary to increase precision of our discussion.
  - **Facility**: This is another synonym, it doesn't seem to carry any
    additional information about the characteristics of the site.
  - **Dark store**: This is a particular kind of site that does not have an
    attached store where end-customers are shopping. Instead, associates are
    collecting orders. There is typically an implication that there is no
    OSR/automation when this term is used.
  - **Store**: Another synonym, however, this one sometimes implies that there
    is an attached grocery store where end-customers are also shopping for their
    own groceries, rather than just associates.
  - **Standalone MFC**: A refinement of MFC that indicates there is no attached
    store, making it similar to a "dark store". This usually implies there is
    an OSR/automated picking taking place at the site.
  - **MFC Code**: A specific identifier used by [Service
    Catalog](https://github.com/takeoff-com/service-catalog).
  - **Retailer Code**: A specific identifier used by retailers to refer to the
    site, usually while placing orders through
    [RINT](https://github.com/takeoff-com/integration).
  - And several more 

  When referring to a site in API definitions, use the Site ID as defined by _TO BE DEVELOPED
  SPECIFICATION_. For example, the site historically refered to via MFC code
  ABS3116 should be referenced as _WHATEVER THAT VALUE IS_. All other forms of
  identification (e.g. retailer codes, mfc code, etc) are considered deprecated.

3. **Tote**

  A tote is a container for products. The standard language used by most Takeoff employees
  seems to have settled on `tote`, but sometimes you may still encounter
  references to as "cases", "crates", "containers" and "boxes".

  There are two sub-variants that may be applicable depending on your context:

  1. Target tote: A tote that products are placed into for assembling a customer
     order. There are several kinds of target totes.

  2. Source tote: A tote that products are taken from while assembling a
     customer order.



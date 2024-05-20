---
title: "OSR Short-pick"
linkTitle: "OSR Flow: Shortpick"
date: 2022-07-21
weight: 5
description: >
---


*Before learning about shortpick you might want to check our [OSR Replicator Onboarding](/docs/engineering/osr-replicator/).*

One of the main flows in KNAPP OSR machine is picking: consolidation of item’s into client’s order from OSR containers into a target tote for following dispatch. In most cases, the requested quantity matches whatever is currently present in OSR, however there are exceptions. 

Imagine a case with a fragile cargo, which was either damaged or rendered unusable. Whether it happened while being stored in OSR or during decanting/picking transportation, once the container with the item reaches picking station it becomes apparent that employee can not add enough of this item in order to fulfill the order. Such a situation is called **short-pick,** i.e. picking of an item insufficient in quantity. 

A KNAPP solution to such a situation is expressed by looking for another container with this item until there is enough. However, if there are no more containers which can fill in the gaps, a MOD 69 event is generated which flags this item in the order for having a quantity discrepancy and the picking of other items continues. 

Taking inspiration from the KNAPP, similar functionality has been added to the OSR replicator. Although, we do not go in depth with covering search-in-other-containers cycle, upon encountering a MOD 69 item, problematic item is transferred to the manual picking queue for further order consolidation and dispatch. 

In case your goal is to simulate an erroneous item, an id-specific trigger was built into the replicator: 88005553535. Once item with such an ID has been detected in the replicator, the shortpick chain is involved: a MOD 69 workstep along with further transfer of this item to a manual picking queue.
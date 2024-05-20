---
date: 2021-06-22
title: "Being on-site is a hard job"
linkTitle: "Being on-site is a hard job"
description: "We are not a fulfillment service. We are a productivity for people."
author: Vladimir Filonov
resources:
- src: "**.{png,jpg}"
  title: "Image #:counter"
  params:
    byline: "Photo: Vladimir Filonov"
---

Being on-site is a hard job. Tight timeframes, freezing air, totes everywhere. Pain in hands and back. Just imagine - you have 1 hour to fulfill hundreds of orders with thousand of lines. And suddenly, everything stuck. Totes are not moving or ride in circles, the scanner is beeping, but nothing happens, the printer does not give you any label, or you need to run between dispatch ramps to find where all totes of the order are.

Yes, during sev1s, we often need to wake up at night, get through tons of logs and make stressful investigations through unknowns. But let’s be honest - we are doing this in a comfortable chair, with a cup of coffee and a blanket if it’s chilly. And when the system is restored, we can go back to sleep. People on site have no such possibility. After sev1, they have dozens if not hundreds of delayed orders to process, heaps of totes with no labels, and the next wave coming. Hour of sev1 can cost them several hours extra work.

But not only sev1s are painful. For us, a lot of issues look insignificant. “No address” at a Pickerman during manual picking? Not a big deal - a picker can still find the item on the dynamic shelf and scan it. A preliminary picklist was not generated? Not a big deal - we have deltas. Orders were not split due to item master lag? Not a big deal - support can split orders manually later.

Just remember how you react when Facebook or Instagram is freezing up, losing your photo, or just crashing. Annoying, right?

Our small issues are a big deal on-site. Each small problem is multiplied by a number of orders, lines, waves. Loss of a single minute during order picking turns into hours. People require to stay longer, take additional shifts, do extra work.

We are creating tickets, writing code, deploying, debugging. We see pull requests, endpoints, payloads, and logs. Unfortunately, quite often, we are losing people behind all of that. People who are working with our solution. People who are frustrating and overworking because of our issues. People who We can make happier at work.

We are not a fulfillment service. We are a productivity for people.

---

PS: I’ve tried to illustrate the complexity and complication of the process on-site =)

{{< imgproc mfc Fill "900x500" >}}
A Micro-Fulfillment world.
{{< /imgproc >}}


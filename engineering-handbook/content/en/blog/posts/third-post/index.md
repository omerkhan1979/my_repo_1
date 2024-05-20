---

# (@formatter:off)
date: 2021-11-29
title: "Your application will fail"
linkTitle: "Your application will fail"
description: "Plan for _when_ your application fails."
author: Dave Mancinelli
# (@formatter:on)
---

A year of development, months of "dark mode" logging, custom behavior-driven testing infrastructure,
deployment and rollback Confluence pages... Fulfillment Orchestrator was finally ready to be
unleashed on the world! After smooth rollouts to two clients and almost two full weeks in
production, everything seemed great. And then disaster struck. A certain type of edge-case order
caused severity 1 issues on two consecutive days. So with all the effort and attention placed on
quality, where did we fall short and what can we learn to prevent this in future rollouts?

---

### 1. Assume your application _will_ fail

Many experienced developers put their hearts and souls and keyboard clicks into making sure every
feature, edge case, and line of code were covered. It wasn't enough, and it never will be. Mind you,
I'm not advocating against testing - quite the contrary - but realize that you will never test every
possible permutation of pathways through your code or data that might be thrown at it. **At some
point, it will fail.**

### 2. Prioritize identifying failure

Orchestrator had been running in the background on production for months, just logging everything it
would be doing when handed the reins. While that was happening, the team was busy adding and
tightening up features for the initial launch. We had ample logging and great dashboards, but they
were noisy, difficult to spot real points of failure, and required someone to go looking for
exceptions. We assumed that because we had logging in place and the application wasn't failing that
everything was cool. We made tech debt items to clean up logs and create automated alerting, but
they took a back seat to the features in the product. In reality, prioritizing this "tech debt"
would likely have saved us from two sev 1's. **Prioritize being alerted to any type of issue before
going to production.**

### 3. Prioritize addressing _business_ failure

I was at the park with my two-year-old when I got the OpsGenie alert saying that an entire wave of
morning orders had failed. I rushed home with my AirPods in trying to help support debug, which as
you can imagine was not easy. The only thing I could really tell them was "let me get home and check
our logs and database." When I did get to my computer, it took two team members over an hour to
fully identify the issue and figure out how to resolve it. The next night, a similar order caused a
similar problem, and we were stuck trying to recreate pub-sub messages on the fly. So how do we do
better? Following the advice in #1, we've taken a step back to:

* Brainstorm all the business cases that could fail...
    * Not the code paths or the causes - you can't predict these.
    * Identify the boundaries where the application changes or interacts with the flow of an order.
    * Involve support and other stakeholders.
    * _Example:_ Orchestrator fails to save orders that were split.

* Assume each boundary point will fail and determine how to identify it...
    * In what state is the order left in within the whole system?
    * Will the team and/or support have the tools and knowledge to identify this state without
      digging through esoteric logs or directly connecting to a database?
    * _Example:_ The orders look split and reserved and are in "queued" status, but they have not
      been sent for fulfillment. Support should be able to query the Orchestrator API for those
      orders and determine if they exist or not.

* Given each failure state, determine a process for unblocking or correcting order flow...
    * The team and/or support will need to adapt to a failure in your code. Identify the tools you
      will need to manually intervene and unblock the business process.
    * _Example:_ Support should be able to query Orchestrator for the failed split message, ideally
      with a clear explanation of the failure. If the failure can be addressed, they should be able
      to reformat the orders and send them to Orchestrator through an API to unblock fulfillment.

---

Your application _will_ fail -- and that's ok. When it does, have the tools in place to identify and
fix the failures quickly.

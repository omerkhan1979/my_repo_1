---

# (@formatter:off)
date: 2022-08-08
title: "Your application will fail - part 2"
linkTitle: "Your application will fail - part 2"
description: "Give your system a way to try again."
author: Neil Dowgun
# (@formatter:on)
---

[A year ago](https://engineering-handbook.takeofftech.org/blog/2021/11/29/your-application-will-fail/) we conceded that none of our systems are perfect: they will fail, and we should be planning for failure. It is important to alert someone who can help when a failure happens and needs to be fixed, and to give them a tools to fix the *business* failure, at least.

It's not easy though.! Even with a focus on planning for failure, we continued to occaisionally end up in completely unforseen, unrecoverable states in production. The circumstances may be rare, and at least we were alerted when the issues occurred, but anyone who has been part of the Outbound domain at some point in time - whether that is working with the couch watcher-based Platform, OMS’s split functionality, or the latest batch of Event-based service communication - knows that a large portion of the fallout work seems to be in recovering or guarding against the <1% of cases where an order gets stuck in a bad state. Can we protect against the unknown? We’ve learned a lot through experience, so in this article let’s see if we can design a system that can always be returned to a working state.

Problems we’ve seen lead to inconsistent state:

- DB state that is changed by one process while we’re in the middle of another process

- Events that get published before DB state is updated

- Events that never get published due to connectivity issues

- Events or Requests that never get processed due to connectivity issues

- DB rollbacks that fail because of connectivity issues

Goals:

- Entities should not end up in a “bad” state except due to connectivity issues (which cannot be helped)

- A layman should be able to manually “fix” an entity in any possible “bad” state

- As much as possible, the system should be self-healing. It should fix bad states itself with automatic retries

---

# Background

## (Epic) Sagas

All of the problems mentioned above come from mistakes we’ve made while trying to implement the Saga Pattern. [This article from microservices.io](https://microservices.io/patterns/data/saga.html) is a nice, succinct walkthrough of what that is. We will use it as an example, so go ahead and read the whole thing. Simply put: “How can you implement transactions that span multiple services?” Or perhaps more particularly, multiple data stores, since even one service could be using more than one store. The simple answer is: you can’t, at least not as an [Atomic transaction](https://en.wikipedia.org/wiki/Atomicity_(database_systems)) that guarantees the system state will either be in a pre-transaction or post-transaction state at all times. 

In the [microservices.io example](
https://microservices.io/patterns/data/saga.html), we are trying to place an Order in an Order Service, but we need to ask the Customer Service to reserve credit for us first (helpfully, it sounds a lot like OMS asking IMS to reserve inventory during split!). The pre-transaction state is no order exists. The post-transaction state is an order exists in Approved status AND credit is reserved. To make it look more transactional, the author has started the Order in a “Pending” state before credit has been reserved, meaning it probably won’t show up in most queries. 

BUT, suppose a failure happens somewhere along the way, such that credit is reserved but the Order service is unable to get a database connection to update the status from Pending to Approved. Now we are in a “bad” intermediate state, where credit is reserved in the Customer service for an Order that does not officially exist. We could try to back out of it by asking the Customer service to release the reservation, but what if we’ve lost connectivity too? The two-party transaction can never be strictly Atomic when **transient failures** may occur, so there will always be some way for your system to fall into an **intermediate state**.

## Event Sourcing

One way to solve this problem is with [Event Sourcing](https://microservices.io/patterns/data/event-sourcing.html) (you can see the intro paragraph to that article is describing the same exact problem of transient failures that we were just covering). Basically, the “save updated state into database” and “notify other systems” effects are unified into one datastore, which looks like a stream of Events. It doesn’t actually get rid of the intermediate state (where an order exists but credit is not reserved); instead it makes them more formal and guarantees that all parts of the system know about that intermediate state.

There are a few big drawbacks to Event Sourcing, mainly that you need every service involved to agree on this pattern and use the same data store, so their implementations are quite coupled together. In many cases we are trying to only refactor one part of our system at a time, so let's look at what we can do while still keeping services somewhat isolated.

## Transactional Outbox

A less daunting way of getting an outcome similar to Event Sourcing is to use a [Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html). This can be localized to whatever service you are working on. It just means you save the db updates and Events you need to publish *into the same data store in an atomic transaction*, and then have a plan for publishing the Events to an external Message Broker later. This is a solid pattern that you are welcome to adopt for your service, and in some cases it may be the simplest, most efficient way to meet the goal of always being able to recover.

The caveats here are:

- you have to add some extra tables and extra infrastructure to make sure the messages get published.

- it forces you to communicate asynchronously, usually using Choreography, which may mean significantly refactoring all services involved.

## Orchestration and Choreography

What did I mean by "Choreography"? Orchestration and Choreography are the two ways of coordinating work between services.

| Orchestration | Choreography |
|---------------|--------------|
| Service A tells Service B what to do. | Service A publishes a record of what it did. Service B interprets what it is supposed to do. |
| Service A knows about Service B and its API schema. | Service A and B are decoupled, but both agree on an Event schema. |
| Service A can get a response from Service B synchronously (but doesn’t have to). | Nothing is synchronous. |

When you choose Choreography, the basic tradeoff is you get to decouple your services by introducing some complexity. Let’s revisit the [Saga example](https://microservices.io/patterns/data/saga.html), where options for both Orchestration and Choreography are laid out. 

In this case, the Order system needs a response from the Customer system, so you could argue it already needs to know about it and therefore they are closely coupled. If you used Orchestration, you could actually call the Customer system synchronously and have one pretty simple “order creation” process (until it gets thrown off by transient failures).

If you use Choreography (or even asynchronous Orchestration), what you thought of as one Saga becomes three processes: 

- Creating a pending order

- Reserving credit for an order

- Approving or Rejecting a pending order

It’s more complex! But what really makes it easy to choose is if you have more than two services involved. If you have N services involved in the Saga, and each one has to do something in series, then Choreography would make you define separate Events for every single step. If you use synchronous Orchestration it’s all managed by one process.

*However*, as N grows, the process will run longer and longer, and the chances you hit a failure in the chain grow. If it is all happening in one process you may need to rerun the whole thing. If you have N services involved in the Saga and they can work *in parallel* (or you don’t need responses from them at all), then it is much simpler to publish one Event. All the other services can subscribe to it and notify the original service when their part of the work is done.

Note:  You can also mix the approaches within one process! You can use Orchestration for a couple of steps that need to be done in series, and then use Choreography to fan out to several independent processes. But doing this still makes it hard to use Transactional Outbox, which is not meant to have any synchronous steps besides the db transaction.

---

# Proposal

So both Orchestration and Choreography have their place, and if you are willing to go all-in on Choreography you can start building Transactional Outboxes. However, if we want to use a mix of patterns in our services (and without an enormous refactor, we do), there is a rule we could apply that would solve almost all of the cases where transient failures put us in unrecoverable states: **make every Saga Retriable**.

## What is Retriable?

Did I just make up a word? Maybe, not *all* dictionaries seem to have it. What I’m talking about is similar to Idempotence, but not quite the same. Idempotence would be:

- Define “f” as a function that takes an input (X) and an initial state (S0), and returns outputs (Y) and a modified state (S1).

- IF `f(X, S0) -> (Y, S1)`, THEN `f(X, S1) -> (Y, S1)`

- Thus, if you start with an initial input and state, no matter how many times you run the function on the updated state it will end with the same outputs and final state.

We can’t exactly guarantee Idempotence in a world of transient failures, so let’s define a Retriable Function/Saga:

- IF the outcome of `f(X, S0)` is EITHER `(Y, S1)` OR any number of *transient failure* states `(Y', S')`.

- THEN `f(X, S1) -> (Y, S1)` OR `(Y', S1)`

- AND `f(X, S') -> (Y, S1)` OR `(Y', S')` for all `S'`

- Thus, if you start with an initial input and state, if you run it enough times that the function outputs the final state, all subsequent runs will leave the state unchanged.

- Also, if the function returns a final output Y, you know the system is also in final state S1 (so you can stop retrying).

Thus, you can think of a Retriable Saga as one that, when wrapped in a Retry Mechanism with sufficient retries, acts as an Idempotent function. 

## Retry Mechanisms

A Retry Mechanism would be anything that acts like so:

```
attempts = 0
while (attempts < maxAttempts) {
  var y = f(x)
  if isFinal(y) return y
  attempts++
}
```

Google has been building out lots of tools for asynchronous coordination that have built-in Retry Mechanisms, like  Pubsub, Cloud Tasks, and Cloud Workflows. Other things that qualify are plain old While loops in the calling code, or a sufficiently dedicated human being. 

Scheduled jobs can also work, but since they do not take inputs or return outputs, you can think of them using the modified state from the previous run as the input for the next run. While jobs will not run out of retries, making sure you save enough state to also act as the inputs to the next run can involve lots of extra work, and the latency between each retry may be much higher than other mechanisms.

### Retriable APIs

Unfortunately, most of these automated Retry Mechanism are not foolproof. Sooner or later you will hit a connectivity issue so egregious that the automated mechanism will give up. And then you will need an API (ideally wrapped in a UI or CLI, for user-friendliness) to manually retry your Saga (or restart the Retry Mechanism). Therefore, point two of this proposal is: **wrap every Saga in an Retriable API**. 

Once you do this, the mechanism that is used to call your Saga becomes largely irrelevant! An API that starts out as a backing for a UI could one day be automatically called by a scheduled job. An effect that you are triggering off a pubsub event could be moved into a Cloud Workflow instead, etc. 

---

# How

So how do we make every API and Saga underneath it Retriable? It must be trickier than it seems at first, or else we would have cracked it long ago. 

Fortunately, the good news is that once you start building Retriable blocks it should get easier. If a Saga is a series of steps that affect the overall system state, then all we need for a Saga to be Retriable is for each of the steps to be Retriable itself.  Let’s start by breaking down the most common types of steps. 

## Synchronous Steps

A synchronous step should be used if you cannot proceed with your Saga until you know the outcome of this step. If a synchronous step hits a transient failure you want your Saga to just return a transient failure as output. That way the Retry Mechanism running the Saga will handle retries.

### DB Update

Any updates to the DB done in one DB Transaction may be considered a single step. The good news is that these transactions already have ways of telling us whether they hit transient failure: almost every error you hit while trying to commit a transaction should be considered transient. 

The bad news is that certain DB behaviors are not Retriable out of the box. For example, an insert into a table with a unique constraint. You cannot run that twice: the second time it will throw an error. So to make your step Retriable you either need to catch that error and ignore it, or proactively check whether the row has already been inserted and skip the insert if it has.

### Synchronous API Call

With API calls, it is important that the caller understand what is a “final” vs “transient” response. Anything is ok as long as the caller and callee agree, but broadly speaking, any code from 200-499 usually indicates a final acceptance or rejection of the input, while 5xx would indicate a transient failure.

If you want, your Saga can wrap the API call in a while loop for another layer of retries on that particular step, but if the while loop exhausts its attempts and is still getting a transient failure then the step as a whole has experience a transient failure.

## Asynchronous Steps

Asynchronous steps are preferable if your Saga should be allowed to “complete” as long as processes have been scheduled in other services and you do not need to wait around for them to finish. Just the creation of the Cloud Task or Pubsub Message should be considered a “final” state for these steps, and the retrying is left up to those delivery mechanisms.

However, remember that the scheduling/publishing of the Retry Mechanism can fail too! The middlemen are also external services to your Saga. One real-world mistake we made was not waiting for the “future” returned by the Pubsub library when publishing: you need to wait to see if that succeeds. So in that way, even asynchronous steps are synchronous, and you may treat communicating with Pubsub or Cloud Tasks as a synchronous API call, with transient failures being passed up.

### Asynchronous API Call

This would be an API call scheduled for later with Cloud Tasks or the like. As with synchronous API calls, it is important that response codes indicate if API hit a transient failure. In this case, you will not have leeway to customize your handling of different response codes though, as the 3rd-party delivery mechanism usually has its own rules for what causes a retry vs what doesn’t. Check those before using this method, as you may need to change the behavior of the API being called.

### Pubsub Message

Pubsub messages have a simple interface for deciding whether to retry: the subscriber can either “ack” or “nack” the message, and it will retry on a “nack”. If using a Push Subscription, this actually turns into API call, and certain response codes will be considered “ack” or “nack”.

Now, if we want all of our Sagas to be wrapped in APIs that could be called by a human, they should be generally RESTful and should look like a command to modify some resource(s) in the service. The pubsub event is not that. Therefore the subscriber is usually an interpreter that takes an event centered around one resource and turns it into a command for another resource. You can use this interpreter layer to also map the response codes of the API to “ack” or “nack” codes, if necessary.

### Logging

Whether it is actually async or not, logging is usually treated as a “fire-and-forget” step, which we are ok with doing twice. The only rule here is you want to make sure the step you are documenting actually finished before logging it. So logging should go outside of db transactions, etc.

## Wrapping in an API

As you can tell from the Retry Mechanism code snippet, our APIs (and the underlying Sagas) will need to have some properties that are not guaranteed for all RESTful APIs:

- their output must indicate whether they reached a final or intermediate state.

- the output must encompass all state affected by the Saga, not just the resource indicated in the API.

    - If Pubsub Events or Cloud Tasks are supposed to be created when a resources is created/updated, then the API should not return a final successful code unless it created all of those.

    - If the system is in a state that could be intermediate - such as if you know the resource was created, but can’t prove the Pubsub Events have been published - then the Saga must retry the steps that may or may not have been applied before. Having duplicate Cloud Tasks and Pubsub Messages is considered fine as long as the downstream handlers are idempotent themselves.

The most difficult challenges arise with the REST endpoints that are not traditionally idempotent: POST and PATCH. Even a simple resource creation that fires off one pubsub message is tricky. What do you return if the message publishing fails? By our rules, you should return a code that indicates a transient failure, like 500, but that is a bit misleading if the resource has actually been created in the db and is accessible through GET calls. And if the creation actually succeeds, what do you do if the API is called again? Here are some tips/thoughts:

- Document the behavior of your API endpoint as much as possible.

- This is a case where Transactional Outbox is really helpful, as it guarantees an atomic transaction that includes both the resource creation and the scheduling of the message.

- Be clear about whether your Create operation is really an “Upsert” or a “Create unless you already have this resource”. We have several real examples where one system that owns a resource (OMS has Order, Orchestrator has Work Task) emits a “resource created” event, which cause downstream systems (Order → Orchestrator, Work Task → ROT) to copy the resources into their local store and then act upon it. These are clearly “Create unless you already have this resource” events, as if the resource was updated we would expect a different type of event.

- If possible, have the system that decides that a new resource is needed (usually the caller) generate a unique identifier for it. This can be implicit (like if there is a constraint that there is only one Foo per Bar, then saying make me a new Foo for Bar X uses Bar X’s unique identifier) or explicit (like the order-id passed into our system from retailers).

- If there are resources that truly do not have a unique identifier themselves, maybe they are actually part of a collection of a larger resource, which should only be modified as a whole.

- Once more, document what behavior you chose for the API!

## Testing

Most developers do put some thought into testing that their Sagas do the right thing when an inner call fails, but it can be hard to stay diligent and test every possible failure case. This actually becomes a bit easier if you don't have to verify what the state is after the *failure*, but that the state is correct if one runs fails and *then another succeeds*, which is all we're trying to guarantee.

Assuming you are using an architecture where your external dependencies (DB, Pubsub, other APIs) are injected into your core business logic and you are able to mock them, then you can make sure your use case is Retriable with a test like so (actual structure will depend greatly on your language):

```
for method in mockDependency.methods {
    ... set up test state ...
    with mockDependency.failOnMethod( method ) {
        result = callSaga( mockDependency )
        ... assert result is a Retriable error ...
    }
    with mockDependency.succeedOnAllMethods() {
        result = callSaga( mockDependency )
        ... assert result is Success ...
    }
    ... assert desired final state ...
}
```

[An example](https://github.com/takeoff-com/fulfillment-orchestrator-fn/blob/bdc6342360175aee9cf20e24514b3622f9d79055/business/use_cases/dispatch_manual_work_task_test.go#L295)

## Tools for Communication

Here is a brief rundown of some pros/cons of some of the "Retry Mechanism" tools at our disposal.

### Cloud Pubsub

- Used for Choreography. As stated before, choreography allows you to decouple services and reduce the number of steps in the Saga itself, as long as the effects of those steps are independent.

- Runs globally, so your caller does not need to worry about routing.

- Lacks visibility into individual messages flowing through it (especially for Push Subscriptions), mostly you can just see graphs of how long messages have been waiting.

### Cloud Tasks

- Used for asynchronous Orchestration, where you don’t care about the outcome of a step but also find it easier for the Saga to know exactly what it is calling rather than using Pubsub.

- Requires less infrastructure than Pubsub, as in both cases the consumer should really have a RESTful API to handle its actual effects. Using Cloud Tasks only needs that API and a Task Queue, while the Pubsub needs a Topic, a Subscription, and something to translate the Event into the payload of the RESTful API.

- A UI for monitoring the Task Queue. Unlike Pubsub you can see specific in-flight tasks.

- More control over rate-limiting the delivery of Tasks.

- Option for scheduled (non-immediate) delivery.

- Tasks are automatically deduped, so if you end up in a situation where you have to retry the creation of the Cloud Task over and over at least some of them will probably be deduped and will cut down on unnecessary processing.

- However, Cloud Task Queues are regional, so you need to know not only the final API you want to hit but what region you are in. 

### Scheduled Jobs

Unlike Cloud Tasks or Pubsub, a scheduled job may never run out of retries. That is its main benefit, but the drawback is that you need a way to determine what the outcome of the last run was in a custom way. In some cases this is trivial, if the last Effect in your Process is to save some state into the local database that you can check later. However, if you consider a complex Saga like Order Split (which currently uses a scheduler) we touch several other systems after the last database save, so it is not easy for the job to tell whether those steps finished.

### Cloud Workflows

What if I need to use the Orchestration approach because my individual steps have to be done in a particular order, but the steps may be long-running or otherwise expensive to retry? Well that is where GCP Workflows might help.

A series of effects that is being orchestrated by a Workflow does not have to finish in a short amount of time like something that is processing a pubsub message or Cloud Task. Effectively, the Workflow is better at keeping track of its progress so you do not have to redo effect A if effect B fails, you can just retry effect B.

However keep in mind:

- Your individual steps still need to be idempotent.

- You *definitely* still need to be ok with the intermediate states between the steps, as they may last a long time.

- It’s unclear how to test the workflow as a whole, since it is written in yaml, not code you can run locally.

- Workflows cost more money. 

    - You should estimate how often each use case would be invoked. The pricing is 5,000 steps free per month, then $0.01 per 1,000 steps. For Order Split, we could probably break it into a Workflow with ~10 steps. Given something like 200,000 orders per month (across all clients) that need to be split, that is 2 million steps and ~$20,000 per month just for one workflow.

---

# Summary

- Atomicity across more than one data store is impossible. Accept that you will sometimes be in an intermediate state, temporarily. Don’t bother trying to rollback to keep two systems in lock-step.

- Design Sagas that are Retriable, and test that they are.

- Wrap your Sagas in APIs that distinguish final states from transient states.

- Make use of async Retry Mechanisms so the success of a high-level Process can be decoupled from the success of all the Effects it triggers. 

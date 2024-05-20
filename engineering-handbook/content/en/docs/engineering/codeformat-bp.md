---
title: "Best Practices - Code Formatting"
linkTitle: "Code Formatting"
date: 2017-07-13
weight: 9
description: >
  Best Practices - creating, maintaining, auditing services 
---

{{% pageinfo %}}
This page needs some more content! You can help us grow the handbook by [contributing to this page](https://github.com/takeoff-com/engineering-handbook/issues).
{{% /pageinfo %}}

## Best Practices - Code Formatting

placeholder language

- best approaches of creating, maintaining and auditing several services interconnections

- basic acceptance criteria are met, like sensitive info is filtered from logs, all connections are encrypted, proper labels are set, etc etc

- the list list of patterns. Examples:

- Use cloud function tied to pubsub to process events as the come

- Use cloud function tied to http to make an API exposed for real time usage

Use API gateway to manage routing

Use this kind of auth scheme for internal and this other for external

Use these compute resources for things in warehouse these others for things in cloud

Prefer async when possible

All of these things come with the details of how takeoff does it and where to find examples and why we choose this way

There should be little to no overlap in approaches when someone has a question they should have relatively few possible answers (you can use x y or z! developers choice! have a stance and make it clear)"
Strong guidance on what we should and shouldn't do from a tech POV. What tool should we use? What language should we use? How should we design endpoints? etc.
techy explanation why we use such tools, frameworks and libraries. set of  "hello world" samples using the frameworks. Dictionary of domain terms like "cut-off time", "pickpath generation" and etc and samples of code/autotest how to run them.
N.A
"What company thinks is a best practice we have to use. Get structured of what we have already.

Could be also:
How to establish communication between services
How to prepare architect proposal
How to make and validate arch decisions




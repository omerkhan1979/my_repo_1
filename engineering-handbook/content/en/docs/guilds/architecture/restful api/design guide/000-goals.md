---
title: "Why do we need an API Design Guide?"
linkTitle: Purpose & Goals
weight: 1
date: 2021-09-10
---

This guide exists to help teams build APIs that look and feel cohesive as well
as avoid some repeated mistakes. Think of it like you would mock-up for a
library of UI widgets. Just like the design team aims to standardize widget
across pages, API policies aim to make consistency between resources in our
APIs.

The policies in this guide range from low level things like how dates should be
represented, urls composed, or which verbs are supported to higher level
concepts such as who reviews changes to API specifications.

API Design has other similarities to UI design. For instance, you are not very
likely to start building backend functionality until you know how it's presented.
The way information is consumed, either by UI or API, is a critical component in
the design of backing systems.

{{% alert %}}
In this guide, all APIs are RESTful HTTP APIs, in particular focusing on
[OpenAPI](https://www.openapis.org/). In the future it may be adapted to other
protocols such as gRPC.
{{% /alert %}}

Throughout the guide we make extensive use of
[RFC-2119](https://datatracker.ietf.org/doc/html/rfc2119) which defines words
like “**SHOULD**” and “**MUST**.” **MUST** indicates that you have no choice but
to adopt a certain concept while **SHOULD** indicates that you are recommended
to use the given approach, but have some flexibility if it doesn’t fit your
need.

This content is derived from [https://google.aip.dev/](https://google.aip.dev/1)
and will often link directly back to Google’s own policies. When you find
something that is undocumented here, consider searching the AIP site for a guide
on how to proceed.

## Getting started

This guide is split up into several pages. It may be possible to find what you
need by skimming titles or searching. We have tried to order the content in a
way that would make it consumable "from start to finish" but do not expect anyone
to actually attempt that.

The pages will try to cross-link between related concepts so that you don't have
to remember everything from every other page.



---
title: Testing
linkTitle: Testing
weight: 9
date: 2021-09-10
description: >
  Special considerations for testing your API code

---

Your software, and by extension APIs, must be tested.

It is common for us to do unit tests for handling functions, but often there is
other configuration and state that your API includes that should be tracked for
breaking changes.

For example: you might write some code to document an endpoint like this example
from `OpsAPI`:

```
    @restricted_endpoint_params(
        path_parameters=[ORDER_SECRET],
        output_objects=((201,
                         "Order Label successfully printed.",
                         serializers.ZPLPrintResult()),),
        permission='can_print')
    @detail_route(methods=["post"])
    def print_pick_stage_labels(self, request: HttpRequest, *args, **kwargs) -> Response:
        ... code here
```

To simply call `print_pick_stage_labels` in a unit test is insufficient:

1. The endpoint documents required permissions. What happens if you call it
   without those permissions? Your testing should include validating access
   constraints as they can change and should be re-enforced with tests.
2. The response needs to be serializable with the `ZPLPrintResult` object,
   presumably any unit tests would validate that responses are compatible with
   it.
3. There is routing logic built in to the `path_parameters`, you will want to
   make sure your tests validate that the paths you expect work with the code
   you've written.

You should write tests that exercise your API configuration, in addition to the
business logic that enables the API.

Once you get past these "internal" concerns around covering your API
configuration, you should start thinking about external factors. Even though
[versioning]({{< relref path="./006-versioning.md" >}}) advises teams to make
sure their API clients only validate the parts of an API payload they consume,
it is sometimes tricky to get that "right." As a result, having an ability to
specify some shared examples can help you build a [Contract
Test](https://martinfowler.com/bliki/ContractTest.html) scheme.
[Pactflow](https://pactflow.io/) is one tool that can be used to help share
contracts between API services and consumers.

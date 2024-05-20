---
title: "Test Creation Mindset"
linkTitle: "Test Creation Mindset"
weight: 1
description: >-
    *The test case implementation approach*
---

As the Engineering organization has gone through the process of [Own Our Code"](https://takeofftech.atlassian.net/browse/TIP-52), the same should be said for the test cases create. We should not rely on existing data or features, etc. We should treat the environment like a clean state since the engineering organization is shifting to use of [ODE](/docs/guilds/architecture/on-demand-environments/), the ODE won’t be pre-populated with products, cutoffs, etc.

1. Actually follow the information in the Testrail test case.
2. Create the necessary data before in the setup
3. If the environment is not setup properly, make the necessary changes, mark the test case as skipped, OR fail the test with the reason.
4. Perform the actual test case.
5. Post test / teardown try to return the environment back to what it was before the test case was executed.

**RQT will move to test features versus cleints and TestRail will be updated accordingly as move to this initiative**

More information can be found here: [Feature Testing](https://takeofftech.atlassian.net/browse/PROD-10962)
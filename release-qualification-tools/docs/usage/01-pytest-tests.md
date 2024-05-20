Pytest Test Suite
==
[[Table of Contents](../../README.md#table-of-contents)] : [Getting Started](../../getting-started/00-getting-started.md)

## Pytest Test Suite

The Pytest Test Suite, also known as RQ or RQ Tools, is built on the [Pytest framework](https://docs.pytest.org/en/7.4.x/) and includes a comprehensive collection of tests that can be run individually or as a full suite.

:warning: Before running tests, please make sure you have reviewed [Getting Started](../../getting-started/00-getting-started.md) to make sure your environment meets the prerequisites and environment-specific setup requirements.

In order to run tests, you'll need several pieces of information:

 - **Test Mark** <code>-m</code> - This can be the full suite (<code>rq</code>), a group of tests (<code>outbound</code>), or an individual test (e.g., <code>osr_express_picking</code>).
 - **Retailer codename** and **Environment** configuration -
   - For QAI and ENVs do configure your local environment. Command: <code>export RETAILER_CONFIGURATION=abs</code> <code>export ENV=qai or uat</code> for <code>QAI</code> or <code>UAT</code> environments.
   - For ODE env do check if the configuration is part of the environment that is deployed.

 - **User Role (_Optional_)** <code>--ur</code> MFC user role with which the test is executed. e.g. `mfc-manager`, `operator`, `admin`, `retailer`, `scf-manager`, `supervisor`, `viewer`. If this argument is not passed, `operator` is the default role.
 - **Location code** (_Optional_) <code>--l</code> - Location ID of MFC location. If not set, a default location is used.          
    Defaults are: 
    abs: `0068`
    maf: `D02`
    pinemelon: `0001`
    smu: `1917`
    wings: `3435`
    winter: `WF0001`
    tienda: `414`

### Examples

| Mark | How to run                                                                      | Description |
| - |---------------------------------------------------------------------------------| - |
| rq | ```pytest -v -s -m rq --l <location-code-tom>```                                | Full suite |
| config | ```pytest -v -s -m config --l <location-code-tom>```                            | Config tests |
| inbound | ```pytest -v -s -m inbound --l <location-code-tom>```  | Inbound tests |
| outbound | ```pytest -v -s -m outbound --l <location-code-tom>``` | Outbound tests |
| smoke | ```pytest -v -s -m smoke --l <location-code-tom>```    | Smoke tests |
| isps | ```pytest -vv -s -m isps_order_flow --ur admin --l 0068```      | Isps test using admin role for Albertsons qai at site 0068 |

If you are looking for a particular test mark, those can be found in the [tests directory](https://github.com/takeoff-com/release-qualification-tools/tree/feature/PROD-12036-improve-rq-docs/tests) of this repo. 

Additional usage information can be found on the [Usage and Invocations](https://docs.pytest.org/en/6.2.x/usage.html)https://docs.pytest.org/en/6.2.x/usage.html section of the Pytest site.

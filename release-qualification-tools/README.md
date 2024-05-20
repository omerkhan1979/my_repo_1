<div id="top"></div>
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/takeoff-com/release-qualification-tools">
    <img src="/docs/images/rqt.png" alt="Logo" height=200px max-width=auto>
  </a>
  
  <h3 align="center">Release Qualification Tools</h3>
  
  <p align="center">
    This project provides tools and features for Takeoff's Release Qualification Testing
  </p>
</div>

<!-- ABOUT THE PROJECT -->

# About The Project

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

Release Qualification Testing tools and features in this repo include:
* An automated set of Pytest tests that can be executed individually, or together as a suite.
* A set of interactive scripts that can be run individually.
* A copy-config application that can be used to make one environment's service catalog similiar, if not identical, to that of another environment.
* A service that provides a series of endpoints that combine several methods which are used in release-qualification tests for other purposes, i.e. TMA testing.
* [Pytest BDD](https://github.com/takeoff-com/release-qualification-tools/blob/master/pytest_BDD/docs/README.md) and an [Environment Setup tool](https://github.com/takeoff-com/release-qualification-tools/blob/master/env_setup_tool/README.md) - these are in-progress for a forthcoming transition to a BDD-based test suite. 

* * *

## Table of Contents

 * [Quick Reference](/docs/quick-reference/00-quick-ref.md)
 * [Env Setup](/docs/getting-started/00-getting-started.md)
      * [On-Demand-Environments](/docs/getting-started/01-on-demand-envs.md)
      * [Docker](/docs/getting-started/02-docker-envs.md)
      * [Dev Environments](/docs/getting-started/03-dev-envs.md)
 * [Usage](/docs/usage/00-Usage.md) 
      * [Pytest Test Suite (RQ)](/docs/usage/01-pytest-tests.md)
      * [Scripts](/scripts/README.md)
 * [Key Classes (Wave Planner)](/docs/key-classes/00-wave-planner.md)
 * [Reporting](/docs/reporting/00-reporting.md)
     * [Publish Results to Testrail](/docs/reporting/01-testrail-reporting.md)
     * [Create Allure Reports](/docs/reporting/02-allure-reports.md)
 * [Copy Configuration](/src/copy_config/README.md)
 * [Pytest BDD](/pytest_BDD/docs/README.md) (WIP)
 * [Env Setup Tool](/env_setup_tool/README.md) (WIP)
 * [Contact](#contact)

<!-- CONTACT -->
## Contact

* [Team Chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f)
* Slack Channel: [#domain-production](https://takeofftech.slack.com/archives/C027W27MHEY)

<p align="right">(<a href="#top">back to top</a>)</p>

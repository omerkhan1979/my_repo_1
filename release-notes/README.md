This repo serves two purposes:

  

# 1. Automated Scheduled Maintenance windows for Takeoff's Statuspage

This repo is also used to automatically generate Scheduled Maintenance events in Takeoff's instance of Atlassian Statuspage [status.takeoff.com](https://status.takeoff.com/access/login), and [https://manage.statuspage.io/pages/qth8l8vxd7y4](https://manage.statuspage.io/pages/qth8l8vxd7y4). This allows us to notify our clients of upcoming deploys through the Statuspage subscriber notification features.

  

**See [/src/schedule/readme.md](https://github.com/takeoff-com/release-notes/blob/master/src/schedule/README.md) for more information about this functionality.**

  

# 2. Automated Takeoff Release Notes

This Repo is used to automatically generate release notes from several fields in Jira, and publish them to our [Zendesk Release Notes page](https://support.takeoff.com/hc/en-us/articles/4417757892753).

This project was originally tracked by [PROD-2610](https://takeofftech.atlassian.net/browse/PROD-2610) and [PROD-3496](https://takeofftech.atlassian.net/browse/PROD-3496).

  

## Automated Release Notes Background

In 2021/22, Takeoff started moving away from being client-centric, and began focusing on becoming a more product-centric, solution-oriented business. Along with that, Takeoff's Engineering team began transitioning to a ci/cd microservices-based method of creating and deploying our software.

To accomodate those changes, we stopped generating client-specific Release Notes, and introduced a single-page model in Zendesk that is more common to Cloud SaaS companies. The common example we use for this is: https://cloud.google.com/release-notes.

The details of this change are documented more extensively in Confluence [here](https://takeofftech.atlassian.net/wiki/spaces/TE/pages/3714285645/Release+Notes+Automation+Rollout) and [here](https://takeofftech.atlassian.net/wiki/spaces/TOP/blog/2022/11/08/3846668647/Release+Communications+Best+Practices+How+and+When+to+Communicate+about+Releases), and our [Engineering Handbook](https://engineering-handbook.takeofftech.org/docs/domains/production/release-notes/).

There is a one-business-day SLA for reviewing and publishing of new or updated release notes.

## Basic overview of the automation

1. [ZD_html_to_dict.yml](https://github.com/takeoff-com/release-notes/blob/master/.github/workflows/ZD_html_to_dict.yml) runs at 6 AM, 12 PM, and 6 PM (UTC) 7 days of the week.

That workflow performs several steps:

   1. It retrieves the contents of the Zendesk page and adds it to data/zendesk_data.html (for use in step 3).

   2. It then queries Jira for anything with **Release Notes Required** field value = **Yes - Ready to Publish** and adds the contents of the following fields to data/jira_data_temp.json:

      - **Release Notes Description**

      - **Fix Versions**

      - **Product Area**

1. Once the above data is retrieved, we use several scripts to compare the data from Jira and Zendesk, add or update data accordingly, and then format and output that data to `release_notes_zendesk.html`. The scripts used are:

  

   - `jira_issue.py` - Creates a list of jira entities from Jira data that can be used in `union_data.py`.

     - The data is sorted by date and grouped product area.

     - Fix Versions are parsed and the earliest one is used if there are multiple. The value is formatted as "RTww-yy" (date information is stripped), and non "RT" fix verisons are ignored.

   - `union_data.py` - Unites data from zendesk and jira, sorts it, groups by Date and issueType, and then returns that unified data.

   - `html_to_dict.py` - Creates a dictionary of jira items from html data.

   - `release_notes_builder.py` uses outputs from `html_to_dict` and `union_data.py` to generate the final release notes html file according to the format defined in the `template.html` file.

4. At that point, a Pull Request is created so that a member of @team-chamaeleon can review the updated data according to the [Release Communications Best Practices](https://takeofftech.atlassian.net/wiki/spaces/TOP/blog/2022/11/08/3846668647/Release+Communications+Best+Practices+How+and+When+to+Communicate+about+Releases)

5. When the PR is approved and merged, [send_to_zd.yml](https://github.com/takeoff-com/release-notes/blob/master/.github/workflows/send_to_zd.yml) is triggered, which uses `html_to_json.py` to transform the contents of `release_notes_zendesk.html` to json, and send it to zendesk to overwrite the previous data in the article with the latest.

  
  

## Repo How-Tos

### Review and Publish Release Notes

1. When Jira issues issues are marked as "Yes - Ready to Published," the automation will pick up the contents of the Release Notes Description field, add them to the release notes with a date stamp, and generate a PR.

2. When the PR is created, a slack message is auto-generated in the [# Domain Technical Documentation](https://takeofftech.slack.com/archives/C01HD8K8QEP) slack channel.

3. The content of the changed file in the pull request must then be reviewed for language, client-identifiable info, etc. See [Release Notes Automation Launch](https://takeofftech.atlassian.net/wiki/spaces/TE/pages/3714285645/Release+Notes+Automation+Launch) for more detail.

4. If everything looks good, the PR can be approved and merged to Master. That kicks off a final workflow that publishes the content to Zendesk.

  

#### Manually kick off a release notes run

1. "Full Workflow" [ZD_html_to_dict.yml](https://github.com/takeoff-com/release-notes/blob/master/.github/workflows/ZD_html_to_dict.yml) can be run via Workflow dispatch

2. Once the PR generated by that workflow is approved and merged, the rest of the publishing process takes place automatically via [send_to_zd.yml](https://github.com/takeoff-com/release-notes/blob/master/.github/workflows/send_to_zd.yml).

#### Modify a previously published issue

You can *update the description*, *change the date*, or *change order/location* a previously published issue.

  

**To update the description (or Product area, Fix Versions, ):**

1. Open the related Jira ticket and update the **Release Note Description** field.

2. The next time the automation runs that day, the updated description will replace the existing one. The issue will stay with the same location and date.

If the change must be made urgently, please reach out to @team-chamaeleon with the Jira number and desired date.

  

**Change the location in the Zendesk article, or date:**

1. In this repo, create a new branch and modify the html file in data > [release_notes_zendesk.html](https://github.com/takeoff-com/release-notes/blob/master/data/release_notes_zendesk.html) according to the requested changes.

2. Open Zendesk and also modify the [Release Notes article](https://takeoffhelp.zendesk.com/hc/en-us/articles/4417757892753-Takeoff-Release-Notes) accoridngly. Be sure to use the "HTML" view to preserve any tag structure.

3. Merge to Master and a workflow will be kicked off that publishes the modified content to Zendesk. The change will be preserved after that.

#### Delete a previously published issue

1. In this repo, create a new branch and delete the issue and corresponding date (if its the only issue under that date) in the html file in data > [release_notes_zendesk.html](https://github.com/takeoff-com/release-notes/blob/master/data/release_notes_zendesk.html) according to the requested changes.

2. Open Zendesk and also modify the [Release Notes article](https://takeoffhelp.zendesk.com/hc/en-us/articles/4417757892753-Takeoff-Release-Notes) accoridngly. Be sure to preserve any div tags in the html view.

3. Merge to Master and a workflow will be kicked off that publishes the modified content to Zendesk. The change will be preserved after that point.

  

## Project Structure

  

```

├── .github
├── workflows
├──ZD_html_to_dict.yml
├──ci.yml
├──pr-slack-msg.yml
├──sandbox_workflow.yml
├──send_statuspage_maint.yml
├──send_to_zd.yml
├──statuspage_maint.yml
├──success-check.yaml
├──CODEOWNERS
├── INCIDENTS
│ ├── RT02-23_incidents.yaml
│ ├── RT04-23_incidents.yaml
│ ├── RT06-23_incidents.yaml
│ ├── RT08-23_incidents.yaml
│ ├── RT10-23_incidents.yaml
│ ├── RT16-23_incidents.yaml
│ ├── RT18-23_incidents.yaml
│ └── RT48-22_incidents.yaml
├── README.md
├── data
│ ├── Statuspage_Client_Times.csv
│ ├── Window_Times.json
│ ├── release_notes_zendesk.html
│ ├── zendesk_embedded.html
│ └── temp.txt
├── pytest
│ ├── test.html
│ └── test.json
├── requirements.txt
├── src
│ ├── __init__.py
│ ├── github_data.py
│ ├── html_to_dict.py
│ ├── html_to_json.py
│ ├── html_to_json_for_validation.py
│ ├── jira_issue.py
│ ├── release_notes_builder.py
│ ├── schedule
│ │ ├── README.md
│ │ ├── __init__.py
│ │ └── statuspage.py
│ ├── template.html
│ └── union_data.py
├── takeoff-utils
└── tests
├── __init__.py
├── conftest.py
├── schedule
│ └── test_statuspage.py
├── test_jira_data.py
├── test_union_data_and_rn_builder.py
├── test_zendesk_data.py
└── tests_data
├── jira_data_temp.json
├── jira_data_temp_no_new_bugs.json
├── statuspage_incident_response.json
├── jira_json_schema.json
├── zd_html_schema.json
├── zd_json_schema.json
├── test_client_times.csv
└── zendesk_example.html


```

### Project Structure Definition

- .github/workflows
	##### Release Notes Automation
	- `ZD_html_to_dict.yml`
		- The primary workflow for this automation - gets the latest data from the Release Notes Zendesk article and validates it against an expected json schema for incoming data from the Zendesk API. It then extracts the article body as html, converts that to json, and then validates against a separate json schema. It then gets today's date, gets data from Jira and validates it against an expected json schema, and runs `release_notes_builder.py`, then creates a pull request.
	- `ci.yml`
		- Runs pytest for linting purposes.
    - `pr-slack-msg.yml` - Adds a message in `#domain-technical-documentation` in slack when a PR is generated for release notes.
	- `send_to_zd.yml`
		- Runs `html_to_json.py` to publish data to Zendesk upon approval of PR to Master.
    - `success-check.yaml` - Checks whether `ZD_html_to_dict.yml` ran successfully, and reports the results to `#domain-technical-documentation` whether successful OR unsuccessful.
	##### Statuspage Maintenance Notifications
	- `statuspage_maint.yml`
		- Creates maintenance events in Statuspage for each client`s primary Release Train deployment window.
    - /incidents/`RT-...` - these files are generated when the output of `statuspage_maint.yml` is merged. They contain the UUIDs of each scheduled maintenance event's uuid for the respective RT.
- `data`
	- `statuspage_client_times.csv` contains a list of client scheduled maintenance times and other data needed by `statuspage_maint.yml` to create scheduled maintenance in Statuspage.
	- `window_times.json` - the json output from `statuspage_maint.yml` that is used to create scheduled maintenance each RT.
	- `release_notes_zendesk.html` 
		- html template used by `release_notes_builder.py` to format data into html. 
	- `temp.txt`
		- Temp file used to to create the /data directory.
- `README.md`
	- This file.
 - `requirements.txt`
	 - Lists Python library version requirements. 
- `pyest`
	- `test.html`
		- Test html data for automated testing purposes.
	- `test.json`
		- Test json data for automated testing purposes.
- `src`
	- `\__init__.py`
		- Makes it easy for `python src/[name].py` to run, while keeping imports clean. 
	- `github_data.py` used for generating incident uuid data for `statuspage_maint.yml`
	- `html_to_dict.py`
		- Takes data from Zendesk html and stores it in a dictionary.
	- `html_to_json.py`
		- Takes data from Jira and stores it in a dictionary. 
	- `jira_issue.py`
		- Creates an internal representation of a `JiraTicket` entity, with only essential data, specific for this project.
	- `release_notes_builder.py`
		- Uses the output from `union_data.py` and `html_to_dict.py` to compile the data to output to Zendesk based on `template.html`.
	- `template.html`
		- Template for html file used by `release_notes_builder.py`.
	- `union_data.py`
		- Performs a union of the data from Zendesk, Jira, and the current datetime.
- `tests`
	- `schedule`
    	- `test_statuspage.py`
        	- Automated testing for statuspage scheduled maintenance automation.
	- `tests_data`
		- `jira_data_temp.json`
			- Json data used for automated testing purposes.
		- `zendesk_example.html`
			- Html data used for testing purposes.
	- `\__init__.py`
		- Makes it easy for `python src/[name].py` to run, while keeping imports clean. 
	- `conftest.py`
		- Used to for automated testing of release_notes_builder, html_to-dict, and union_data for testing purposes.
	- `test_jira_data.py`
		- Used for testing jira data.
	- `test_union_data_and_rn_builder.py`
		- Used for testing union_data and release_notes_builder.
	- `test_zendesk_data.py`
		- Used for testing html data from Zendesk.

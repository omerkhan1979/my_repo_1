import json
import pytest

from src import release_notes_builder, html_to_dict
from src.union_data import unite_update_jira_zendesk_data, return_jira_issues
from src.schedule.statuspage import parse_maint_file, ScheduleWindow
from src.jira_issue import JiraIssue

zendesk_html_path = "./tests/tests_data/zendesk_example.html"
jira_issues_data_path = "./tests/tests_data/jira_data_temp.json"
jira_issues_no_new_bugs_data_path = "./tests/tests_data/jira_data_temp_no_new_bugs.json"

statuspage_data_path = "./tests/tests_data/test_client_times.csv"

statuspage_response_path = "./tests/tests_data/statuspage_incident_response.json"


@pytest.fixture
def statuspage_response() -> dict:
    with open(statuspage_response_path, "r") as input:
        return json.loads(input.read())


@pytest.fixture
def union_jira_zendesk() -> dict:
    return release_notes_builder.create_union_data_from_files(
        zendesk_html_path, jira_issues_data_path
    )


@pytest.fixture
def issue_list_from_html() -> list[JiraIssue]:
    results = html_to_dict.get_issue_list(zendesk_html_path)
    return results


@pytest.fixture
def issue_list_from_json() -> list[JiraIssue]:
    return return_jira_issues(jira_issues_data_path)


@pytest.fixture
def issue_list_from_json_no_new_bugs() -> list[JiraIssue]:
    return return_jira_issues(jira_issues_no_new_bugs_data_path)


@pytest.fixture
def union_jira_zendesk_no_new_bugs() -> dict:
    return release_notes_builder.create_union_data_from_files(
        zendesk_html_path, jira_issues_no_new_bugs_data_path
    )


@pytest.fixture
def union_issues_list(
    issue_list_from_json: list[JiraIssue], issue_list_from_html: list[JiraIssue]
) -> list[JiraIssue]:
    return unite_update_jira_zendesk_data(issue_list_from_json, issue_list_from_html)


@pytest.fixture
def schedule_window_list() -> list[ScheduleWindow]:
    return parse_maint_file(statuspage_data_path)

import copy
import json
from datetime import datetime


from jira_issue import (
    transform_list_of_jsons_to_list_of_issues,
    JiraIssue,
    IssueType,
)


def data_union(zendesk_data: list, jira_data: list):
    """Unite data from zendesk and jira. Sort and group by Date and issueType. Returns united data"""

    united_list = unite_update_jira_zendesk_data(jira_data, zendesk_data)
    # group issues by date
    by_date = {}
    for item in united_list:
        date_time_obj = datetime.strptime(item.date_item, "%d %b, %Y")
        if date_time_obj in by_date:
            by_date[date_time_obj].append(item)
        else:
            by_date[date_time_obj] = [item]

    list_of_sorted_dates = sorted(by_date.keys(), reverse=True)

    output_item = {}
    for dt in list_of_sorted_dates:
        date_items = {}
        output_item[f"{dt:%d %b, %Y}"] = date_items
        bugs = []
        improvements = []
        for item in by_date[dt]:
            if item.type == IssueType.BUG:
                bugs.append(item)
            else:
                improvements.append(item)
        if len(bugs) > 0:
            date_items["Fixed Bug(s)"] = bugs
        if len(improvements) > 0:
            date_items["Improvement(s)"] = improvements
    return output_item


def unite_update_jira_zendesk_data(
    jira_data: list[JiraIssue], zendesk_data: list[JiraIssue]
) -> list[JiraIssue]:
    zendesk_map = {}
    for item in copy.deepcopy(zendesk_data):
        zendesk_map[item.key] = item

    # update item description, fix_version, and product_area or add item to map
    for item in jira_data:
        if item.key in zendesk_map:
            zendesk_map[item.key].release_notes_desc = item.release_notes_desc
            # only add it if attribute exists
            if hasattr(item, "product_area") and item.product_area != None:
                setattr(zendesk_map[item.key], "product_area", item.product_area)

            # only add fix version if zendesk doesn't have it and jira data does
            # we won't to keep the original fix_version
            if (
                hasattr(zendesk_map[item.key], "fix_version") == False
                or zendesk_map[item.key].fix_version == None
            ) and hasattr(item, "fix_version"):
                setattr(zendesk_map[item.key], "fix_version", item.fix_version)
        else:
            zendesk_map[item.key] = item
    return list(zendesk_map.values())


def _load_jira_issue_data(filepath):
    with open(filepath, "r") as input:
        string = json.loads(input.read())
        return json.dumps(string)


def _get_jira_issues_list(s: str) -> list[JiraIssue]:
    data = json.loads(s)
    i_list = data["issues"]
    return transform_list_of_jsons_to_list_of_issues(i_list)


def return_jira_issues(filepath) -> list[JiraIssue]:
    other_data = _load_jira_issue_data(filepath)
    return _get_jira_issues_list(other_data)

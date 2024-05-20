from datetime import datetime

from src.jira_issue import get_issue_by_key, JiraIssue, IssueType


def test_grouping_by_date_after_union(union_jira_zendesk):
    # check key, desc and issue type before and after union data
    dates_list = list(union_jira_zendesk.keys())
    today_date = f"{datetime.now():%d %b, %Y}"
    assert dates_list == [
        today_date,
        "04 Oct, 2022",
        "28 Sep, 2022",
        "20 Sep, 2022",
        "28 Apr, 2022",
        "21 Feb, 2022",
    ]
    assert len(union_jira_zendesk[today_date]) == 2
    assert len(union_jira_zendesk["28 Sep, 2022"]) == 2
    assert len(union_jira_zendesk["21 Feb, 2022"]) == 2
    assert len(union_jira_zendesk["28 Apr, 2022"]) == 1
    assert len(union_jira_zendesk["04 Oct, 2022"]) == 1
    assert len(union_jira_zendesk["20 Sep, 2022"]) == 1


def test_issues_data_after_union(
    issue_list_from_json, issue_list_from_html, union_issues_list
):
    # Check all items from jira are in union list, except of duplicates in jira and zendesk data (OUTBOUND-3054 & PROD-12345):
    assert (
        len(union_issues_list)
        == len(issue_list_from_json) + len(issue_list_from_html) - 3
    )

    for i in issue_list_from_json:
        if i.key == "OUTBOUND-3054" or i.key == "PROD-12345" or i.key == "PROD-6789":
            continue
        else:
            assert i in union_issues_list
            assert i == get_issue_by_key(union_issues_list, i.key)

    for i in issue_list_from_html:
        if i.key == "OUTBOUND-3054" or i.key == "PROD-12345" or i.key == "PROD-6789":
            continue
        else:
            assert i in union_issues_list
            assert i == get_issue_by_key(union_issues_list, i.key)

    assert get_issue_by_key(union_issues_list, "OUTBOUND-3054").key == "OUTBOUND-3054"
    assert get_issue_by_key(union_issues_list, "PROD-6789").key == "PROD-6789"
    assert get_issue_by_key(union_issues_list, "PROD-12345").key == "PROD-12345"


def test_issues_data_after_union_duplicates(union_issues_list):
    for i in union_issues_list:
        print(f"{i.key} -- \n {i}")
        assert i in union_issues_list
        assert i == get_issue_by_key(union_issues_list, i.key)

    assert get_issue_by_key(union_issues_list, "OUTBOUND-3054").key == "OUTBOUND-3054"
    assert get_issue_by_key(union_issues_list, "PROD-6789").key == "PROD-6789"
    assert get_issue_by_key(union_issues_list, "PROD-12345").key == "PROD-12345"


def test_description_updated_from_jira_for_existing_in_zendesk_issue(
    union_issues_list, issue_list_from_json, issue_list_from_html
):
    # In precondition files jira issue OUTBOUND-3054 had different description in zendesk and jira_data
    jira_zendesk_notes_desc: JiraIssue = get_issue_by_key(
        issue_list_from_html, "OUTBOUND-3054"
    ).release_notes_desc
    jira_json_notes_desc = get_issue_by_key(
        issue_list_from_json, "OUTBOUND-3054"
    ).release_notes_desc
    jira_after_union_notes_desc = get_issue_by_key(
        union_issues_list, "OUTBOUND-3054"
    ).release_notes_desc
    assert jira_zendesk_notes_desc != jira_after_union_notes_desc
    assert jira_json_notes_desc == jira_after_union_notes_desc


def test_fix_version_updated_from_jira_for_existing_in_zendesk_issue(
    union_issues_list, issue_list_from_json, issue_list_from_html
):
    # In precondition files jira issue OUTBOUND-3054 had different fix_version in zendesk and jira_data
    jira_zendesk_fix_version: JiraIssue = get_issue_by_key(
        issue_list_from_html, "OUTBOUND-3054"
    ).fix_version
    jira_json_fix_version = get_issue_by_key(
        issue_list_from_json, "OUTBOUND-3054"
    ).fix_version
    jira_after_union_fix_version = get_issue_by_key(
        union_issues_list, "OUTBOUND-3054"
    ).fix_version
    assert jira_zendesk_fix_version == jira_after_union_fix_version
    assert jira_json_fix_version != jira_after_union_fix_version


def test_product_area_updated_from_jira_for_existing_in_zendesk_issue(
    union_issues_list, issue_list_from_json, issue_list_from_html
):
    # In precondition files jira issue OUTBOUND-3054 had different product_area in zendesk and jira_data
    jira_zendesk_product_area: JiraIssue = get_issue_by_key(
        issue_list_from_html, "OUTBOUND-3054"
    ).product_area
    jira_json_product_area = get_issue_by_key(
        issue_list_from_json, "OUTBOUND-3054"
    ).product_area
    jira_after_union_product_area = get_issue_by_key(
        union_issues_list, "OUTBOUND-3054"
    ).product_area
    assert jira_zendesk_product_area == jira_after_union_product_area
    assert jira_json_product_area != jira_after_union_product_area


def test_issue_date_is_not_updated_if_desc_changed(
    union_issues_list, issue_list_from_html
):
    # check issue date before union and after union
    jira_date_zendesk = get_issue_by_key(
        issue_list_from_html, "OUTBOUND-3054"
    ).date_item
    jira_date_after_union = get_issue_by_key(
        union_issues_list, "OUTBOUND-3054"
    ).date_item
    assert jira_date_zendesk == jira_date_after_union


def test_new_issue_grouped_under_todays_date(union_jira_zendesk):
    # In precondition file two jira issues in jira_data_file are new, 1 issue already exist in zendesk
    today_date = f"{datetime.now():%d %b, %Y}"
    new_issues_after_union = union_jira_zendesk[today_date]["Improvement(s)"]
    issue_key_list = []
    for i in new_issues_after_union:
        issue_key_list.append(i.key)
    assert issue_key_list == [
        "INBOUND-99555",
        "OUTBOUND-3199",
        "OUTBOUND-3299",
        "INC-568",
    ]


def test_issues_grouped_under_correct_type(union_jira_zendesk, issue_list_from_json):
    today_date = f"{datetime.now():%d %b, %Y}"
    new_issues = union_jira_zendesk[today_date]
    bugs_list = []
    improvements_list = []
    for i in issue_list_from_json:
        if i.type == IssueType.BUG:
            if i.key == "OUTBOUND-3054" or i.key == "PROD-12345":
                continue
            bugs_list.append(i)
        else:
            if i.key != "PROD-6789":
                improvements_list.append(i)
    assert new_issues["Fixed Bug(s)"] == bugs_list
    assert new_issues["Improvement(s)"] == improvements_list


def test_issues_grouped_under_correct_type_no_new_bugs(
    union_jira_zendesk_no_new_bugs, issue_list_from_json_no_new_bugs
):
    today_date = f"{datetime.now():%d %b, %Y}"
    new_issues = union_jira_zendesk_no_new_bugs[today_date]
    bugs_list = []
    improvements_list = []
    for i in issue_list_from_json_no_new_bugs:
        if i.type == IssueType.BUG:
            if i.key == "OUTBOUND-3054" or i.key == "PROD-12345":
                continue
            bugs_list.append(i)
        else:
            improvements_list.append(i)
    assert hasattr(new_issues, "Fixed Bug(s)") == False
    assert new_issues["Improvement(s)"] == improvements_list

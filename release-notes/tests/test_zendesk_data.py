import pytest

from src import jira_issue


def test_issue_list_from_html(issue_list_from_html):
    assert len(issue_list_from_html) == 9


def test_issue_data_from_html(issue_list_from_html):
    assert issue_list_from_html[0].key == "OUTBOUND-3851"
    assert issue_list_from_html[0].fix_version == None
    assert issue_list_from_html[0].product_area == None
    assert (
        issue_list_from_html[0].release_notes_desc
        == "By releasing this increment in RT40-22, QC-audit printout from TOM UI will have the correct picked Zone"
    )
    assert issue_list_from_html[0].type == jira_issue.IssueType.BUG

    assert issue_list_from_html[1].key == "INBOUND-9999"
    assert issue_list_from_html[1].fix_version == "RT31-21"
    assert issue_list_from_html[1].product_area == None
    assert (
        issue_list_from_html[1].release_notes_desc
        == "INBOUND-9999 Release Notes description."
    )
    assert issue_list_from_html[1].type == jira_issue.IssueType.BUG

    assert issue_list_from_html[2].key == "OUTBOUND-1150"
    assert issue_list_from_html[2].fix_version == "RT52-22"
    assert issue_list_from_html[2].product_area == None
    assert (
        issue_list_from_html[2].release_notes_desc
        == "OUTBOUND-1150 Release Notes description."
    )
    assert issue_list_from_html[2].type == jira_issue.IssueType.IMPROVEMENT

    assert issue_list_from_html[3].key == "OUTBOUND-3054"
    assert issue_list_from_html[3].fix_version == "RT42-21"
    assert (
        issue_list_from_html[3].product_area
        == "Order Serving / Truck Loading / Truck Unloading"
    )
    assert (
        issue_list_from_html[3].release_notes_desc
        == "OUTBOUND-3054 Release Notes description."
    )
    assert issue_list_from_html[3].type == jira_issue.IssueType.BUG

    assert issue_list_from_html[4].key == "OUTBOUND-1250"
    assert issue_list_from_html[4].fix_version == "RT52-22"
    assert issue_list_from_html[4].product_area == "Order Management"
    assert (
        issue_list_from_html[4].release_notes_desc
        == "OUTBOUND-1250 Release Notes description."
    )
    assert issue_list_from_html[4].type == jira_issue.IssueType.IMPROVEMENT

    assert issue_list_from_html[5].key == "OUTBOUND-3154"
    assert issue_list_from_html[5].fix_version == "RT52-22"
    assert issue_list_from_html[5].product_area == "Dispatch"
    assert (
        issue_list_from_html[5].release_notes_desc
        == "OUTBOUND-3154 Release Notes description."
    )
    assert issue_list_from_html[5].type == jira_issue.IssueType.BUG

    assert issue_list_from_html[6].key == "PROD-12345"
    assert issue_list_from_html[6].fix_version == None
    assert issue_list_from_html[6].product_area == "Dispatch"
    assert (
        issue_list_from_html[6].release_notes_desc
        == "OUTBOUND-3154 Release Notes description."
    )
    assert issue_list_from_html[6].type == jira_issue.IssueType.BUG

    assert issue_list_from_html[7].key == "OUTBOUND-3919"
    assert issue_list_from_html[7].fix_version == None
    assert issue_list_from_html[7].product_area == "Picking - OSR, Staging"
    assert (
        issue_list_from_html[7].release_notes_desc
        == "Now the MFC Manager has the capability in TOM UI to assign the dispatch lanes for express orders"
        " without request to the support team by using the “Dispatch ramp assignment“ button on the Dispatch Ramp page in TOM UI."
    )
    assert issue_list_from_html[7].type == jira_issue.IssueType.IMPROVEMENT

    assert issue_list_from_html[8].key == "PROD-6789"
    assert issue_list_from_html[8].fix_version == None
    assert issue_list_from_html[7].product_area == "Picking - OSR, Staging"
    assert (
        issue_list_from_html[7].release_notes_desc
        == "Now the MFC Manager has the capability in TOM UI to assign the dispatch lanes for express orders"
        " without request to the support team by using the “Dispatch ramp assignment“ button on the Dispatch Ramp page in TOM UI."
    )
    assert issue_list_from_html[7].type == jira_issue.IssueType.IMPROVEMENT


def test_issue_grouping_by_date(issue_list_from_html):
    assert issue_list_from_html[0].date_item == "04 Oct, 2022"
    assert issue_list_from_html[1].date_item == "28 Apr, 2022"
    assert issue_list_from_html[2].date_item == "21 Feb, 2022"
    assert issue_list_from_html[3].date_item == "21 Feb, 2022"
    assert issue_list_from_html[4].date_item == "28 Sep, 2022"
    assert issue_list_from_html[5].date_item == "28 Sep, 2022"
    assert issue_list_from_html[6].date_item == "28 Sep, 2022"
    assert issue_list_from_html[7].date_item == "20 Sep, 2022"
    assert issue_list_from_html[8].date_item == "20 Sep, 2022"

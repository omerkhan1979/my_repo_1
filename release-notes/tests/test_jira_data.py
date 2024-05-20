from src import jira_issue
from src import union_data
from datetime import datetime

JIRA_ISSUE_BUG = (
    "{"
    '   "issues": ['
    '       {"expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields", '
    '       "id": "74783", '
    '       "self": "https://takeofftech.atlassian.net/rest/api/2/issue/74783", '
    '       "key": "OUTBOUND-7777", '
    '       "fields": {'
    '           "issuetype": '
    '           {"self": "https://takeofftech.atlassian.net/rest/api/2/issuetype/10204", '
    '           "id": "10204", '
    '           "description": "Bug description", '
    '           "iconUrl": "https://takeofftech.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10792?size=medium", '
    '           "name": "Bug", '
    '           "subtask": false, '
    '           "avatarId": 10792, '
    '           "hierarchyLevel": 0'
    "           }, "
    '           "customfield_10372": "This is a bug release notes",'
    '           "fixVersions": ['
    '               {"name":"RT52-22:[22-01-02]"},'
    '               {"name":"By releasing this increment, well add the ability to configure items availability split logic on MFC level rather than having it on a global level (per environment) using ITEMS_AVAILABILITY_MFC config so that spit strategy can be set up per location-id"}'
    "           ]"
    "       }"
    "       }"
    "   ],"
    '   "quantity": 1}'
)
JIRA_ISSUE_STORY = (
    "{"
    '   "issues": ['
    "       {"
    '           "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields", '
    '           "id": "73665", '
    '           "self": "https://takeofftech.atlassian.net/rest/api/2/issue/73665", '
    '           "key": "INBOUND-1604", '
    '           "fields": {'
    '               "issuetype": {'
    '                   "self": "https://takeofftech.atlassian.net/rest/api/2/issuetype/10100", '
    '                   "id": "10100", '
    '                   "description": "A user story. Created by JIRA Software - do not edit or delete.", '
    '                   "iconUrl": "https://takeofftech.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10802?size=medium", '
    '                   "name": "Story", '
    '                   "subtask": false, '
    '                   "avatarId": 10802, '
    '                   "hierarchyLevel": 0'
    "               }, "
    '               "customfield_10372": "Story Release Notes Description",'
    '               "fixVersions": ['
    '                   {"name":"RT52-22:[22-12-21]"},'
    '                   {"name":"RT52-21:[21-12-20]"},'
    '                   {"name":"By releasing this increment, well add the ability to configure items availability split logic on MFC level rather than having it on a global level (per environment) using ITEMS_AVAILABILITY_MFC config so that spit strategy can be set up per location-id"}'
    "               ]"
    "           }"
    "       }"
    "   ], "
    '   "quantity": 1'
    "}"
)

JIRA_ISSUE_PRODUCT_AREA = (
    '{"issues": ['
    '{"expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields", '
    '"id": "73665", '
    '"self": "https://takeofftech.atlassian.net/rest/api/2/issue/73665", '
    '"key": "INBOUND-1604", '
    '"fields": {"issuetype": '
    '{"self": "https://takeofftech.atlassian.net/rest/api/2/issuetype/10100", '
    '"id": "10100", '
    '"description": "A user story. Created by JIRA Software - do not edit or delete.", '
    '"iconUrl": "https://takeofftech.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10802?size=medium", '
    '"name": "Story", '
    '"subtask": false, '
    '"avatarId": 10802, '
    '"hierarchyLevel": 0}, '
    '"customfield_10372": "Story Release Notes Description", '
    '               "customfield_10589": [{ "value": "3P delivery (new field for 2023)"} ],'
    '"fixVersions": ['
    '                   {"name": "RT52-22:[22-01-02]"},'
    '                   {"name": "RT51-22:[22-12-10]"},'
    '                   {"name": "By releasing this increment, well add the ability to configure items availability split logic on MFC level rather than having it on a global level (per environment) using ITEMS_AVAILABILITY_MFC config so that spit strategy can be set up per location-id"}'
    "               ]"
    "           }"
    "       }"
    "   ], "
    '   "quantity": 1'
    "}"
)

JIRA_ISSUE_PRODUCT_AREA_NONE = (
    '{"issues": ['
    '{"expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields", '
    '"id": "73665", '
    '"self": "https://takeofftech.atlassian.net/rest/api/2/issue/73665", '
    '"key": "INBOUND-1604", '
    '"fields": {"issuetype": '
    '{"self": "https://takeofftech.atlassian.net/rest/api/2/issuetype/10100", '
    '"id": "10100", '
    '"description": "A user story. Created by JIRA Software - do not edit or delete.", '
    '"iconUrl": "https://takeofftech.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10802?size=medium", '
    '"name": "Story", '
    '"subtask": false, '
    '"avatarId": 10802, '
    '"hierarchyLevel": 0}, '
    '"customfield_10372": "Story Release Notes Description", '
    '               "customfield_10589": [{ "value": ""} ],'
    '"fixVersions": ['
    '                   {"name":"RT52-22:[22-01-02]"},'
    '                   {"name":"By releasing this increment, well add the ability to configure items availability split logic on MFC level rather than having it on a global level (per environment) using ITEMS_AVAILABILITY_MFC config so that spit strategy can be set up per location-id"}'
    "               ]"
    "           }"
    "       }"
    "   ], "
    '   "quantity": 1'
    "}"
)

JIRA_ISSUE_PRODUCT_AREA_MULITPLE = (
    '{  "issues": ['
    '   {   "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields", '
    '       "id": "7366", '
    '       "self": "https://takeofftech.atlassian.net/rest/api/2/issue/7366", '
    '       "key": "INBOUND-160", '
    '       "fields": {'
    '           "issuetype": '
    '           {   "self": "https://takeofftech.atlassian.net/rest/api/2/issuetype/1010", '
    '               "id": "1010", '
    '               "description": "A user story. Created by JIRA Software - do not edit or delete.", '
    '               "iconUrl": "https://takeofftech.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10792?size=medium", '
    '               "name": "BUG", '
    '               "subtask": false, '
    '               "avatarId": 10792, '
    '               "hierarchyLevel": 0'
    "           }, "
    '           "customfield_10372": "Bug with multiple Product Areas Description", '
    '           "customfield_10589": ['
    "               {"
    '                   "self": "https://takeofftech.atlassian.net/rest/api/2/customFieldOption/10842", "value": "Picking - OSR", "id": "10842"'
    "               },"
    '               { "value": "3P delivery (new field for 2023)"},'
    '               { "value": "Order Serving / Truck Loading / Truck Unloading" },'
    '               { "value": "Dispatch" }'
    "           ],"
    '"fixVersions": ['
    '                   {"name":"RT52-22:[22-01-02]"},'
    '                   {"name":"By releasing this increment, well add the ability to configure items availability split logic on MFC level rather than having it on a global level (per environment) using ITEMS_AVAILABILITY_MFC config so that spit strategy can be set up per location-id"}'
    "               ]"
    "       }"
    "   }], "
    '   "quantity": 1'
    "}"
)


def test_jira_correct_issue_fields():
    issues_list = union_data._get_jira_issues_list(JIRA_ISSUE_STORY)
    assert issues_list[0].key == "INBOUND-1604"
    assert issues_list[0].release_notes_desc == "Story Release Notes Description"
    assert issues_list[0].type == jira_issue.IssueType.IMPROVEMENT


def test_jira_correct_issue_fields_with_product_area():
    """Tests Jira fields including Product Area"""
    issues_list = union_data._get_jira_issues_list(JIRA_ISSUE_PRODUCT_AREA)
    assert issues_list[0].key == "INBOUND-1604"
    assert issues_list[0].release_notes_desc == "Story Release Notes Description"
    assert issues_list[0].type == jira_issue.IssueType.IMPROVEMENT
    assert issues_list[0].product_area == jira_issue.ProductArea.THREE_P_DELIVERY


def test_jira_issue_fields_with_product_area_multiple():
    """Tests Jira fields including Product Area"""
    issues_list = union_data._get_jira_issues_list(JIRA_ISSUE_PRODUCT_AREA_MULITPLE)
    assert issues_list[0].key == "INBOUND-160"
    assert (
        issues_list[0].release_notes_desc
        == "Bug with multiple Product Areas Description"
    )
    assert issues_list[0].type == jira_issue.IssueType.IMPROVEMENT
    print(f'"{issues_list[0].product_area}"')
    product_array_list = issues_list[0].product_area.strip().split(",")
    assert len(product_array_list) == 4
    assert product_array_list[0].strip() == jira_issue.ProductArea.PICKING_OSR
    assert product_array_list[1].strip() == jira_issue.ProductArea.THREE_P_DELIVERY
    assert product_array_list[2].strip() == jira_issue.ProductArea.ORDER_SERVING
    assert product_array_list[3].strip() == jira_issue.ProductArea.DISPATCH


def test_issue_product_area_none():
    """Checks for product area"""
    story = union_data._get_jira_issues_list(JIRA_ISSUE_PRODUCT_AREA_NONE)
    bug = union_data._get_jira_issues_list(JIRA_ISSUE_BUG)

    assert story[0].product_area == None
    assert bug[0].product_area == None


def test_issue_type():
    story = union_data._get_jira_issues_list(JIRA_ISSUE_STORY)
    bug = union_data._get_jira_issues_list(JIRA_ISSUE_BUG)

    assert story[0].type == jira_issue.IssueType.IMPROVEMENT
    assert bug[0].type == jira_issue.IssueType.BUG


def test_several_issues(issue_list_from_json):
    assert len(issue_list_from_json) == 8
    assert issue_list_from_json[0].key == "INBOUND-99555"
    assert issue_list_from_json[1].key == "PROD-12345"
    assert issue_list_from_json[2].key == "OUTBOUND-3199"
    assert issue_list_from_json[3].key == "OUTBOUND-3054"
    assert issue_list_from_json[4].key == "OUTBOUND-3999"
    assert issue_list_from_json[5].key == "OUTBOUND-3299"
    assert issue_list_from_json[6].key == "INC-568"
    assert issue_list_from_json[7].key == "PROD-6789"


def test_new_jira_issues_have_todays_date(issue_list_from_json):
    today_date = f"{datetime.now():%d %b, %Y}"
    assert issue_list_from_json[0].date_item == today_date
    assert issue_list_from_json[1].date_item == today_date
    assert issue_list_from_json[2].date_item == today_date
    assert issue_list_from_json[3].date_item == today_date
    assert issue_list_from_json[4].date_item == today_date
    assert issue_list_from_json[5].date_item == today_date
    assert issue_list_from_json[6].date_item == today_date
    assert issue_list_from_json[7].date_item == today_date


def test_jira_issues_fix_version(issue_list_from_json: list[jira_issue.JiraIssue]):
    assert issue_list_from_json[0].fix_version == "RT52-22"
    assert issue_list_from_json[1].fix_version == "RT51-21"
    assert issue_list_from_json[2].fix_version == "RT52-22"
    assert issue_list_from_json[3].fix_version == "RT50-22"
    assert issue_list_from_json[4].fix_version == "RT40-22"
    assert issue_list_from_json[5].fix_version == "RT48-21"
    assert issue_list_from_json[6].fix_version == "RT06-22"
    assert issue_list_from_json[7].fix_version == "RT16-22"


def test_jira_correct_fix_version_same_year():
    issues_list = union_data._get_jira_issues_list(JIRA_ISSUE_PRODUCT_AREA)
    assert len(issues_list) == 1
    assert issues_list[0].fix_version == "RT51-22"


def test_jira_correct_fix_version_different_year():
    issues_list = union_data._get_jira_issues_list(JIRA_ISSUE_STORY)
    assert len(issues_list) == 1
    assert issues_list[0].key == "INBOUND-1604"
    assert issues_list[0].fix_version == "RT52-21"

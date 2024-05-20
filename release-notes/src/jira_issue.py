from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class IssueType(str, Enum):
    BUG = ("Bug",)
    IMPROVEMENT = "Improvement"


class ProductArea(str, Enum):
    """Different possible Product Areas

    Args:
        str (_type_): _description_
        Enum (_type_): _description_
    """

    PICKING_MANUAL = "Picking - Manual"
    PRODUCT_CATALOG = "Product Catalog"
    DECANTING = "Decanting"
    INVENTORY_MANAGEMENT = "Inventory Management"
    INVENTORY_MANAGEMENT_OSR = "Inventory Management - OSR"
    INVENTORY_MANAGEMENT_MANUAL = "Inventory Management - Manual"
    ORDER_MANAGEMENT = "Order Management"
    USER_MANAGEMENT = "User Management & Authentication"
    ASSORTMENT_MANAGEMENT = "Assortment Management Platform"
    CONFIGURATION_MANAGEMENT = "Configuration management UI (new field for 2023)"
    IN_STORE_PICKING = "In-store Picking"
    REPLENISHMENT = "Replenishment - GOLD"
    MANUAL_RECEIVING = "Manual Receiving"
    ORDER_SERVING = "Order Serving / Truck Loading / Truck Unloading"
    PICKING_OSR = "Picking - OSR"
    STAGING = "Staging"
    LABELING = "Labeling"
    DISPATCH = "Dispatch"
    THREE_P_DELIVERY = "3P delivery (new field for 2023)"
    EXPRESS_ORDERS = "Express Orders"


@dataclass
class JiraIssue:
    """Internal representation of 'JiraTicket' entity, with only essential data, specific for this project"""

    key: str  # is a main jira issue identifier
    type: IssueType  # issue type - Bug or Improvement
    release_notes_desc: str  # human-readable release note description
    product_area: str  # Product areas that can more that one
    fix_version: str
    date_item: str = f"{datetime.now():%d %b, %Y}"

    def __init__(
        self,
        key: str,  # is a main jira issue identifier
        type: IssueType,  # issue type - Bug or Improvement
        release_notes_desc: str,  # human-readable release note description
        fix_version: str,  # RT fix version
        date_item: str = None,
        product_area: str = None,
    ):
        self.key = key.replace("\n", " ").strip()
        self.type = type

        if release_notes_desc:
            # get rid of \n we will use <br> and <p> fpr spacing in the html
            self.release_notes_desc = release_notes_desc.strip()

        if date_item:
            self.date_item = date_item

        self.set_product_area(product_area)

        self.fix_version = fix_version

    def set_product_area(self, product_area: str):
        if product_area != None and len(product_area.strip()) > 1:
            self.product_area = product_area.strip()
        else:
            self.product_area = None


def get_issue_by_key(jira_issue_list: list[JiraIssue], key: str) -> JiraIssue:
    for i in jira_issue_list:
        if i.key == key:
            return i
    raise Exception(f"Issue with key {key} not found")


def transform_json_to_jira_issue(issue_json: dict) -> JiraIssue:
    if issue_json["fields"]["customfield_10372"] is None:
        print(
            f'{issue_json["key"]} Jira issue did not have any Rlease Notes Description'
        )
    jira_issue = JiraIssue(
        key=issue_json["key"],
        release_notes_desc=issue_json["fields"]["customfield_10372"],
        type=get_issue_type(issue_json),
        fix_version=get_fix_version(issue_json),
    )

    # only include if field exists
    if issue_json["fields"].__contains__("customfield_10589"):
        if issue_json["fields"]["customfield_10589"] is not None:
            product_area = ""
            for current_product_area in issue_json["fields"]["customfield_10589"]:
                if (
                    (current_product_area.get("value") is not None)
                    and current_product_area.get("value").strip() != ""
                    and current_product_area.get("value").strip() != "None"
                ):
                    if len(product_area) == 0:
                        product_area = current_product_area.get("value")
                    else:
                        product_area = (
                            product_area + ", " + current_product_area.get("value")
                        )

                if len(product_area) > 0:
                    jira_issue.product_area = product_area
    return jira_issue


def transform_list_of_jsons_to_list_of_issues(list_of_jsons: list) -> list[JiraIssue]:
    result = []
    for issue_json in list_of_jsons:
        issue = transform_json_to_jira_issue(issue_json)
        result.append(issue)
    return result


def get_issue_type(issue_json: dict) -> str:
    issue_type = issue_json["fields"]["issuetype"]["name"]
    if issue_type == IssueType.BUG:
        return IssueType.BUG
    else:
        return IssueType.IMPROVEMENT


def get_fix_version(issue_json: dict) -> str:
    fix_versions = issue_json["fields"]["fixVersions"]
    list_fix_versions = []
    for i in range(len(fix_versions)):
        if (
            (fix_versions[i].get("name") is not None)
            and fix_versions[i].get("name").strip() != ""
            and fix_versions[i].get("name").strip() != "None"
            and fix_versions[i].get("name").strip().startswith("RT")
        ):
            # Only care about the ones that start with RT, all others can be discarded
            list_fix_versions.append(  # truncates the Date content to only print RTXX-YY
                "{:7.7}".format(fix_versions[i].get("name").strip())
            )

    fix_version = None
    if len(list_fix_versions) > 0:
        # if there are multiple RT fix versions - go through this logic
        fix_version = list_fix_versions[0]
        for i in range(len(list_fix_versions)):
            # code get the the lowest/oldest RT version
            if fix_version == list_fix_versions[i]:
                continue
            # get the value after RT
            temp_rt_num = int(fix_version[2:4])
            # get the value after -
            temp_rt_yr = int(fix_version[5:7])
            if temp_rt_yr > int(list_fix_versions[i][5:7]):
                # if yr is greater update fix_version
                fix_version = list_fix_versions[i]
            elif temp_rt_yr == int(list_fix_versions[i][5:7]) and temp_rt_num > int(
                list_fix_versions[i][2:4]
            ):
                # if yr is the same and week is greater then  update fix_version
                fix_version = list_fix_versions[i]

    return fix_version


def get_issues_by_product_area(
    jira_list: list[JiraIssue], product_area: str
) -> list[JiraIssue]:
    """This function takes a list of Jira Issue objects and filters for for a specified Product Area.

    Args:
        jira_list (list[JiraIssue]): list of Jira Issue objects_
        product_area (str): specified Product Area

    Returns:
        list[JiraIssue]: list of Jira Issues with the specified Product Area
    """
    product_area_list = []
    for i in jira_list:
        if hasattr(i, "product_area") and i.product_area == product_area:
            product_area_list.append(i)
    return product_area_list


def get_issues_by_fix_version(
    jira_list: list[JiraIssue], fix_version: str
) -> list[JiraIssue]:
    """This function takes a list of Jira Issue objects and filters for for a specified Product Area.

    Args:
        jira_list (list[JiraIssue]): list of Jira Issue objects_
        fix_version (str): specified Fix Version

    Returns:
        list[JiraIssue]: list of Jira Issues with the specified Fix Version
    """
    fix_version_list = []
    for i in jira_list:
        if hasattr(i, "fix_version") and i.fix_version == fix_version:
            fix_version_list.append(i)
    return fix_version_list

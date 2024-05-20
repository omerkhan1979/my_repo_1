from bs4 import BeautifulSoup
from re import search

from jira_issue import JiraIssue, IssueType


def read_input_html(file_path):
    """Get the "soup" for a given html file, can be a url"""

    with open(file_path, "r", encoding="utf-8") as fh:
        # Read and parse the file
        return BeautifulSoup(fh, features="html.parser")


def get_issue_list(file_path) -> list[JiraIssue]:
    """Iterate over html file, building a list of `JiraIssue` objects"""
    issuelist = []
    date_list = read_input_html(file_path).find_all("div")
    for elem in date_list:
        date = elem.h2.text
        issue_groups = elem.find_all("section")
        for e in issue_groups:
            group = e.h3

            # backward compatible - originally it was h4
            if group == None:
                group = e.h4.text
            else:
                group = group.text

            if group.find(IssueType.BUG) != -1:
                issue_type = IssueType.BUG
            else:
                issue_type = IssueType.IMPROVEMENT
            issue_list = e.find_all("p")
            for issue in issue_list:
                issue_key_product_area: str = issue.find("strong").text
                issue_key = issue_key_product_area
                m = search(r"\d+$", issue_key)
                issue_product_area = None
                fix_version = None
                if "Version:" in issue_key:
                    issue_info = issue_key.split("Version:", 1)
                    issue_key = issue_info[0]
                    fix_version = issue_info[1]
                    if "Product Area(s):" in fix_version:
                        fix_version = fix_version.split("Product Area(s):", 1)
                        issue_product_area = fix_version[1]
                        fix_version = fix_version[0]

                    # truncates the Date content to only print RTXX-YY
                    fix_version = "{:7.7}".format(fix_version.strip())

                elif "Product Area(s):" in issue_key:
                    issue_key = issue_key.split("Product Area(s):", 1)
                    issue_product_area = issue_key[1]
                    issue_key = issue_key[0]

                elif m is None:
                    # backward compatible for Product Area for issues prior to October 4th, 2022
                    issue_key_product_area = issue_key.split(" ", 1)
                    issue_key = issue_key_product_area[0]
                    issue_product_area = issue_key_product_area[1]

                issue_desc = issue.find("span").text
                if issue_product_area != None:
                    issue_product_area = (
                        issue_product_area.replace("<br>", "")
                        .replace("\\n", "")
                        .strip()
                    )

                if fix_version != None:
                    fix_version = (
                        fix_version.replace("<br>", "").replace("\\n", "").strip()
                    )

                issuelist.append(
                    JiraIssue(
                        issue_key.replace("<br>", "").replace("\\n", "").strip(),
                        issue_type,
                        issue_desc.strip(),
                        fix_version,
                        date,
                        issue_product_area,
                    )
                )
    return issuelist


if __name__ == "__main__":
    list = get_issue_list("../pytest/test.html")
    for i in list:
        print("Issue: ", i)

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

"""
This is the content of the information that is retrieved from Get Jira Issue. 
customfield_10000 is the field to look at. Here is the sample information:
{
    pullrequest={
        dataType=pullrequest, state=OPEN, stateCount=2
    }, 
    build={
        count=2, dataType=build, failedBuildCount=0, successfulBuildCount=1, unknownBuildCount=1
    }, 
    json={
        "cachedValue":{
            "errors":[],
            "summary":{
                "pullrequest":{
                    "overall":{
                        "count":2,
                        "lastUpdated":"2022-10-05T09:18:58.000-0400",
                        "stateCount":2,
                        "state":"OPEN",
                        "dataType":"pullrequest",
                        "open":true
                    },
                    "byInstanceType":{
                        "GitHub":{
                            "count":1,
                            "name":"GitHub"
                        },
                        "GitForJiraCloud":{
                            "count":1,
                            "name":"GitForJiraCloud"
                        }
                    }
                },
                "build":{
                    "overall":{
                        "count":2,
                        "lastUpdated":null,
                        "failedBuildCount":0,
                        "successfulBuildCount":1,
                        "unknownBuildCount":1,
                        "dataType":"build"
                    },
                    "byInstanceType":{
                        "cloud-providers":{
                            "count":2,
                            "name":"Other providers"
                        }
                    }
                }
            }
        },
        "isStale":false
    }
}

From the content above, the json output specifically: ["cachedValue"]["summary"]["pullrequest"]
and ["cachedValue"]["summary"]["build"]
    """


class PullRequestReviewState(Enum):
    """Different Pull Request Review State
    Args:
        Enum (_type_): _description_
    """

    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    COMMENTED = "commented"
    DISMISSED = "dismissed"
    PENDING = "pending"


class PullRequestState(Enum):
    """Different Pull Request Review State
    Args:
        Enum (_type_): _description_
    """

    CLOSED = "closed"
    MERGED = "merged,closed"
    OPEN = "open"


@dataclass
class Build:
    """Internal representation of 'Build' entity, with only essential data, specific for this project"""

    count = 0
    failedBuildCount = 0
    successfulBuildCount = 0
    unknownBuildCount = 0

    def __init__(
        self,
        key: str,
        state: PullRequestState = None,
        review_state: PullRequestReviewState = None,
    ):
        self.key = key
        self.state = state
        self.review_state = review_state


@dataclass
class PullRequest:
    """Internal representation of 'PullRequest' entity, with only essential data, specific for this project"""

    key: str
    state: PullRequestState
    review_state: PullRequestReviewState
    stateCount: num
    lastUpdated

    def __init__(
        self,
        key: str,
        state: PullRequestState = None,
        review_state: PullRequestReviewState = None,
    ):
        self.key = key
        self.state = state
        self.review_state = review_state


@dataclass
class GitHubData:
    """Internal representation of 'GitHubData' entity, with only essential data, specific for this project"""

    def __init__(self, build: Build = None, pullrequest: PullRequest = None):
        self.build = build
        self.pullrequest = pullrequest


def get_pull_request_by_review_state(
    pr_list: list[PullRequest], key: PullRequestReviewState
) -> list[PullRequest]:
    """
    This function takes a list of Pull Request objects and filters for for a specified
    PullRequestReviewState.

    Args:
        pr_list (list[PullRequest]): list of Pull Request objects
        key (PullRequestReviewState): specified Pull Request Review State

    Returns:
        list[PullRequest]: list of Jira Issues with the specified Pull Request Review State
    """
    pull_request_list = []
    for i in pr_list:
        if hasattr(i, "review_state") and i.review_state == key:
            pull_request_list.append(i)
    return pull_request_list


def get_pull_request_by_state(
    pr_list: list[PullRequest], key: PullRequestState
) -> list[PullRequest]:
    """
    This function takes a list of Pull Request objects and filters for for a specified
    PullRequestState.

    Args:
        pr_list (list[PullRequest]): list of Pull Request objects
        key (PullRequestState): specified Pull Request State

    Returns:
        list[PullRequest]: list of Jira Issues with the specified Pull Request State
    """
    pull_request_list = []
    for i in pr_list:
        if hasattr(i, "state") and i.state == key:
            pull_request_list.append(i)
    return pull_request_list

#!/bin/bash

version=""
pr_name=""
calver=$(TZ=UTC git show --quiet HEAD --date='format-local:%y-%m-%d' --format="%cd")

# Set branch to ${CHANGE_BRANCH} if building from Pull Request
if [[ ${BUILD_SOURCEBRANCH} =~ "refs/heads/master" || ${BUILD_SOURCEBRANCH} =~ refs\/heads\/release\/.* ]]; then
  branch=$(echo ${BUILD_SOURCEBRANCH} | sed 's/refs.heads.//g')
else
  branch=${SYSTEM_PULLREQUEST_SOURCEBRANCH}
fi

echo "BUILD_SOURCEBRANCH: ${BUILD_SOURCEBRANCH}"
echo "Branch: ${branch}"

case ${branch} in
  *master) version=${calver} ;;
  *release/*)
    current_release=(${branch//release\//})
    version=${current_release}-hotfix
    ;;
  *feature/*)
    feature_name=(${branch//feature\//})
    version=PR${SYSTEM_PULLREQUEST_PULLREQUESTNUMBER}
    ;;
  *bugfix/*)
    bugfix_name=(${branch//bugfix\//})
    version=PR${SYSTEM_PULLREQUEST_PULLREQUESTNUMBER}
    ;;
  *hotfix/*)
    hotfix_version=(${branch//hotfix\//})
    version=PR${SYSTEM_PULLREQUEST_PULLREQUESTNUMBER}
    ;;
  *)
    >&2 echo "Unsupported branch name. Refer to 'Dev Lifecycle, Stagings, Jira Statuses' Confluence page."
    >&2 echo "https://cartfresh.atlassian.net/wiki/spaces/takeoff/pages/119144456/Dev+Lifecycle+Stagings+Jira+Statuses"
    exit 1
  ;;
esac

echo Prefix of version: ${version}
echo Build number: ${COUNTBUILD}

tagId=${version}.${COUNTBUILD}
echo tagId: ${tagId}

echo "##vso[task.setvariable variable=tagId;]$tagId"
echo "##vso[task.setvariable variable=branch;]$branch"
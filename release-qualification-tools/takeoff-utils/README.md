# takeoff-utils
A submodule for Takeoff's myriad utilities to be included in other repositories.
## Submodule Installation and Project Repository Updating
#### In order to install the takeoff-utils submodule into an existing repository:
```
git checkout -b UTILS-000
git submodule add https://github.com/takeoff-com/takeoff-utils.git takeoff-utils
git commit -m 'UTILS-000: Adding takeoff-utils submodule to repository'
git push -u origin UTILS-000
```
#### To update the version of the submodule that an existing repository points to:
When installed into a repository, a specific revision of the submodule is referenced. To update the tag in your repository to point to the latest version of the submodule, use:
```
git checkout -b UTILS-111
git submodule update --merge --remote
git commit -m"UTILS-111: Updating submodule"
git push -u origin UTILS-111
```
## Pulling the submodule into your workspace
#### Clone a repository that has the submodule from remote
`git clone --recursive <url to your repository>`

#### Pull the submodule into an already cloned repository
`git submodule init && git submodule update`

## Utility Descriptions
### githooks
#### Install githooks in your local workspace
Ensure that the submodule is in your repository, then run:
`./takeoff-utils/githooks/addhooks.sh`

#### Install pre-push githook only
Ensure that the submodule is in your repository, then run:
`./takeoff-utils/githooks/add_pre-push.sh`

#### Install pre-push githook and forward to specific calyx env:
Ensure that the submodule is in your repository, then run:
`./takeoff-utils/githooks/add_pre-push.sh dev`
`./takeoff-utils/githooks/add_pre-push.sh staging`
`./takeoff-utils/githooks/add_pre-push.sh prod` (default)
`./takeoff-utils/githooks/add_pre-push.sh localhost:9000`(when running calyx localy)


#### post-checkout
This hook will pull the latest revision of the takeoff-utils submodule that is referenced by your repository when a checkout command is run. This will ensure that your submodule is updated to the latest revision used by your repository.

#### pre-commit
This hook ensures that branch names conform to our [conventions](https://cartfresh.atlassian.net/wiki/spaces/SE/pages/1297055805/Naming+conventions)

#### commit-msg
This hook ensures that all commit messages conform to our [conventions](https://cartfresh.atlassian.net/wiki/spaces/SE/pages/1297055805/Naming+conventions)

#### prepare-commit-msg
This hook prepends the Jira key from the current branch to the commit message before editing. Note that it will not run if options are passed to `git commit` (e.g., `git commit -am "some message"`).

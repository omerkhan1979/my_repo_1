# Takeoff Engineering Handbook

Welcome to our [Takeoff Engineering Handbook site](https://engineering-handbook.takeofftech.org/) repository. This site is derived from [Docsy](https://github.com/google/docsy), a [Hugo-based theme](https://gohugo.io/) designed for technical documentation.

## Contributing

We welcome contributions from anyone at Takeoff. If you want to make a request or a submission, please understand the following:

- Before requesting or contributing, please review the [Handbook Jira project](https://takeofftech.atlassian.net/secure/RapidBoard.jspa?rapidView=281&projectKey=EH&view=planning&selectedIssue=EH-34&issueLimit=100) backlog for similar requests. If a similar request exists, please add to it rather than creating a new one.
- Issues are disabled for this repo. We use Jira tickets in the handbook project instead.

### Requesting content

Submit requests for content in our [Handbook Jira project](https://takeofftech.atlassian.net/secure/RapidBoard.jspa?rapidView=281&projectKey=EH&view=planning&selectedIssue=EH-34&issueLimit=100).

### Submitting Content
> ℹ️ !Warning!
> 
> Branch names must match the regex `^((feature|release|hotfix|bugfix)\/)?[A-Z]{2,8}-[0-9]{1,8}([_-][a-zA-Z0-9]+)*|(master)$`  
>Breaking this down:  
> 1) It must start with one of `feature`, `release`, `hotfix`, `bugfix`  
> 2) after this there must be a slash `/`  
> 3) The first part after the slash - `[A-Z]{2,8}-[0-9]{1,8}` should be a Jira ticket.  
> 4) after this, you can add some descriptive name using only letters, numbers, underscores, and hyphens.    
>
> Putting this all together you will have something like: `feature/DATA-1234-add-data-doc`
> 
> Failure to adhere to this will cause your branch to fail CI. If this happens, you will need to
> 1) make sure your local repo is not on the branch - `git checkout master`
> 2) remove the remote from your local copy - `git remote remove <bad branch>`
> 3) rename the branch - `git branch -m "oldname" "newname"`
> 4) switch to the new branch - `git checkout "newname"`
> 5) push the renamed branch back - `git git push --set-upstream origin $(git branch --show-current)`
> 6) create a new PR - `gh pr create --base <base_branch> --head <head_branch> --title "<PR_Title>" --body "<PR_Description>"`
> 7) close the old PR - `gh pr close <pr number>`
> 8) delete the old branch on the remote - `gh repo delete https://github.com/takeoff/engineering-handbook --branch <oldbranch>`


An Engineering Handbook Jira ticket is automatically created for each pull request. All content submissions are subject to a code-review workflow before they are published. If you would like to be part of the Handbook publishing review team, please submit a ticket on the [Handbook Jira project](https://takeofftech.atlassian.net/secure/RapidBoard.jspa?rapidView=281&projectKey=EH&view=planning&selectedIssue=EH-34&issueLimit=100).

## About the project theme

This Docsy Example Project is hosted at [https://example.docsy.dev/](https://example.docsy.dev/).

You can find detailed theme instructions in the Docsy user guide: https://docsy.dev/docs/

### Using Shortcodes

Hugo provides several [shortcodes][hugo-shortcodes], or reusable snippets of content that extend pure Markdown. In addition, you may also use [Docsy shortcodes][docsy-shortcodes] or [custom shortcodes][custom-shortcodes].

## Getting Started
For small changes or corrections, you can edit files in this repository directly in your browser, and submit a merge request.

For larger changes or contributions, we recommend branching this project and making changes on your own branch before making a submission.

## Running the website locally

Building and running the site locally requires a recent `extended` version of [Hugo](https://gohugo.io).
You can find out more about how to install Hugo for your environment in our
[Getting started](https://www.docsy.dev/docs/getting-started/#prerequisites-and-installation) guide.

Once you've made your working copy of the site repo, from the repo root folder, run

```
git submodule update --init --recursive
hugo server --poll 1000ms
```

## Running a container locally

You can run docsy-example inside a [Docker](https://docs.docker.com/)
container, the container runs with a volume bound to the `docsy-example`
folder. This approach doesn't require you to install any dependencies other
than [Docker Desktop](https://www.docker.com/products/docker-desktop) on
Windows and Mac, and [Docker Compose](https://docs.docker.com/compose/install/)
on Linux.

1. Update submodule

   ```
   git submodule update --init --recursive
   ```

2. Build the docker image

   ```bash
   # on non amd64
   docker-compose build
   # on amd64
   docker-compose -f docker-compose-m1.yaml build
   ```

3. Run the built image

   ```bash
   docker-compose up
   ```

   > NOTE: You can run both commands at once with `docker-compose up --build`.

4. Verify that the service is working.

   Open your web browser and type `http://localhost:1313` in your navigation bar,
   This opens a local instance of the docsy-example homepage. You can now make
   changes to the docsy example and those changes will immediately show up in your
   browser after you save.

### Cleanup

To stop Docker Compose, on your terminal window, press **Ctrl + C**. 

To remove the produced images run:

```console
docker-compose rm
```
For more information see the [Docker Compose
documentation](https://docs.docker.com/compose/gettingstarted/).

## Working with data model / puml diagrams

This repository uses a mixture of tools to have 'diagrams as code'. One tool is
PlantUML, which itself depends on `graphviz`. These assets are managed with
`./scripts/puml_to_svg.py`.

To update and interact with these diagrams locally:

1. set up a virtualenv for the handbook using python 3.8 (you can double check
   the version in the github workflow definition).
2. install the requirements from requirements.txt in `./scripts`
3. run the script with no arguments.

This will find and generate _all_ diagrams. It can take quite a while.

A full example of how to run this might be:

```
brew install graphviz
cd scripts
python3 -m venv ./env
./env/bin/pip install -r requirements.txt
./env/bin/python3 puml_to_svg.py
```

## Troubleshooting

As you run the website locally, you may run into the following error:

```
➜ hugo server

INFO 2021/01/21 21:07:55 Using config file: 
Building sites … INFO 2021/01/21 21:07:55 syncing static files to /
Built in 288 ms
Error: Error building site: TOCSS: failed to transform "scss/main.scss" (text/x-scss): resource "scss/scss/main.scss_9fadf33d895a46083cdd64396b57ef68" not found in file cache
```

This error occurs if you have not installed the extended version of Hugo.
See our [user guide](https://www.docsy.dev/docs/getting-started/) for instructions on how to install Hugo.

[hugo-shortcodes]: https://gohugo.io/content-management/shortcodes/
[docsy-shortcodes]: https://www.docsy.dev/docs/adding-content/shortcodes/
[custom-shortcodes]: layouts/shortcodes

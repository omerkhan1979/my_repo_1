---
title: "GitHub Best Practices"
linkTitle: "Git at Takeoff"
weight: 2
date: 2021-09-09
description: >
  Git best practices at Takeoff, and GitHub how-to intro training.  
---
 <img src="/images/en/docs/Engineering/git/gitteacher.png" alt = "git cat teacher" width="200" height="150" style="float:right" /> 

## Authentication
If you are on a new device you should authenticate through the github command line tool. On a mac this can be installed by running `brew install gh`. On a pc the tool can be installed through either WinGet, scoop, Chocolatey, or Conda, or can be downloaded as an MSI from the [release page](https://github.com/cli/cli/releases/latest)

- From your command line run `gh auth login`
- For "What account do you want to log into?" select "GitHub.com"
- If asked to re-authenticate, type `yes`
- For "What is your preferred protocol for Git operations" select `https`
- When asked "Authenticate Git with your GitHub credentials?" select `yes`
- For "How would you like to authenticate GitHub CLI?" select `Login with a web browser`
- Press enter to launch a web browser and copy the one-time code shown in your command line into the browser window.
- After entering the one-time code, You should see "GitHub CLI by GitHub wants to access your your-name_tkf account." Validate that the correct account is show, and click `Authorize github`
- Run `gh auth status` and validate that your tkf github account is listed along with `oauth_token`, and `https` protocol.

This process will create an oauth token and configure your git client to use that token. Oauth tokens are the only supported way of authenticating to github. ssh keys are not supported, and PAT tokens are supported only for automation use cases.

## New Repositories
If you're creating a new repository, there are a few things you need to make sure to do at the outset:
- The default branch of the new repository must be **main**
- **You must have [repository team owners set]**(https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/maintaining-ownership-continuity-for-your-organization), which can be at least members of the team you are working on. Each team has a corresponding team tag in github, such as `@team-sisyphus-members`.
- The main branch [**must** be protected](https://stackoverflow.com/questions/46146491/prevent-pushing-to-master-on-github#:~:text=To%20find%20it%20go%20to,people%20who%20are%20not%20moderators.) in absolutely all repositories, no pushes directly to main branch should be allowed ever (especially force pushes!).
- [Require two reviews](https://docs.github.com/en/organizations/organizing-members-into-teams/managing-code-review-assignment-for-your-team) for a merge to main branch in all repositories.
- **You must have a readme.md** - Make sure that the readme tells a developer that has never seen the repository everything they need to know to start developing on that repo. 

   Your Readme must include:
   1. What the repo does from a business perspective.
   2. If it is a service, what the service does in plain english.
   3. For local development: 
      1. How to install any relevant dependencies, and describe any dependencies for deployment to an environment (other services, secrets that must exist, env variables, etc.) 
      2. How to run the service locally.
   4. How the service runs from a technical perspective. what services does it talk to, what services does it listen to?
   5. What is the structure of the repository?
   6. Is there configuration that needs to be set up by the developer?
   7. How does the logging work, and where are the logs stored?
   8. How and where is the service monitored for health?
   9.  How to run test for the service. 
   10. How to deploy, both to staging and to production (is this repo tied to a release train, or independently deployable to prod?).
   11. FAQ, make sure to keep updating this as people ask you questions :smile:.

{{% alert title="Note" %}} An example of a really great readme at Takeoff is [Robotic Order Translator](https://github.com/takeoff-com/robotic-order-translator). {{% /alert %}}

- **You must have a contribute.md** that explains how to contribute, and lists or links to the appropriate contribution process.
## Committing
Make commits as small as possible; each commit should be able to have a single stated purpose. For reviewers, commits can act as a way to break down a pull request (PR) into more understandable chunks.

Another important way to make your PRs more understandable is with detailed commit messages. Leave an additional empty line after your commit summary if you are adding more detail so that the summary is easily visible when looking at a list of commits.

#### What to do before you commit
Diff (`git diff`) before you commit to make sure you are aware of every change about to go into your commit.
Make sure that your commit does one thing and one thing only; don't refactor something and make something new in the same commit!

#### Important details to put in a commit message:
1. What has changed in the commit code-wise?
1. What has changed in the logical flow of the program?

#### What NOT to do when committing:
1. Generic messaging, for example, “Fixed bug”, “refactored function”, or “work for JIRA-123”
1. Blaming messaging, for example, “WTF is this”, “fix this stupid garbage”


## Longer-lived Branches
Make sure you try to keep branches up to date with main branch as often as possible so that eventual merges are not confusing and difficult. You can do this via [rebasing](https://docs.github.com/en/get-started/using-git/about-git-rebase), where you re-point the base of your branch to the current head of main branch.

## Naming Conventions
At Takeoff, we have specific, enforced naming conventions for both commit messages and branch names. If naming conventions are not followed, your pull request will fail our convention checks and you will not be able to merge.

### Commit message conventions
All commit messages must be prefixed with `ABC-123: `  or `ABC-123 - ` (where `ABC-123` is the associated Jira task number), followed by a description of the commit.
If you use an incorrect commit name (which you will do eventually), you can [change the commit message](https://docs.github.com/en/github/committing-changes-to-your-project/creating-and-editing-commits/changing-a-commit-message) even after pushing it to fix the problem. 
<!-- See {{section on rebasing and renaming commits}} for info on how to do this. -->

### Branch name conventions
All branches must be named according to the following convention:
`<TYPE>/abc-123-<optional descriptive text>` where `<TYPE>` is one of either feature, release, hotfix, or bugfix depending on what the branch is for, and `abc-123` is the associated jira task.

### Pull Request name conventions
Pull request names must take one of the following forms:
`ABC-123: Task Summary` or `ABC-123 - Task Summary`.

## Merging
We currently use a few merge strategies depending on the repository, but the most common is the explicit merge (With a merge commit). There are some repositories that use squash and merge, which keeps the author signature in place.

### Fixing merge conflicts
If you aren't already experienced in git, you need to download and set up a merge tool. You can look at a few by just googling "git merge tools". One such tool used by engineers at Takeoff is [Diffmerge](https://sourcegear.com/diffmerge/), which you can install via brew on MacOS: `brew install --cask diffmerge`

Resolve conflicts using your best judgement. whenever possible, try to preserve all current logical flows that exist in both of the branches that you are merging. If you are unsure how to do that, you should reach out to the author of the changes that you are in conflict with. You can check this by doing a `git blame` on those specific lines, which looks something like this: `git blame our_file_path.go -L 95,100`. That will get us the names (or at least the git accounts) of the last person for every line between 95 and 100 (inclusive) in `our_file_path.go`. You can also just go to the github UI for that file and use the `blame` functionality on the file viewer.

Merges can accidentally break functionality (or roll back new functionality) if not done correctly, so always double-check the final version of the merged file to verify it looks and acts exactly how you expect it to. Also, if you've got good unit tests they will catch many more issues from merge problems!

For further, more detailed information on merge conflicts, see [Github's documentation on conflicts](https://docs.github.com/en/github/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-on-github).

## Release Branches
Release branches here at takeoff (as of 2021) are cut once every two weeks, and tested for one week prior to the first client release. During this window hotfixes are also allowed with the approval of the System QA team.

### Pushing a hotfix
Whoops, something is wrong in the release branch! we have to hotfix it, otherwise we cannot release our software to clients. There are multiple business processes involved in deciding to hotfix something, but here we are mostly going to discuss the technical details of _how_ to push a hotfix. If you need more information on the hotfix process, see [this document on our hotfix process](https://takeofftech.atlassian.net/wiki/spaces/SQ/pages/3133538658/Hotfix+Process+of+work+with+fixes+during+release+qualification+testing).

To release a hotfix, we will need two separate PRs. One for the main branch, and one for the release branch that we are trying to fix the issue in. These PRs will be using the same commits, which means we need to make use of `git cherry-pick`.

Assuming you've got approval from the system QA team for your change to go into the release branch, the general flow will be as follows:
1. Make a new branch, `bugfix/OOPS-123-hotfix` off of the main branch (not the release branch!).
1. Code up your hotfix and commit it to that branch (use multiple commits if it's appropriate, no need to stick to one).
   - Don't forget to test your change!
2. Push your branch up and open up a new pull request.
3. If your change was small and main branch has not diverged much from the release branch yet, you _may_ be able to just create another pull request using the same branch but setting the base branch to release instead of the main branch. If you try to do that and see any extraneous commits or work that you did not specifically do for that hotfix, abort!
   - Instead, create a new branch `bugfix/OOPS-123-blalalala` and use `git cherry-pick {commit-1}..{commit-n)`, where `commit-1` is the first commit you made for your hotfix and `commit-n` is the last. You can then push that up to github and request reviews on these pull requests you've made.
4. Once the changes are approved, you can merge your fix into the release branch. Make sure that the builds succeed after your merge, and inform the system QA team that the new release build is ready.
5. Main branch merges go through the normal review process.

## Reviews
Reviews are paramount to a good software project! When we put up a PR, we are putting it up for other employees to take a look at it, see what they think, and give feedback on the changes / features.

Similar to how we deal with commit messages, we don't want to use blaming words; don't say things are "stupid," or "bad," or "would only be done by an idiot." We're all trying to build the same application, and we're doing it together. If it isn't going to help the product by saying it, so leave it out.

The things we want to watch for most in code reviews are:
1. Is the change following the overall design of the current code?
   * If not, is there a reason for the change to design / flow?
1. Does it do what the developer intended?
   * We would generally expect functionality to be in place by the time a change gets to code review, but we still need to take a look! maybe the developer missed a functional requirement, or maybe they misunderstood what a requirement really meant.
   * Deploying a PR to test it if you're not sure about its functionality is always a good idea!
1. Is the change overly complex? This is a big one here at takeoff! we have a lot of different systems, many of them interconnected. If we can keep the internals of those systems simple and easily understandable, both current and future devs will be happier.
   * Don't be clever! clever code is hard to understand code. Even if you get marginal performance improvements out of being clever, it's still causing pain if someone in the future has to change that code and has no idea how it really works.
   * Don't over-engineer! make sure that the pull request is solving the problem at hand _now_, and not trying to solve future problems that haven't been scoped out yet; chances are it won't be solved in the best way.
1. Is there unit testing for the change?
   * We need to test any and all functional or bug changes, full stop. If we are not testing the actual change that was made, then we are setting ourselves up for problems in the future when someone changes the code, breaks functionality, and doesn't notice because there weren't unit tests covering some edge case.
1. Is the naming easily understandable?
   * Are the variables specific enough? If you're reading the code in a vacuum, can you understand what each variable is really for?
   * Please, please no single letter variables (yes, even `k,v`).
1. Comments; do they exist?
   * If there is a new function, it has clear and useful comments where necessary so we can understand what the function does at a high level. You don't always need to get into the nitty gritty if the function is fairly easy to read, but if it is necessarily complex (for example a state machine), feel free to get a little bit more into the weeds.
   * When making changes to code with existing comments, make sure that they are still both accurate and relevant; code changes without relevant comment changes can greatly increase confusion if engineers are getting conflicting information.
1. If you see something that you don't understand, ask about it! Code reviews aren't just for critiquing the change, they're also for the reviewer to understand the change that was made (and _why_ it was made).
1. Style guides, TBD by our coding standards.

## Repo Cleanliness
It's important to keep our repositories clean. A clean repository means that we don't have anything in there that doesn't need to be in there, and also that we _can't_ put anything in there that doesn't need to be there. To enforce this, we can take the following steps:
1. Don’t commit generated files, with the exception of generated lock files or other files essential for versioning of dependencies such as `package-lock.json`
1. Don’t commit dependencies (external libs and such). These must be installed locally for development and via whatever build job you are using for actual deployable artifacts.
1. Use one PR for one issue; do not combine multiple issues into a single PR.
1. Use .gitignore files to enforce these cleanliness rules!
1. Delete stale, old branches (you can make GitHub automatically delete merged ones, but branches that are never merged must still be pruned manually, eventually :sunglasses:).

### Terminology
Some of these are pulled directly from [git SCM](https://git-scm.com/docs/gitglossary); some of them are not, as the official documentation is sometimes a bit complex for this type of handbook.
#### Branch
A "branch" is a line of development. The most recent commit on a branch is referred to as the tip of that branch. The tip of the branch is referenced by a branch head, which moves forward as additional development is done on the branch. A single Git repository can track an arbitrary number of branches, but your working tree is associated with just one of them (the "current" or "checked out" branch), and HEAD points to that branch.
#### head
As above, head (often stylized as HEAD) is a pointer to the tip of a branch, which is generally the last commit on a branch.
#### fetch
Fetching a branch means to get the branch’s head ref from a remote repository (github-hosted repos in our case), to find out which objects (commits) are missing from the local object database, and then grab those objects.
#### hash
The unique identifier of an object (usually a commit). The object name is represented by a 40 character hexadecimal string called a SHA-1, although they can also be referenced by a shorter portion of that string, ex. `01797c49e6cdb6b79df1233e3ffb48fa235392e0` could be referenced as `01797c4`.
#### push
Pushing a branch means to get the branch’s head ref from a remote repository, find out if it is an ancestor to the branch’s local head ref, and in that case, putting all objects, which are reachable from the local head ref, and which are missing from the remote repository, into the remote object database, and updating the remote head ref. If the remote head is not an ancestor to the local head, the push fails.

---
## Exercise: 
### Getting this handbook running externally with a pull request
This little exercise is intended for people who are completely new with git, to get them comfortable with the flow of pulling a repository, changing to a new branch, making some changes, and making a PR. We won't be actually merging anything in this exercise, but that just involves clicking a big green button (very satisfying).

Most IDEs (such as VS Code) have the ability to preview `.md` files, so I suggest using one of those to make your changes; that way you can see what the page will really look like with your changes.

The first thing we need to do is actually get the engineering handbook copied onto our local machine; to do this, we need a takeoff-connected github account. If you don't have one of those yet, you can submit a ticket to IT support and they can connect an existing github account to takeoff for you (you will have to create the actual account yourself first).

We pull down a repository to our local machine by doing `git clone {clone link}` (the link can be found under the `code` button on the [homepage of the git repo](https://github.com/takeoff-com/engineering-handbook). This will download the whole repo into a folder under your current location, and turn that folder into a local git repository.

{{% alert title="Note" %}}  you can use [OUTBOUND-2471](https://takeofftech.atlassian.net/browse/OUTBOUND-2471) as your example jira ticket for any branch / commit naming in this exercise; it was the ticket used to write this page! {{% /alert%}}

Next, we want to navigate into that folder called `engineering-handbook`. We can do this by entering `cd engineering-handbook` (change directory to engineering handbook). Now that we're in the engineering handbook, we want to create a new branch for our changes.

`git checkout -b {your-new-branch-name}` moves you to a new branch with the specified name, branched off of your current branch, so let's execute that command.
Now you can make your changes (for example, change this line to say that you wrote this whole file and you're a git expert, everyone should now go to you with git questions)

Now that you have asserted your dominance over this page, do a last check for what changes you made by running the command `git diff`. If you only see the changes that you expect, we're good to stage our files make our first commit!

"Staging files" essentially means marking them as ready to commit. We can do this for every file we changed (`git add -A`), or we can go through each individual change (`git add -p .`) and either stage them or decide that we don't want to stage them, maybe because we saw a small issue. I generally recommend the latter, so that you can do one final sanity check on your changes.

Once we've staged the changes we want to commit, we can commit them via the command: `git commit -m "{commit message here}"`. Make sure your commit message is explaining what change you've just made!

Now, we've got a new branch with a new commit, but it's not on our github yet; we need to push it up there!

To do this, we can execute the command `git push origin [branch name]` (or just `git push` to push your current branch).
If that succeeds, we can go to the [repo homepage](https://github.com/takeoff-com/engineering-handbook) and see a yellow banner at the top that says something like `{branch name} had recent pushes less than a minute ago`, and a big green button that says `compare and pull request` and looks very satisfying to push. Good news, you get to push it!

Once you press that nice green button, you'll be brought to a PR creation page. Make sure your PR has a title that fits our conventions (See [Pull request naming conventions](#pull-request-name-conventions)), and add in any other information that you want into the body section below the title.

Once you have done that, you can hit one final satisfying green button, that this time says `Create pull request`.

Congrats! You made a pull request and can now contribute to this handbook as much as you want! If you make a real pull request and want people to review your changes (which they have to do before you can actually merge in your pull request), You can use `reviewers` section on the right side of the page to assign people who you think would want to review your work.

Now you can tell people that you know how to do basic git stuff, and be telling the truth! Because even if you forget, this page will always be here to help you :)

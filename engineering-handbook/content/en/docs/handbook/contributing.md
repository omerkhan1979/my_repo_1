---
title: "Contributing to the Handbook"
linkTitle: "How to Contribute"
weight: 3
date: 2017-07-14
description: >
  How to contribute to the Handbook.
---
## Who can update pages on this site?

*Anyone* can contribute! Examples of when and why you might contribute include:
- You find errors or other room for improvement in existing documentation.
- Existing content needs to be updated or expanded upon.
- You have an idea for all-new documentation that would help a Takeoff team members learn, grow, and excel at their job.  

## Iterative Approach

Do the smallest thing possible and get it out as quickly as possible. Do not fear the imperfect! If you make suggestions that can be excluded from the first iteration, turn them into separate linked issues. Don’t write a large plan; only write the first step. 
Borrow from examples you consider to be great. There's no shame in using something great to create an even better resource.
Trust that you’ll know better how to proceed after something is written. You’re doing it right if you’re slightly embarrassed by the first iteration. The impact both on your work process and on how much you achieve is greater than anticipated. In the beginning, it hurts to make decisions fast and to see that things are changed with less consultation. But frequently, the simplest version turns out to be the best one.

## Contribution Process

If you have a new idea, request, or an edit for existing content, please [review our Backlog](https://takeofftech.atlassian.net/secure/RapidBoard.jspa?rapidView=281&projectKey=EH&view=planning.nodetail&issueLimit=100) for similar requests, and either add on to an existing one, or [submit a new **story** ticket](https://takeofftech.atlassian.net/secure/CreateIssue.jspa?issuetype=10100&pid=10261).  

All contributions must start with a [Jira ticket on the Handbook board](https://takeofftech.atlassian.net/secure/CreateIssue.jspa?issuetype=10100&pid=10261). 

After you've created a ticket: 
1. Make sure your submission meets all the guidelines and requirements.
2. New documentation: or updated content can be drafted or edited as follows: 
   - In Confluence for convenience and collaboration, then converted to Markdown using [stackedit.io](https://stackedit.io/)
   - Directly as Markdown using your preferred code editor (we recommend VS Code + [Markdown All-in-one addon](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one)).
   - Directly in GitHub. An easy way to do this for any page is by clicking the "Edit This Page" link at the top of the right-hand pane in the Handbook. 
  {{% alert title="Note" color="warning" %}}
  Please make sure all documentation adheres to the [Documentation Templates](/docs/contributing/templates/) structure, and do your best to follow the [Style Guide](/docs/handbook/handbook-styleguide/).{{% /alert %}}
3. When you are ready, create a merge request and/or comment in the Jira ticket. All merge requests must receive a code review by the Handbook team. 
4. So that the Handbook is the Single Source of Truth (SSOT), any Confluence drafts must be **deleted** (Strongly recommended), or archived (strongly discouraged as this leads to redundant versoins).


## Contribution Guidelines and Requirements 

### File requirements
- All .md file names must be lowercase, and must include underscores "_" instead of spaces.
- All .md files that begin top level sections must be named "**_index.md**", and files that begin sub-sections must be named "**index.md**"  

### Frontmatter 
Each page file in a Hugo site has metadata frontmatter that tells Hugo about the page. You specify page frontmatter in TOML, YAML, or JSON (our example site and this site use YAML). Use the frontmatter to specify the page title, description, creation date, link title, template, and menu weighting. You can see a complete list of possible page frontmatter in [Front Matter](https://gohugo.io/content-management/front-matter/).

```markdown
---
title: "Contributing to the Handbook" 
linkTitle: "How to Contribute"
weight: 3
date: 2017-07-14
description: >
  How to contribute to the Handbook.
---
```
For our Handbook, metadata items are used as follows: 
  - **title**: The heading that apears at the top of the page.
  - **linkTitle**: The page link that appears in the right-hand pane.
  - **weight**: The ordered location within the section where the page link appears in the right-hand pane. The Handbook team can also help with this when you create a pull request.
  - **date**: The date that the page was last updated. Formatted as "[yyyy]-[mm]-[dd]."
  - **description**(*optional*): Sub-header introductory line (written as a sentence) that appears at the top of the page.    


### Page Contents
- Always construct your content using [one or more templates]({{< relref path="./templates.md" >}})
- See our style guide for an in-depth writing and style reference.
- All pages must be written in markdown. If you are not comfortable using markdown, let the Handbook team know and we will help you convert from Confluence. 
- Any pages brought over from Confluence must be deleted from Confluence to avoid duplication. [Archived content in Confluence is still available](https://confluence.atlassian.com/confeval/confluence-evaluator-resources/confluence-archiving-content#:~:text=Archived%20spaces%20are%20less%20visible%2C%20but%20still%20available%20on%20your%20site.%20Archiving%20a%20space%20is%20easy%20to%20undo%20%E2%80%94%20you%20can%20make%20a%20space%20current%20again%20at%20any%20time.) and can therefore cause a lot of confusion.
- [Shortcodes are available for formatting](https://gohugo.io/content-management/shortcodes/) for everything **except images**. 
- HTML is allowed for images, shortcodes are preferred for everything else.

### Image Requirements
- All images must be stored in **../static**, within a sub-directory path that mirrors the location of the .md file you are editing.
- Inline HTML is allowed for image formatting. 

### Other media
- Always embed videos and presentations using a [shortcodes](https://gohugo.io/content-management/shortcodes/).
  
## Merge Requests
When you are ready to submit your content, create a merge request in our [Github Repository](https://github.com/takeoff-com/engineering-handbook). 
Follow the [Merge Request Guidelines]({{< relref path="./styleguide.md#merge-requests-mrs" >}}).

Once your content or request is submitted, the Handbook team will review and determine next steps, whether that is approving the merge request, or following up with questions. 

### Reviewing and merging

Anyone with Maintainer access to the relevant Takeoff project can merge documentation changes.
Maintainers must make a good-faith effort to ensure that the content:

- Is clear and sufficiently easy for the intended audience to navigate and understand.
- Meets the [Templates]({{< relref path="./templates.md" >}}), and [Writing and Style Guidelines]({{< relref path="./styleguide.md" >}}).

If the author or reviewer has any questions, they can message the writer in the ticket or merge request.

The process involves the following:

- Primary Reviewer. Review by a **code reviewer** or other appropriate colleague to confirm accuracy, clarity, and completeness. This can be skipped
  for minor fixes without substantive content changes.
- Technical Writer (Optional). If not completed for a merge request prior to merging, can be scheduled
  post-merge with a separate [handbook board ticket](https://takeofftech.atlassian.net/secure/CreateIssue.jspa?issuetype=10100&pid=10261).

## Other ways to help

If you have ideas for further documentation resources please
[create an issue](https://takeofftech.atlassian.net/secure/CreateIssue.jspa?issuetype=10100&pid=10261)
in the Hanbook backlog.

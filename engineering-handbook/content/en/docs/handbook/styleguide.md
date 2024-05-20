---
title: "Handbook Style Guide"
linkTitle: "Style Guide"
date: 2017-08-05
weight: 5
description: >
  Takeoff Handbook documentation style guide
---

# Documentation Style Guide

This document defines the standards for Engineering handbook documentation, including grammar, formatting, word use, and more.

For style questions, create an issue or merge request with the handbook team.

In addition to this page, the following resources can help you craft and contribute to documentation:

- [Doc contribution guidelines]({{< relref path="./contributing.md" >}})
- [Documentation Templates]({{< relref path="./templates.md" >}})
- [Microsoft Style Guide](https://docs.microsoft.com/en-us/style-guide/welcome/)
- [Google Developer Documentation Style Guide](https://developers.google.com/style)

## Documentation is the single source of truth (SSOT)

The Takeoff documentation is the SSOT for all information related to Takeoff implementation, usage, and troubleshooting. It evolves
continuously, in keeping with new decisions and developments, and with improvements
for clarity, accuracy, and completeness.

This policy prevents information silos, making it easier to find information
about anything that Engineering team members need to know.

It also informs decisions about the kinds of content we include in our
documentation.

### The documentation includes all Engineering information

This also means including problem-solving actions that may address rare cases or be considered
_risky_, but provide proper context through fully-detailed
warnings and caveats. This kind of content should be included as it could be
helpful to others and, when properly explained, its benefits outweigh the risks.
If you think you have found an exception to this rule, contact the
Technical Writing team.

In addition, add all troubleshooting information to the documentation, no matter how
unlikely a user is to encounter a situation.

### The documentation includes all media types

Include any media types/sources if the content is relevant to readers. You can
freely include or link presentations, diagrams, and videos. No matter who
it was originally composed for, if it is helpful to any of our audiences, we can
include it.

- If you use an image that has a separate source file (for example, a vector or
  diagram format), link the image to the source file so that it may be reused or
  updated by anyone.
- Do not copy and paste content from other sources unless it is a limited
  quotation with the source cited. Typically it is better to either rephrase
  relevant information in your own words or link out to the other source.

### Topic types

In the software industry, it is a best practice to organize documentation into
different types. For example:

- Concepts
- Tasks
- Reference
- Troubleshooting

This allows us to address these issues:

- **Content is hard to find.** Our docs are comprehensive and include a large amount of
  useful information. Topic types create repeatable patterns that make our content easier
  to scan and parse.
- **Content is often written from the contributor's point of view.**  Our docs
  are written by contributors. Topic types (tasks specifically) help put
  information into a format that is geared toward helping others, rather than
  documenting how a feature was implemented.

Combining topic types within the same page is allowed. 

Takeoff uses these [topic type templates](../templates.md).

### Link instead of repeating text

Rather than repeating information from another topic, link to the single source
of truth and explain why it is important.

### Docs-first methodology

We employ a _documentation-first methodology_. This method ensures the documentation
remains a complete and trusted resource, and makes communicating more efficient.

- If the answer to a question exists in documentation, share the link to the
  documentation instead of rephrasing the information.
- When you encounter new information not available in our handbook documentation (for
  example, when working on a support case or testing a feature), your first step
  should be to create a merge request (MR) to add this information to the
  documentation. You can then share the MR to communicate this information.

New information that would be useful for our engineering team to know should not be written directly in a forum or other messaging system,
but added to a documentation merge request and then referenced, as described above.

The more we reflexively add information to the documentation, the more
the documentation helps others efficiently accomplish tasks and solve problems.

If you have questions when considering, authoring, or editing documentation, ask
the Handbook team. They're available on Slack in `#handbook` or in Jira by opening a ticket on the [Handbook board](https://takeofftech.atlassian.net/secure/RapidBoard.jspa?rapidView=281&projectKey=EH&selectedIssue=EH-35).
Otherwise, forge ahead with your best effort. It does not need to be perfect;
the team is happy to review and improve upon your content. Review the
[Contribution guidelines](../contributing.md) before you begin your first documentation MR.

Maintaining a knowledge base separate from the documentation would
be against the documentation-first methodology, because the content would overlap with
the documentation.

## Markdown

All Takeoff documentation is written using [Markdown](https://en.wikipedia.org/wiki/Markdown).

The [documentation website](https://engineering-handbook.takeofftech.org/)
uses Hugo as its static site generator, and Goldmark as its Markdown parser.

We recommend using regular Markdown and follow the rules in the linked style guide.

Hugo provides several [shortcodes][hugo-shortcodes], or reusable snippets of content that extend pure Markdown. In addition, you may also use [Docsy shortcodes][docsy-shortcodes] or [custom shortcodes][custom-shortcodes]. Avoid using inline code snippets except for these shortcodes.

### HTML in Markdown

Hard-coded HTML is valid, although it's discouraged from being used unless:

- There's no equivalent markup in Markdown.
- Advanced tables are necessary.
- Special styling is required.
- The usage is reviewed and approved by the handbook team.

### Markdown Rules

The Markdown used across all documentation must be consistent, as
well as easy to review and maintain. We do not yet test documentation changes, but in the near future we will implement tests that fail when any
document has an issue with Markdown formatting that may cause the page to render
incorrectly. Tests will also be designed to fail when a document has
non-standard Markdown (which may render correctly, but is not the current
standard for Takeoff documentation).

The linting tool we will be implementing is [markdownlint](https://github.com/DavidAnson/markdownlint)

## Structure

We use concept, task, and reference topic types in the same larger topic.

For top level categories (for example, engineering or architecture), we have one topic that's a landing page.
Below that topic in the left nav are individual topics. Each of these include a concept
and multiple related tasks, reference, and troubleshooting topics.

See [Content Templates](https://literate-meme-e2241634.pages.github.io/docs/handbook/templates/) for more information. 

### Folder structure overview

Our goal is to have a clear hierarchical structure with meaningful URLs like
`engineering-handbook.takeoff.org/engineering/using_github/`. With this pattern, you can
immediately tell that you are navigating to engineering-related documentation about
using GitHub. 

Put files for specific areas into the related folder. For example:

| Directory             | What belongs here |
|:----------------------|:------------------|
| `engineering/onboarding/`           | Engineering onboarding related documentation. Anything that related to engineering or takeoff onboarding within the engineering department goes here. |
| `engineering/api/`            | API-related documentation. |
| `architecture/data_model/`    | Documentation related to Takeoff's architecture team and decisions related to our data model.|
| `handbook/style_guide/`          | The location of this style guide. |
| `takeoff_agile_model/guilds/`        | Contains information about Agile guilds at Takeoff. |

### Work with directories and files

When working with directories and files in our Handbook project:

1. When you create a new directory, always start with an `index.md` file. This will become your landing page, and Hugo requires a file by this name to initialize each section. 
   Don't use another filename and _do not_ create `README.md` files.
1. _Do not_ use special characters and spaces, or capital letters in file
   names, directory names, branch names, and anything that generates a path.
1. When creating or renaming a file or directory and it has more than one word
   in its name, use underscores (`_`) instead of spaces or dashes. For example,
   proper naming would be `import_project/import_from_github.md`. This applies
   to both image files and Markdown files.
1. For image files, do not exceed 100KB.
2. Do not upload video files to the project repository.
   [Link or embed videos](#videos) instead.
3. There are six main directories: `onboarding`, `handbook`, `culture`, `takeoff agile model`, `engineering`, and
   `architecture`. If you would like to propose another directory, please submit a ticket to the Handbook team.

If you're unsure where to place a document or a content addition, this shouldn't
stop you from authoring and contributing. Use your best judgment, and then ask
the reviewer of your MR to confirm your decision. You can also ask the handbook team at
any stage in the process. The handbook team reviews all
documentation changes, regardless, and can move content if there is a better
place for it.

### Avoid duplication

Do not include the same information in multiple places.
[Link to a single source of truth instead.](#link-instead-of-repeating-text)

### References across documents

- Give each folder an `index.md` page that introduces the topic, and both introduces
  and links to the child pages, including to the index pages of
  any next-level sub-paths.
- To ensure discoverability, ensure each new or renamed doc is linked from its
  higher-level index page and other related pages.
- When making reference to Takeoff products and features, link to their
  respective documentation, at least on first mention.
- When making reference to third-party products or technologies, link out to
  their external sites, documentation, and resources.

### Structure in documents

- Structure content in alphabetical order in tables, lists, and so on, unless
  there's a logical reason not to (for example, when mirroring the user
  interface or an otherwise ordered sequence).

## Writing Style Guidelines

1. At Takeoff, we use American English as the standard written language.
1. Do not use rich text, it makes it hard to copy/paste. Use [Markdown](/handbook/markdown-guide/) to format text that is stored in a Git repository. In Google Docs use "Normal text" using the style/heading/formatting dropdown and paste without formatting.
1. Don't use ALL CAPS because it [feels like shouting](https://en.wikipedia.org/wiki/All_caps#Association_with_shouting).
1. Always write a paragraph on a single line. Use soft breaks ("word wrap") for readability. Don't put in a hard return at a certain character limit (e.g., 80 characters) and don't set your IDE to automatically insert hard breaks. Merge requests for the blog and handbook are very difficult to edit when hard breaks are inserted.
1. Do not create links like "here" or "click here". All links should have relevant anchor text that describes what they link to, such as: "Takeoff retailer integration API documentation". Using [meaningful links](https://www.futurehosting.com/blog/links-should-have-meaningful-anchor-text-heres-why/) is important to both search functionality and accessibility for people with learning differences and/or physical disabilities.
   This guidance should be followed in all places links are provided, whether in the handbook, website, GoogleDocs, or any other content.
   Avoid writing GoogleDocs content which states - `Goolge Meeting Link [Link]`.
   Rather, paste the full link directly following the word `Google`.
   This makes the link more prominent and makes it easier to follow while viewing the document.
1. Always use [ISO dates](https://en.wikipedia.org/wiki/ISO_8601#Calendar_dates) in all writing and legal documents since other formats [lead to online confusion](http://xkcd.com/1179/). Use `yyyy-mm-dd`, for example 2015-04-13, and never 04-13-2015, 13-04-2015, 2015/04/13, 20150413, 2015.04.13, nor April 13, 2015. Even if you use an unambiguous alternative format it is still harder to search for a date, sort on a date, and for other team members to know we use the ISO standard. For months use `yyyy-mm`, so 2018-01 for January. Refer to a year with CY18 (never with 2018) and a quarter with CY18-Q1 to prevent confusion with fiscal years and quarters. If the year is obvious from the context it is OK to use Dec 4, but not 12/4, since the ordering isn't obvious when using two numbers but when naming the month it is clear that the number of the day of the month.
1. Takeoff operates on a Fiscal Year that aligns with the calendar year. When referring to a fiscal year or quarter, please use the following abbreviations:
   1. "FY21" is the preferred format and means: Fiscal Year 2021, the period running from January 1, 2020 through December 31, 2020
   1. "Q1" = the first quarter of the current Fiscal Year, so on Jan 1, 2021, "Q1" is the period from Jan. 1, 2020 through Mar 30, 2021.
   1. When referring to a quarter in a future or past year, combine the two above: "FY22-Q1"
   1. When financial data is presented include a note to indicate fiscal year (e.g. "Fiscal Year ending January, 31 'yy")
1. Remember that not everyone is working in the same timezone; what may be morning for you is evening for someone else. Try to say 3 hours ago or 4 hours from now, or use a timestamp, including a timezone reference.
1. We use Eastern Standard Time as the timezone for engineering (for example production postmortems) and all cross-functional activities. Please refer to time as "9:00 Eastern" or `9:00 ET`. It isn't often necessary to specify whether a timezone is currently observing Daylight Saving Time, and such references are often incorrect, so prefer "PT" to "PDT" or "PST" unless you have a specific need to differentiate between PDT and PST.
1. When specifying measurements, please include both Metric and Imperial equivalents.
1. Although we're a US based company we're also an internationally diverse one. Please do not refer to team members outside the US as international, instead use non-US. Please also avoid the use of offshore/overseas to refer to non-American continents.
1. If you have multiple points in a comment or email, please number them. Numbered lists are easier to reference during a discussion over bulleted lists.
1. When you reference an issue, merge request, comment, commit, page, doc, etc. and you have the URL available please paste that in.
1. In making URLs, always prefer hyphens to underscores, and always use lowercase.
1. All people working for Takeoff (the company) are the Takeoff Team, or Rocketberries (internally). 
1. Please always refer to Takeoff Technologies Inc. people as Takeoff team members, not employees.
1. Use [inclusive and gender-neutral language](https://techwhirl.com/gender-neutral-technical-writing/) in all writing.
1. Always write "Takeoff" with "T" capitalized, and the "o" lowercase, even when writing "Takeoff.com", except within URLs. When "takeoff.com" is part of a URL it should be lowercase.
1. Refer to our overarching product offering as the "Takeoff solution".
1. Monetary amounts shouldn't have one digit, so prefer $19.90 to $19.9.
1. If an email needs a response, write the answer at the top of it.
1. Use the contemporary version of words. Just like we don't write internet with a capital letter anymore. We write frontend and webhook without a hyphen or space.
1. Our homepage is https://takeoff.com/ (with `https`).
1. Try to use the [active voice](https://writing.wisc.edu/Handbook/CCS_activevoice.html) whenever possible.
1. If you use headers, properly format them (`##` in Markdown, "Heading 2" in Google Docs); start at the second header level because header level 1 is for titles. Do not end headers with a colon. Do not use emoji in headers as these cause links to have strange characters.
1. Always use a [serial comma](https://en.wikipedia.org/wiki/Serial_comma) (a.k.a. an "Oxford comma") before the coordinating conjunction in a list of three, four, or more items.
1. Always use a single space between sentences rather than two.
1. Read our [Handbook Styleguide](/docs/handbook/handbook-styleguide/) for more information when writing documentation.
1. Do not use acronyms when you can avoid them. Acronyms have the effect of excluding people from the conversation if they are not familiar with a particular term. Example: instead of `MR`, write `merge request (MR)`.
   1. If acronyms are used, expand them at least once near the beginning of the document, but not in the title, and define them in the document. When possible, link to the definition of the acronym if it is described in further detail elsewhere.
1. Many times an explanation can be aided by a diagram.
Whenever presenting a diagram, we should still allow everyone to contribute.
Where possible, take advantage of the handbook's support for [Mermaid](https://mermaid-js.github.io/mermaid/#/README) and [Plant UML](https://plantuml.com/). If you are new to using Mermaid or PlantUML and need help troubleshooting errors in your diagram code, the [Mermaid Live Editor](https://mermaid-js.github.io/mermaid-live-editor/) and [PlantUML Live editor](https://www.planttext.com/) can be a helpful tool.
Where taking advantage of these diagram tools isn't possible, link to the original diagram or embed it in the page so that the diagram can be edited by anyone.

## Language

Takeoff documentation should be clear and easy to understand.

- Be clear, concise, and stick to the goal of the documentation.
- Write in US English with US grammar.
- Use [inclusive language](#inclusive-language).

### Trademark

Only use the Takeoff name and trademarks in accordance with
[Takeoff Brand Guidelines](https://docs.google.com/presentation/d/1s43N8AqmFKnv_5SBMa8dtrbebZ3PMF4UAlkW9itX4kE/edit#slide=id.g5544e787a1_0_4).

Don't use the possessive form of the word Takeoff (`Takeoff's`).

### Capitalization

#### Headings

Use sentence case. For example:

- `# Use variables to configure pipelines`
- `## Use the To-Do List`

#### UI text

When referring to specific user interface text, like a button label or menu
item, bold the name and use the same capitalization and spelling that's displayed in the user interface.

If you think the user interface text contains style mistakes,
create an issue to notify our UX team of the issue.

#### Feature names

- *Feature or functionality names are typically lowercase*, like those describing actions and
  types of objects in Takeoff. For example:
  - orders
  - issues
  - issue weights
  - merge requests
  - milestones
  - reorder issues
  - to-do list items
- *Major functionality and product areas are capitalized*, typically nouns naming Takeoff-specific
  capabilities or tools. For example:
  - Takeoff Solution
  - Takeoff Middleware UI (TOM UI)
  - Takeoff Mobile
  - Inbound
  - Outbound
- *Physical areas of the MFC are capitalized*
  - Micro-Fulfillment Center (MFC)
  - Manual area
- *Operations are not capitalized*
  - manual picking
  - decanting
  - in-store picking

Document any exceptions in this style guide. If you're not sure, ask the handbook team so that they can help decide and document the result.

#### Other terms

Capitalize names of:

- Takeoff partners and customers, for example: Braintree, Sedanos, Wakefern, Knapp, etc.  
- Third-party organizations, software, and products. For example, Prometheus,
  Kubernetes, GitHub.
- Methods or methodologies. For example, Continuous Integration,
  Continuous Deployment, Scrum, and Agile.

Follow the capitalization style listed at the [authoritative source](#links-to-external-documentation)
for the entity, which may use non-standard case styles. 

Use forms of *sign in*, instead of *log in* or *login*. For example:

- Sign in to Takeoff.
- Open the sign-in page.

Exceptions to this rule include the concept of *single sign-on* and
references to user interface elements. For example:

- To sign in to product X, enter your credentials, and then select **Log in**.

### Inclusive language

We strive to create documentation that's inclusive. 

We write our documentation with inclusivity and diversity in mind. This
page is not an exhaustive reference, but describes some general guidelines and
examples that illustrate some best practices to follow.

#### Avoid gender-specific wording

When possible, use gender-neutral pronouns. For example, you can use a singular
[they](https://developers.google.com/style/pronouns#gender-neutral-pronouns) as
a gender-neutral pronoun.

Avoid the use of gender-specific pronouns, unless referring to a specific person.


| Use                               | Avoid                           |
|-----------------------------------|---------------------------------|
| People, humanity                  | Mankind                         |
| Takeoff Team Members              | Manpower                        |
| You can install; They can install | He can install; She can install |


If you need to set up [Fake user information](#fake-user-information), use
diverse or non-gendered names with common surnames.

#### Avoid ableist language

Avoid terms that are also used in negative stereotypes for different groups.

| Use                    | Avoid                |
|------------------------|----------------------|
| Check for completeness | Sanity check         |
| Uncertain outliers     | Crazy outliers       |
| Slows the service      | Cripples the service |
| Placeholder variable   | Dummy variable       |
| Active/Inactive        | Enabled/Disabled     |
| On/Off                 | Enabled/Disabled     |

Credit: [Avoid ableist language](https://developers.google.com/style/inclusive-documentation#ableist-language)
in the Google Developer Style Guide.

#### Culturally sensitive language

Avoid terms that reflect negative cultural stereotypes and history. In most
cases, you can replace terms such as `master` and `slave` with terms that are
more precise and functional, such as `primary` and `secondary`.

| Use                  | Avoid                 |
|----------------------|-----------------------|
| Primary / secondary  | Master / slave        |
| Allowlist / denylist | Blacklist / whitelist |

For more information see the [Internet Draft specification](https://tools.ietf.org/html/draft-knodel-terminology-02).

### Fake user information

You may need to include user information in entries such as a REST call or user profile.
_Do not_ use real user information or email addresses in Takeoff documentation. For email
addresses and names, do use:

- _Email addresses_: Use an email address ending in `example.com`.
- _Names_: Use strings like `example_username`. Alternatively, use diverse or
  non-gendered names with common surnames, such as `Sidney Jones`, `Zhang Wei`,
  or `Alex Garcia`.

### Fake URLs

When including sample URLs in the documentation, use:

- `example.com` when the domain name is generic.
- `Takeoff.example.com` when referring only to self-managed Takeoff instances.
  Use `Takeoff.com` for Takeoff SaaS instances.

### Fake tokens

There may be times where a token is needed to demonstrate an API call using
cURL or a variable used in CI. It is strongly advised not to use real tokens in
documentation even if the probability of a token being exploited is low.

You can use these fake tokens as examples:

| Token type            | Token value                                                        |
|:----------------------|:-------------------------------------------------------------------|
| Personal access token | `<your_access_token>`                                             |
| Application ID        | `2fcb195768c39e9a94cec2c2e32c59c0aad7a3365c10892e8116b5d83d4096b6` |
| Application secret    | `04f294d1eaca42b8692017b426d53bbc8fe75f827734f0260710b83a556082df` |
| CI/CD variable        | `Li8j-mLUVA3eZYjPfd_H`                                             |
| Specific runner token | `yrnZW46BrtBFqM7xDzE7dddd`                                         |
| Shared runner token   | `6Vk7ZsosqQyfreAxXTZr`                                             |
| Trigger token         | `be20d8dcc028677c931e04f3871a9b`                                   |
| Webhook secret token  | `6XhDroRcYPM5by_h-HLY`                                             |
| Health check token    | `Tu7BgjR9qeZTEyRzGG2P`                                             |
| Request profile token | `7VgpS4Ax5utVD2esNstz`                                             |

### Usage list
<!-- vale off -->

| Usage                 | Guidance |
|-----------------------|----------|
| above                 | Try to avoid extra words when referring to an example or table in a documentation page, but if required, use **previously** instead. |
| admin, admin area     | Use **administration**, **administrator**, **administer**, or **Admin Area** instead.  |
| allow, enable         | Try to avoid, unless you are talking about security-related features. For example, instead of "This feature allows you to create a pipeline," use "Use this feature to create a pipeline." This phrasing is more active and is from the user perspective, rather than the person who implemented the feature. [View details](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/a/allow-allows). |
| and/or                | Use **or** instead, or another sensible construction. |
| below                 | Try to avoid extra words when referring to an example or table in a documentation page, but if required, use **following** instead. |
| currently             | Do not use when talking about the product or its features. The documentation describes the product as it is today. |
| easily                | Do not use. If the user doesn't find the process to be these things, we lose their trust. |
| e.g.                  | Do not use Latin abbreviations. Use **for example**, **such as**, **for instance**, or **like** instead. |
| future tense          | When possible, use present tense instead. For example, use `after you execute this command, Takeoff displays the result` instead of `after you execute this command, Takeoff will display the result`. [Present tense](https://developers.google.com/style/tense) is the most brief form of English, is direct, conveys authority and confidence, and does not attmpt to predict the future. |
| handy                 | Do not use. If the user doesn't find the process to be these things, we lose their trust. |
| I                     | Do not use first-person singular. Use **you**, **we**, or **us** instead. |
| i.e.                  | Do not use Latin abbreviations. Use **that is** instead. |
| jargon                | Do not use software or grocery industry jargon where possible. Define the term or [link to a definition](#links-to-external-documentation). |
| may, might            | **Might** means something has the probability of occurring. **May** gives permission to do something. Consider **can** instead of **may**. |
| me, myself, mine      | Do not use first-person singular. Use **you**, **we**, or **us** instead. |
| please                | Do not use. For details, see the [Microsoft style guide](https://docs.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/p/please). |
| profanity             | Do not use. Doing so may negatively affect other users and contributors, which is contrary to values of diversity, inclusion, and belonging. |
| simply                | Do not use. If the user doesn't find the process to be these things, we lose their trust. |
| slashes               | Instead of **and/or**, use **or** or another sensible construction. This rule also applies to other slashes, like **follow/unfollow**. Some exceptions (like **CI/CD**) are allowed. |
| subgroup              | Use instead of `sub-group`. |
| that                  | Do not use. Example: `the file that you save` can be `the file you save`. |
| useful                | Do not use. If the user doesn't find the process to be these things, we lose their trust. |
| utilize               | Do not use. Use **use** instead. It's more succinct and easier for non-native English speakers to understand. It also does not translate well to other languages. |
| via                   | Do not use Latin abbreviations. Use **with**, **through**, or **by using** instead.  |

### Contractions

Contractions are encouraged, and can create a friendly and informal tone,
especially in tutorials and instructional documentation.

Some contractions, however, should be avoided:

- Do not use [the word Takeoff in a contraction](#trademark).

- Do not use contractions with a proper noun and a verb. For example:

  | Do                                       | Don't                                   |
  |------------------------------------------|-----------------------------------------|
  | Canada is establishing X.                | Canada's establishing X.                |


- Do not use contractions when you need to emphasize a negative. For example:

  | Do                                       | Don't                                   |
  |------------------------------------------|-----------------------------------------|
  | Do *not* install X with Y.               | *Don't* install X with Y.               |


- Do not use contractions in reference documentation. For example:

  | Do                                       | Don't                                   |
  |------------------------------------------|-----------------------------------------|
  | Do *not* set a limit greater than 1000.  | *Don't* set a limit greater than 1000.  |
  | For `parameter1`, the default is 10.     | For `parameter1`, the default's 10.     |


- Avoid contractions in error messages. Examples:
  

  | Do                                       | Don't                                   |
  |------------------------------------------|-----------------------------------------|
  | Requests to localhost are not allowed.   | Requests to localhost aren't allowed.   |
  | Specified URL cannot be used.            | Specified URL can't be used.            |

## Text

- [Write in Markdown](#markdown) for this handbook.
- Splitting long lines (preferably up to 100 characters) can make it easier to
  provide feedback on small chunks of text.
- Insert an empty line for new paragraphs.
- Insert an empty line between different markups (for example, after every
  paragraph, header, list, and so on). Example:

  ```markdown
  ## Header

  Paragraph.

  - List item 1
  - List item 2
  ```

### Emphasis

- Use double asterisks (`**`) to mark a word or text in bold (`**bold**`).
- Use underscore (`_`) for text in italics (`_italic_`).
- Use greater than (`>`) for blockquotes.

### Punctuation

Follow these guidelines for punctuation:

| Rule                                                             | Example                                                |
|------------------------------------------------------------------|--------------------------------------------------------|
| Avoid semicolons. Use two sentences instead.                     | _That's the way that the world goes 'round. You're up one day and the next you're down._
| Always end full sentences with a period.                         | _For a complete overview, read through this document._ |
| Always add a space after a period when beginning a new sentence. | _For a complete overview, check this doc. For other references, check out this guide._ |
| Do not use double spaces.  | --- |
| Do not use tabs for indentation. Use spaces instead. You can configure your code editor to output spaces instead of tabs when pressing the tab key. | --- |
| Use serial commas (_Oxford commas_) before the final _and_ or _or_ in a list of three or more items.  | _You can create new issues, merge requests, and milestones._ |
| Always add a space before and after dashes when using it in a sentence (for replacing a comma, for example). | _You should try this - or not._ |
| Always use lowercase after a colon.                              | Linked issues: a way to create a relationship between issues. |


### Placeholder text

You might want to provide a command or configuration that
uses specific values.

In these cases, use [`<` and `>`](https://en.wikipedia.org/wiki/Usage_message#Pattern)
to call out where a reader must replace text with their own value.

For example:

```shell
cp <your_source_directory> <your_destination_directory>
```

### Keyboard commands

Use the HTML `<kbd>` tag when referring to keystroke presses. For example:

```plaintext
To stop the command, press <kbd>Control</kbd>+<kbd>C</kbd>.
```

When the docs are generated, the output is:

To stop the command, press <kbd>Control</kbd>+<kbd>C</kbd>.

### Spaces between words

Use only standard spaces between words. The search engine for the documentation
website doesn't split words separated with
[non-breaking spaces](https://en.wikipedia.org/wiki/Non-breaking_space) when
indexing, and fails to create expected individual search terms. Tests that search
for certain words separated by regular spaces can't find words separated by
non-breaking spaces.

## Lists

- Always start list items with a capital letter, unless they're parameters or
  commands that are in backticks, or similar.
- Always leave a blank line before and after a list.
- Begin a line with spaces (not tabs) to denote a [nested sub-item](#nesting-inside-a-list-item).

### Ordered vs. unordered lists

Only use ordered lists when their items describe a sequence of steps to follow.

Do:

```markdown
These are the steps to do something:

1. First, do the first step.
1. Then, do the next step.
1. Finally, do the last step.
```

Don't:

```markdown
This is a list of available features:

1. Feature 1
1. Feature 2
1. Feature 3
```

### Markup

- Use dashes (`-`) for unordered lists instead of asterisks (`*`).
- Prefix `1.` to every item in an ordered list. When rendered, the list items
  display with sequential numbering.

### Punctuation

- Don't add commas (`,`) or semicolons (`;`) to the ends of list items.
- Only add periods to the end of a list item if the item consists of a complete
  sentence (with a subject and a verb).
- Be consistent throughout the list: if the majority of the items do not end in
  a period, do not end any of the items in a period, even if they consist of a
  complete sentence. The opposite is also valid: if the majority of the items
  end with a period, end all with a period.
- Separate list items from explanatory text with a colon (`:`). For example:

  ```markdown
  The list is as follows:

  - First item: this explains the first item.
  - Second item: this explains the second item.
  ```

**Examples:**

Do:

- First list item
- Second list item
- Third list item

Don't:

- First list item
- Second list item
- Third list item.

Do:

- Let's say this is a complete sentence.
- Let's say this is also a complete sentence.
- Not a complete sentence.

Don't (vary use of periods; majority rules):

- Let's say this is a complete sentence.
- Let's say this is also a complete sentence.
- Not a complete sentence

### Nesting inside a list item

It's possible to nest items under a list item, so that they render with the same
indentation as the list item. This can be done with:

- [Code blocks](#code-blocks)
- [Blockquotes](#blockquotes)
- [Alert boxes](#alert-boxes)
- [Images](#images)

Items nested in lists should always align with the first character of the list
item. In unordered lists (using `-`), this means two spaces for each level of
indentation:

````markdown
- Unordered list item 1

  A line nested using 2 spaces to align with the `U` above.

- Unordered list item 2

  > A quote block that will nest
  > inside list item 2.

- Unordered list item 3

  ```plaintext
  a code block that nests inside list item 3
  ```

- Unordered list item 4

  ![an image that will nest inside list item 4](image.png)
````

For ordered lists, use three spaces for each level of indentation:

````markdown
1. Ordered list item 1

   A line nested using 3 spaces to align with the `O` above.

1. Ordered list item 2

   > A quote block that will nest
   > inside list item 2.

1. Ordered list item 3

   ```plaintext
   a code block that nests inside list item 3
   ```

1. Ordered list item 4

   ![an image that will nest inside list item 4](image.png)
````

You can nest full lists inside other lists using the same rules as above. If you
want to mix types, that's also possible, if you don't mix items at the same
level:

```markdown
1. Ordered list item one.
1. Ordered list item two.
   - Nested unordered list item one.
   - Nested unordered list item two.
1. Ordered list item three.

- Unordered list item one.
- Unordered list item two.
  1. Nested ordered list item one.
  1. Nested ordered list item two.
- Unordered list item three.
```

## Tables

Tables should be used to describe complex information in a straightforward
manner. Note that in many cases, an unordered list is sufficient to describe a
list of items with a single, simple description per item. But, if you have data
that's best described by a matrix, tables are the best choice.

### Creation guidelines

To keep tables accessible and scannable, tables should not have any
empty cells. If there is no otherwise meaningful value for a cell, enter
*N/A* (for 'not applicable') or *none* so that readers do not get the impression that the blank cell indicates a mistake.

To help tables be easier to maintain, consider adding additional spaces to the
column widths to make them consistent. For example:

```markdown
| App name | Description          | Requirements   |
|:---------|:---------------------|:---------------|
| App 1    | Description text 1.  | Requirements 1 |
| App 2    | Description text 2.  | None           |
```

Consider installing a plugin or extension in your editor for formatting tables:

- [Markdown Table Prettifier](https://marketplace.visualstudio.com/items?itemName=darkriszty.markdown-table-prettify) for Visual Studio Code
- [Markdown Table Formatter](https://packagecontrol.io/packages/Markdown%20Table%20Formatter) for Sublime Text
- [Markdown Table Formatter](https://atom.io/packages/markdown-table-formatter) for Atom

## Quotes

Valid for Markdown content only, not for front matter entries:

- Standard quotes: double quotes (`"`). Example: "This is wrapped in double
  quotes".
- Quote inside a quote: double quotes (`"`) wrap single quotes (`'`). Example:
  "This sentence 'quotes' something in a quote".


## Headings

- Add _only one H1_ in each document, by adding `#` at the beginning of
  it (when using Markdown). The `h1` becomes the document `<title>`.
- Start with an `h2` (`##`), and respect the order `h2` > `h3` > `h4` > `h5` > `h6`.
  Never skip the hierarchy level, such as `h2` > `h4`
- Avoid putting numbers in headings. Numbers shift, hence documentation anchor
  links shift too, which eventually leads to dead links. If you think it is
  compelling to add numbers in headings, make sure to at least discuss it with
  someone in the Merge Request.
- Avoid using symbols and special characters in headers. Whenever possible, they should be plain and short text.
- When possible, avoid including words that might change in the future. Changing
  a heading changes its anchor URL, which affects other linked pages.
- When introducing a new document, be careful for the headings to be
  grammatically and syntactically correct. Mention this in your merge request if you need review.
  This is to ensure that no document with a wrong heading is going live without an
  audit, thus preventing dead links and redirection issues when corrected.
- Leave exactly one blank line before and after a heading.
- Do not use links in headings.
- Our documentation site search engine prioritizes words used in headings and
  subheadings. Make your subheading titles clear, descriptive, and complete to help
  users find the right example, as shown in the section on [heading titles](#heading-titles).
- See [Capitalization](#capitalization) for guidelines on capitalizing headings.

### Heading titles

Keep heading titles clear, direct, and brief. Make every word count. To accommodate
search engine optimization (SEO), use the imperative, where possible.

| Do                                    | Don't                                                       |
|:--------------------------------------|:------------------------------------------------------------|
| Configure GDK                         | Configuring GDK                                             |
| Takeoff Release and Maintenance Policy | This section covers the Takeoff Release and Maintenance Policy |
| Backport to older releases            | Backporting to older releases                               |
| Takeoff Pages examples                 | Examples                                                    |

For guidelines on capitalizing headings, see the section on [capitalization](#capitalization).

NOTE:
If you change an existing title, be careful. In-page [anchor links](#anchor-links),
links in the Takeoff application, and links from external sites can break.

### Anchor links

Headings generate anchor links when rendered. `## This is an example` generates
the anchor `#this-is-an-example`.

Keep in mind that there are many links between documentation pages on this site
and anchor links to take the user to the right spot. When you change
a heading, search for the old
anchor. If you do not fix these links, the handbook team will require this upon merge request.

Important:

- Avoid crosslinking documentation to headings unless you need to link to a
  specific section of the document. This avoids breaking anchors in the
  future in case the heading is changed.
- In general, avoid changing headings if possible.
- Do not link to `h1` headings. Instead, link to pages.


## Links

Links are important in Takeoff documentation. Use links instead of
summarizing to help preserve a [single source of truth](#documentation-is-the-single-source-of-truth-ssot).

We include guidance for links in these categories:

- How to set up [anchor links](#anchor-links) for headings.
- How to set up [criteria](#basic-link-criteria) for configuring a link.
- How to set up [links to internal documentation](#links-to-internal-documentation)
  for cross-references.
- How to set up [links to external documentation](#links-to-external-documentation)
  for authoritative sources.
- When to use [links requiring permissions](#links-requiring-permissions).
- How to set up a [link to a video](#link-to-video).
- How to [include links with version text](#where-to-put-version-text).
- How to [link to specific lines of code](#link-to-specific-lines-of-code)

### Basic link criteria

- Use inline link Markdown markup `[Text](https://example.com)`.
  It's easier to read, review, and maintain. _Do not_ use `[Text][identifier]`.

- Use [meaningful anchor texts](https://www.futurehosting.com/blog/links-should-have-meaningful-anchor-text-heres-why/).
  For example, instead of writing something like `Read more about Takeoff [here](LINK)`,
  write `Read more about [Takeoff](LINK)`.

### Links to internal documentation

NOTE:
_Internal_ refers to documentation in the same project. If there is a need to link to
documentation in separate projects (for example, linking to Confluence documentation
from Takeoff documentation), you must use absolute URLs.

Do not use absolute URLs like `https://docs.Takeoff.com/ee/index.html` to
cross-link to other documentation in the same project. Use relative links to
the file, like `../index.md`. (These are converted to HTML when the site is
rendered.)

Relative linking enables crosslinks to work:

- in Review Apps and local previews.
- when working on the documentation locally, so you can verify that they work as
  early as possible in the process.
- in the Takeoff user interface when browsing doc files in their respective
  repositories. For example, the links displayed at
  `https://Takeoff.com/Takeoff-org/Takeoff/-/blob/master/doc/README.md`.

To link to internal documentation:

- Use relative links to Markdown files in the same repository.
- Prefer to use hugo's [`relref`](https://gohugo.io/functions/relref/) feature
  to make sure your links don't break. For example: `[my-cool-link]({{</* relref path="../my-cool-page.md" */>}})`
  - Put anchors within the `path`. For example: `[my-cool-link]({{</* relref path="../my-cool-page.md#my-anchor" */>}})`
- Do not use absolute URLs or URLs from `Takeoff.com`.
- Use `../` to navigate to higher-level directories.
- Don't prepend `./` to links to files or directories. To link to a file in the
  same directory or one of its sub-directories, use the syntax `path/to/file.md`.
- Don't link relative to root. For example, `/engineering-handbook/content/.../index.md`.

  Don't:

  - `https://engineering-handbook.takeoff.com/docs/engineering/cicd.html`
  - `/engineering-handbook/docs/engineering/cicd.html`
  - `./cicd.md`

  Do: `../../docs/engineering/cicd.md`

- Always add the filename `file.md` at the end of the link with the `.md`
  extension, not `.html`.

  Don't:

  - `../../merge_requests/`
  - `../../issues/tags.html`
  - `../../issues/tags.html#stages`

  Do:

  - `../../merge_requests/index.md`
  - `../../issues/tags.md`
  - `../../issues/tags.md#stages`
  - `issues/tags.md`


### Links to external documentation

When describing interactions with external software, it's often helpful to
include links to external documentation. When possible, make sure that you're
linking to an [**authoritative** source](#authoritative-sources). For example,
if you're describing a feature in Google Cloud Platform, include a link
to official Google documentation.

### Authoritative sources

When citing external information, use sources that are written by the people who
created the item or product in question. These sources are the most likely to be
accurate and remain up to date.

Examples of authoritative sources include:

- Specifications, such as a [Request for Comments](https://www.ietf.org/standards/rfcs/)
  document from the Internet Engineering Task Force.
- Official documentation for a product. For example, if you're setting up an
  interface with the Google OAuth 2 authorization server, include a link to
  Google's documentation.
- Official documentation for a project. For example, if you're citing NodeJS
  functionality, refer directly to [NodeJS documentation](https://nodejs.org/en/docs/).
- Books from an authoritative publisher.

Examples of sources to avoid include:

- Personal blog posts.
- Non-trustworthy articles.
- Discussions on forums such as Stack Overflow.
- Documentation from a company that describes another company's product.

While many of these sources to avoid can help you learn skills and or features,
they can become obsolete quickly. Nobody is obliged to maintain any of these
sites. Therefore, we should avoid using them as reference literature.

NOTE:
Non-authoritative sources are acceptable only if there is no equivalent
authoritative source. Even then, focus on non-authoritative sources that are
extensively cited or peer-reviewed.

### Links requiring permissions

Don't link directly to:

- Slack discussions.
- Jira issues if a more formal source of truth exists.
- Locations that require special permissions to view.

These fail for:

- Those without sufficient permissions.
- Automated link checkers.

Instead:

- To reduce confusion, mention in the text that the information is either:
   - Requires special permission to a project to view.
- Provide a link in back ticks (`` ` ``) so that those with access to the issue
  can navigate to it.

### Link to specific lines of code

When linking to specific lines in a file, link to a commit instead of to the
branch. Lines of code change over time. Linking to a line by using
the commit link ensures the user lands on the line you're referring to. See [GitHub's documentation](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files) for more details about obtaining permalinks.

## Navigation

When documenting navigation through the user interface:

- Use the exact wording as shown in the UI, including any capital letters as-is.
- Use bold text for navigation items.

## Images

Images, including screenshots, can help a reader better understand a concept.
However, they can be hard to maintain, and should be used sparingly.

Before including an image in the documentation, ensure it provides value to the
reader, with the exception of landing page images.

### Capture the image

Use images to help the reader understand where they are in a process, or how
they need to interact with the application.

When you take screenshots:

- _Capture the most relevant area of the page._ Don't include unnecessary white
  space or areas of the page that don't help illustrate the point. 
- _Keep it small._ If you don't need to show the full width of the screen, don't.
  A value of 1000 pixels is a good maximum width for your screenshot image.
- _Be consistent._ Coordinate screenshots with the other screenshots already on
  a documentation page. For example, if other screenshots include certain arrows or formatting, use the same formatting in all images.

### Save the image

- Save the image with a lowercase filename that's descriptive of the feature
  or concept in the image. If the image is of the Takeoff user interface, append the
  Takeoff version to the filename, based on this format:
  `image_name_mm_yyyy.png`. For example `tomui_orderspage_09_2021.png`
- Place images in a separate directory named `static/` in a sub-directory structure that mirrors the location of the `.md` document that you're working on is located.
- Consider using PNG images instead of JPEG.
- [Compress all PNG images](#compress-images).
- Compress GIFs with <https://ezgif.com/optimize> or similar tool.
- Images should be used (only when necessary) to _illustrate_ the description
  of a process, not to _replace_ it.
- Max image size: 100KB (GIFs included).
- See also how to link and embed [videos](#videos) to illustrate the
  documentation.

### Add the image link to content

The Markdown code for including an image in a document is:
`![Image description which will be the alt tag](static/.../document_image_title_vX_Y.png)`

The image description is the alt text for the rendered image on the
documentation site. For accessibility and SEO, use [descriptions](https://webaim.org/techniques/alttext/)
that:

- Are accurate, succinct, and unique.
- Don't use _image of…_ or _graphic of…_ to describe the image.

### Compress images

You should always compress any new images you add to the documentation. One
known tool is [`pngquant`](https://pngquant.org/), which is cross-platform and
open source. Install it by visiting the official website and following the
instructions for your OS.

## Videos

Embedding videos to the documentation is
encouraged, unless the video is outdated. Videos should not replace
documentation, but complement or illustrate it. If content in a video is
fundamental to a concept, but isn't adequately
covered in the documentation, you should add this detail to the documentation text.

Do not upload videos to the GitHub repositories. [Link](#link-to-video) or
[embed](#embed-videos) them instead.

### Link to video

To link out to a video, include a YouTube icon so that readers can scan the page
for videos before reading:

```markdown
<i class="fa fa-youtube-play youtube" aria-hidden="true"></i>
For an overview, see [Video Title](link-to-video).
```

You can link any up-to-date video that's useful to the Takeoff user.

### Embed videos

The [Takeoff documentation site](https://engineering-handbook.takeoff.org) supports embedded
videos.

To embed a video, follow the [Hugo Shortcode instructions](https://gohugo.io/content-management/shortcodes/) based on the location where the video is hosted. 


## Code blocks

- Always wrap code added to a sentence in inline code blocks (`` ` ``).
  For example, `.Takeoff-ci.yml`, `git add .`, `CODEOWNERS`, or `only: [master]`.
  File names, commands, entries, and anything that refers to code should be
  added to code blocks. To make things easier for the user, always add a full
  code block for things that can be useful to copy and paste, as they can do it
  with the button on code blocks.
- HTTP methods (`HTTP POST`) and HTTP status codes, both full (`404 File Not Found`)
  and abbreviated (`404`), should be wrapped in inline code blocks when used in sentences.
  For example: Send a `DELETE` request to delete the runner. Send a `POST` request to create one.
- Add a blank line above and below code blocks.
- When providing a shell command and its output, prefix the shell command with `$`
  and leave a blank line between the command and the output.
- When providing a command without output, don't prefix the shell command with `$`.
- If you need to include triple backticks inside a code block, use four backticks
  for the code block fences instead of three.
- For regular fenced code blocks, always use a highlighting class corresponding to
  the language for better readability. Examples: 

  ````markdown
  ```ruby
  Ruby code
  ```

  ```javascript
  JavaScript code
  ```

  ```markdown
  [Markdown code example](example.md)
  ```

  ```plaintext
  Code or text for which no specific highlighting class is available.
  ```
  ````

Syntax highlighting is required for fenced code blocks added to the Handbook
documentation. Refer to the Hugo documentation for more information about how to use the [Syntax Highlighting shortcode](https://gohugo.io/content-management/syntax-highlighting/).


<!-- | Preferred language tags | Language aliases and notes                                                   |
|-------------------------|------------------------------------------------------------------------------|
| `asciidoc`              |                                                                              |
| `dockerfile`            | Alias: `docker`.                                                             |
| `elixir`                |                                                                              |
| `erb`                   |                                                                              |
| `golang`                | Alias: `go`.                                                                 |
| `graphql`               |                                                                              |
| `haml`                  |                                                                              |
| `html`                  |                                                                              |
| `ini`                   | For some simple configuration files that are not in TOML format.             |
| `javascript`            | Alias `js`.                                                                  |
| `json`                  |                                                                              |
| `markdown`              | Alias: `md`.                                                                 |
| `mermaid`               |                                                                              |
| `nginx`                 |                                                                              |
| `perl`                  |                                                                              |
| `php`                   |                                                                              |
| `plaintext`             | Examples with no defined language, such as output from shell commands or API calls. If a code block has no language, it defaults to `plaintext`. Alias: `text`.|
| `prometheus`            | Prometheus configuration examples.                                           |
| `python`                |                                                                              |
| `ruby`                  | Alias: `rb`.                                                                 |
| `shell`                 | Aliases: `bash` or `sh`.                                                     |
| `sql`                   |                                                                              |
| `toml`                  | Runner configuration examples, and other TOML-formatted configuration files. |
| `typescript`            | Alias: `ts`.                                                                 |
| `xml`                   |                                                                              |
| `yaml`                  | Alias: `yml`.                                                                | -->


## Alert, Note, and Warning boxes

Our Hugo site theme supports Alert, Note, and Warning boxes. For example, a Warning box can be created as follows: 

```go-html-template
{{%/* alert title="Warning" color="warning" */%}}
This is a warning.
{{%/* /alert */%}}

```
renders to:

{{% alert title="Warning" color="warning" %}}
This is a warning.
{{% /alert %}}

See the [theme documentation](https://www.docsy.dev/docs/adding-content/shortcodes/#alert) for more details about insterting these boxes. 

### Alert

Use alert boxes to call attention to information.

### Note

Use notes sparingly. Too many notes can make topics difficult to scan.

Instead of adding a note:

- Re-write the sentence as part of a paragraph.
- Put the information into its own paragraph.
- Put the content under a new subheading.

### Warning

Use a warning to indicate deprecated features, or to provide a warning about
procedures that have the potential for data loss.

## Blockquotes

For highlighting a text inside a blockquote, use this format:

```markdown
> This is a blockquote.
```

It renders on the documentation site as:

> This is a blockquote.

If the text spans multiple lines, you can split them.

For multiple paragraphs, use the symbol `>` before every line:

```markdown
> This is the first paragraph.
>
> This is the second paragraph.
>
> - This is a list item
> - Second item in the list
```

It renders on the Takeoff documentation site as:

> This is the first paragraph.
>
> This is the second paragraph.
>
> - This is a list item
> - Second item in the list

## Terms

To maintain consistency through Takeoff documentation, use these styles and terms.

### Merge requests (MRs)

Merge requests allow you to exchange changes you made to source code and
collaborate with other people on the same project.

- Use lowercase _merge requests_ regardless of whether referring to the feature
  or individual merge requests.

As noted in the Takeoff [Writing Style Guidelines](https://about.Takeoff.com/handbook/communication/#writing-style-guidelines),
if you use the _MR_ acronym, expand it at least once per document page.
Typically, the first use would be phrased as _merge request (MR)_ with subsequent
instances being _MR_.

Examples:

- "We prefer Takeoff merge requests".
- "Open a merge request to fix a broken link".
- "After you open a merge request (MR), submit your MR for review and approval".

### Describe UI elements

Follow these styles when you're describing user interface elements in an
application:

- For elements with a visible label, use that label in bold with matching case.
  For example, `the **Cancel** button`.
- For elements with a tooltip or hover label, use that label in bold with
  matching case. For example, `the **Add status emoji** button`.
- For elements or areas that do not have a label, search existing documentation for instances where the element or area has already been given a name. If no other documentation names the element or area, name the area after it's purpose. For example, a panel containing order details should be named the "Order Details area." If the element is a button or other control, bold and capitalize the name. If it is an area, capitalize it but do not bold the name.   

### Verbs for UI elements

Use these verbs for specific uses with user interface
elements:

| Recommended         | Used for                              | Replaces                   |
|:--------------------|:--------------------------------------|:---------------------------|
| _select_ or _tap_   | buttons, links, menu items            | "click, "press," "hit"     |
| _select_ or _clear_ | checkboxes                            | "enable", "click", "press" |
| _expand_            | expandable sections, dropdowns        | "open"                     |

### Other Verbs

| Recommended | Used for                        | Replaces              |
|:------------|:--------------------------------|:----------------------|
| _go to_     | making a browser go to location | "navigate to", "open" |


### Versions in the past or future

When describing functionality available in past or future versions, use:

- Earlier, and not older or before.
- Later, and not newer or after.

## Products and features

Refer to the information in this section when describing products and features
in the Takeoff product documentation.

### Avoid line breaks in names

If a feature or product name contains spaces, don't split the name with a line break.
When names change, it is more complicated to search or grep text that has line breaks.

## Style Guide Requests or Suggestions

If you have a request, idea, correction, suggestion, or anything else you want to submit, [create a ticket on the handbook board](https://takeofftech.atlassian.net/secure/CreateIssue.jspa?issuetype=10100&pid=10261).

[hugo-shortcodes]: https://gohugo.io/content-management/shortcodes/
[docsy-shortcodes]: https://www.docsy.dev/docs/adding-content/shortcodes/
[custom-shortcodes]: layouts/shortcodes

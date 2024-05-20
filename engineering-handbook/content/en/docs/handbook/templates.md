---
title: "Documentation Templates"
linkTitle: "Content Templates"
date: 2017-07-13
weight: 3
description: >
  Using templates helps us break down our content into consistent, familiar structures that promote easy creation and better information retention.  
---

Rather than providing traditional large templates that force a specific structre, at Takeoff we use smaller **topic** templates that can be can be combined and duplicated within articles however we want. In general, each page in our docset contains multiple topics.

Loosely derived from an information organization specification known as [DITA](https://en.wikipedia.org/wiki/Darwin_Information_Typing_Architecture), these smaller templates allow information to be consistent, while also being modular. Organizing our information this way allows us to iterate our Handbook structure over time. 

# Topic types

All documentation must be created starting from one of the following topic templates, and because topics represent smaller chunks of information, they can be **placed together on pages in any order**. For example, you can include a concept, and multiple task or reference topics together within a large, complex explanation.

  - [Landing pages](#landing-pages)
  - [Concept](#concept)
  - [Task](#task)
  - [Reference](#reference)
  - [Troubleshooting](#troubleshooting)


## Landing pages

Landing pages are topics that group other topics and help the reader quickly understand the contents of a given section.

-Within our handbook, the left navigation bar is only two levels deep (by design), and so we use landing page topics to navigate the documentation.

-These topics can also help other users find the most important topics in a section.

Landing page topics should be in this format:

```markdown
# Title (a noun, like "CI/CD" or "Data Model")

Brief introduction to the concept or product area.
Include the reason why someone would use this thing.

- Bulleted list of important related topics.
- These links are needed because users of in-product help do not have left navigation.
```

## Concept

A concept topic introduces a single feature or concept.

A concept should answer the questions:

- What is this?
- Why would I use it?

Think of everything someone might want to know if they've never heard of this topic before.

Don't tell them **how** to do this thing. Tell them **what it is**.

If you start describing another topic, start a new concept and link to it.

Also, do not use "Overview" or "Introduction" for the topic title. Instead,
use a noun or phrase that someone would search for.

Concept topics should be in this format:

```markdown
# Title (a noun, like "Widgets")

A paragraph that explains what this thing is.

Another paragraph that explains what this thing is.

Remember, if you start to describe about another concept, stop yourself.
Each concept topic should be about one concept only.
```

## Task

A task topic gives instructions for how to complete a procedure.

Task topics should be in this format:

```markdown
# Title (starts with an active verb, like "Create a widget" or "Delete a widget")

Do this task when you want to...

Prerequisites (optional):

- Thing 1
- Thing 2
- Thing 3

To do this task:

1. Location then action. (Go to this menu, then select this item.)
1. Another step.
1. Another step.

Task result (optional). Next steps (optional).
```

Here is an example.

```markdown
# Create an issue

Create an issue when you want to track bugs or future work.

Prerequisites:

- A minimum of Contributor access to a project in Takeoff.

To create an issue:

1. Go to **Issues > List**.
1. In the top right, select **New issue**.
1. Complete the fields. (If you have a reference topic that lists each field, link to it here.)
1. Select **Create issue**.

The issue is created. You can view it by going to **Issues > List**.
```

If you have several tasks on a page that share prerequisites, you can make a
reference topic with the title **Prerequisites**, and link to it.

## Reference

A reference topic provides information in an easily-scannable format,
like a table or list. It's similar to a dictionary or encyclopedia entry.

```markdown
# Title (a noun, like "Pipeline settings" or "Administrator options")

Introductory sentence.

| Setting | Description |
|---------|-------------|
| **Name** | Descriptive sentence about the setting. |
```

If a feature or concept has its own prerequisites, you can use the reference
topic type to create a **Prerequisites** header for the information.

## Troubleshooting

Troubleshooting topics can be one of two categories:

- **Troubleshooting task.** This topic is written the same as a [standard task topic](#task).
  For example, "Run debug tools" or "Verify syntax."
- **Troubleshooting reference.** This topic has a specific format.

Troubleshooting reference topics should be in this format:

```markdown
# Title (the error message or a description of it)

You might get an error that states <error message>.

This issue occurs when...

The workaround is...
```

For the topic title:

- Consider including at least a partial error message in the title.
- Use fewer than 70 characters.

Remember to include the complete error message in the topics content if it is
not complete in the title.


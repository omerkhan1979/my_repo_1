---
title: "Design Tokens and where to find them"
linkTitle: "Design Tokens and where to find them"
date: 2021-10-26
type: blog
categories: ["article"]
tags: ["article", "ui-design"]
weight: 1
author: "Maria Tsampas"
---

# Introduction

The purpose of this document is to provide some onboarding into Figma, the tool that designers use to create design specs for handoff to engineers. The document will provide an intro to Figma, specifically for developers, as well as an overview of design systems and tokens and a walkthrough of Takeoff’s design system library.

As a developer, you will be tasked with creating new components that the designers spec out in Figma. It is helpful for you to know a little about Figma so that you can properly inspect each component to get specifics on padding, color, tokens used, etc.

## Takeoff Design System File

Use this link to open up Takeoff’s design system Figma file. Everyone in the Takeoff organization should already have access to this, but if you don’t, please request access when prompted.

Figma works best with the downloaded desktop app, please download [here](https://www.figma.com/downloads/) if you haven’t already.

[Takeoff Design System 2021](https://www.figma.com/file/KBMNkPdPPPEx1HIUhvqTl4/Takeoff-Design-System-2021?node-id=37%3A142)

## General Figma Intro

If this is your first time using Figma, read this [quick intro](https://trydesignlab.com/figma-101-course/introduction-to-figma/) to get the lay of the land.

## Figma for Developers

Figma is a tool designed to improve collaboration between product, design, and engineering. There are various features in Figma that make it easy for developers to see actual code for designed elements to build exact to spec.

In Figma, the Code panel offers an easy way to extract code information from a specific page element. The code will be displayed by clicking on a layer.

Currently, Figma supports CSS, Swift, and XML, but notice that most of the code available involves only visual properties and spacing. No Javascript or other logic is exported.

The right hand panel provides code data for color values, typography, position, and sizes. Additionally, designers have the option to add a text description to styles and components, which will be available in the same place.

Further reading:

- [Tips for Figma developers](https://www.figma.com/best-practices/tips-on-developer-handoff/an-overview-of-figma-for-developers/#code-inspection-and-layout-measurements)

![](/images/en/docs/Learning/ui-ux/design-tokens-figma-1.png)

## Design Systems and Tokens

{{% pageinfo color="primary" %}}
_A design system is a set of standards to manage design at scale by reducing redundancy while creating a shared language and visual consistency across different pages and channels._
{{% /pageinfo %}}

[Design Systems 101](https://www.nngroup.com/articles/design-systems-101/)

_Design tokens_ are the visual design atoms of the design system — specifically, they are named entities that store visual design attributes. We use them in place of hard-coded values (such as hex values for color or pixel values for spacing) in order to maintain a scalable and consistent visual system for UI development.

Further reading:

- [UI/UX Design Tokens - Confluence documentation](https://takeofftech.atlassian.net/wiki/spaces/UIUX/pages/3128066069)
- [UI/UX Design Tokens - Introduction](https://docs.google.com/presentation/d/1160whlGJ1_3cdHyH8nCDzqrFw7vlqP1AainqCBMDZTI/edit?usp=sharing)
- [Design Tokens in Figma Article](https://www.headway.io/blog/design-tokens-in-figma-setting-up-your-design-system)

## Design System Figma Space Walkthrough:

[Takeoff Design System 2021](https://www.figma.com/file/KBMNkPdPPPEx1HIUhvqTl4/Takeoff-Design-System-2021?node-id=37%3A142) is our design system space in Figma.

![](/images/en/docs/Learning/ui-ux/design-tokens-overview.png)
_Design tokens Overview_

![](/images/en/docs/Learning/ui-ux/design-tokens-left-panel.png)
_Left hand “Page” panel_

When you open up the Figma file, you will have the option to go through the different pages we have set up in our design system in this left hand panel.

In this first section, you can find the design tokens page as well as some copy guidelines as well as some old components from our previous design system as a hold over before we move them into this file.

In _Component Specs_ section, you can find finished and fleshed out specs of components in our design system (e.g., buttons, checkboxes, chips, etc.)

This _Work in Progress_ section is where the designers are currently speccing out components and developers should not utilize these pages as final specs.

![](/images/en/docs/Learning/ui-ux/design-tokens-button-example.png)
_Buttons spec example_

When you click into a component page, you’ll see specced out components. In the example above, the designer has specced out column headers into the different states available (e.g., :enabled, :selectable, :selected, etc.).

In most component specs, we will outline the different design tokens that make up each part of the design. Use these to help you develop the component correctly using our design token library.

![](/images/en/docs/Learning/ui-ux/design-tokens-inspect-panel.png)
_Right hand “Inspect” panel for code inspection_

![](/images/en/docs/Learning/ui-ux/design-tokens-inspect-panel-close-up.png)

_“Inspect” panel close up_

Don’t forget that you can use the Inspect panel on the right side of Figma to dive into the specifics of a component!

## Creating a new shared component

Developers may be tasked with creating a new component for our design system and should utilize this guidance document to do so: [Guidance: Creating a new shared component](https://takeofftech.atlassian.net/wiki/spaces/UIUX/pages/3234725936)

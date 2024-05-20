---
title: "How-to find and preview Core UI reusable components"
linkTitle: "How to preview Core UI components"
date: 2021-10-26
type: docs
tags: ["how-to"]
weight: 8
---

In Takeoff, _Core UI_ and _React Native Core UI_ packages, provide a set of components that matches the official designs from Takeoff.

If you are developing a new page or Native component that uses any of these reusable components, it is recommended to import these from these libraries.

This will help as these components already provide the styling and behaviour required.

To find and preview these reusable components:

1. First Head to Core-UI / React Native Core-UI documentation in Github.

   The documentation in the [Core-UI](https://github.com/takeoff-com/core-ui) and [React Native Core-UI](https://github.com/takeoff-com/react-native-core-ui) is up to date with the latest information about the components.

1. Navigate to the docs page of the component you are planning to use

   For example, if we need to check the button component:

   - [Core-UI Button](https://github.com/takeoff-com/core-ui/blob/master/docs/components/Button.md)
   - [React Native Core-UI Button](https://github.com/takeoff-com/react-native-core-ui/blob/master/docs/components/button.md)

1. Check the Properties (Props) section

   In this document, the Props section will describe all the properties that you can use to style or modify the reusable components behavior.

   There is information here on how to use the component to render it in your React application.

1. Head to the Chromatic Storybook

   To preview how these props work and how the component look like, you need to head to the latest version of the Storybook.

   These are the permalinks to the latest version of Storybook so this view will be the one generated from the latest master version.

   - [Core-UI Storybook](https://master--61092acd880dce003b1a3b15.chromatic.com/)
   - [React Native Core-UI Storybook](https://master--61093bf948df55003971c946.chromatic.com/)

1. In Storybook, navigate to the Component you want to use.

   ![](/images/en/docs/Learning/ui-ux/storybook.png)

   In the component, there is be a `knobs` pane below the section.

   The knobs will allow you change the props to modify your component.

   Select the knobs until you match your expected design, and use these values in your code!

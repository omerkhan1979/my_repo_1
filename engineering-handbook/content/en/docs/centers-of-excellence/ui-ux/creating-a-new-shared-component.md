---
title: "Creating a new shared component"
linkTitle: "Creating a new shared component"
date: 2021-11-26
type: docs
tags: ["how-to"]
weight: 5
---

The purpose of this document is to provide some guidance on the list of areas required to develop a component in Core-UI or React Native Core-UI. This document will describe each of these areas in detail that can be used as an approach to develop a reusable component. 

## 1. Obtain the designs

The first step when developing a new reusable component is to obtain the designs from the design team. These designs are usually delivered as a page of the Design System Figma files these are (in order of priority):
[Takeoff Design System](https://www.figma.com/file/KBMNkPdPPPEx1HIUhvqTl4/Takeoff-Design-System-2021)
[Design System 2020](https://www.figma.com/file/eOMGGLj1TiOJT0S0BvQodd/Design-System-2020?node-id=0%3A1)

The designs should provide some information about, the expected appearance of the components, different variants of the component and a list of design tokens. Design Tokens are named properties that can be used by the developer to style their components.

The component name should be present in this design documentation, and should be respected, if there is a proposal for a different name, contact the design  tteam stefordiscussing the name.

It is also important to note that during implementation there can be cases where the designs cannot be met, or can be improved with some changes identified by the developer, if this is the case, please contact the design team to coordinate how to address these differences.

## 2. Identify the base components
When developing a new component it is important to identify if there are available components that can be reused to compose the new component. The sources to search for these components are:

  * **Core-UI and Core UI React Native Core UI Components**
      The Core UI and Core UI Native repos has a continuously growing set of components that can be used as part of any new components, typically, sub-components such as Typography, Button, etc. could provide some base components that can be reused using the Composition pattern.  

      To explore what components are available, go to:

      [Storybook (Chromatic) - Core-UI](https://master--61092acd880dce003b1a3b15.chromatic.com/) 
      [Storybook (Chromatic) - React Native Core-UI](https://master--61093bf948df55003971c946.chromatic.com/)


  * **Base UI Framework**

      Core-UI and React Native Core UI, use [Material UI](https://mui.com/) and [React Native Paper](https://callstack.github.io/react-native-paper/) as UI Frameworks, respectively. A new component should rely on the base implementation of these components, and extend or compose from them to form a new component that meets the design requirements.

      To see these components:

      Web (Material UI) [Usage - MUI](https://mui.com/getting-started/usage/) 
      -or-
      Mobile (React Native Paper), [Home · React Native Paper](https://callstack.github.io/react-native-paper/).


  * **3rd party library**

      Although not highly encouraged, it is also possible to fulfill the requirement by adding a third party library, if there is a good balance between the package reliability, dependencies, package size and effort to meet the requirement. 

      In such cases, please reach out to the UI/UX team before implementing to get some analysis on the proposed library.
      
## 3. Identify expected Props
It is also important during development process to identify what React props (short for properties) will be exposed of the component. These props will act as the signature for the component, and will allow defining how the component will look, render and behave.

Some typical Prop types are:
*```Events```: such as onClick or onChange, will give the parent component the control to describe what the component will do on each of these events. For example: [Core UI Button - onClick](https://github.com/takeoff-com/core-ui/blob/1d618d1511c45476a6ec5d40a755c08938cde484/src/Button/index.tsx#L14), the event when clicking a Core-UI button.
*```Label```: In cases where the component provides some labels in a specific place, a label string can be convenient, for example: [Core-UI Tab - Label](https://github.com/takeoff-com/core-ui/blob/1d618d1511c45476a6ec5d40a755c08938cde484/src/Tab/index.tsx#L48), the label for a specific Tab.
*```Flags```: Any flag that will change how the component renders, for example: [React Native Core-UI Dialog - Visible](https://github.com/takeoff-com/react-native-core-ui/blob/d4afee8cdc8bdde3d23b31e0c7b40b72fb885205/src/components/Dialog/index.jsx#L17)

*[Click here to learn more about React Props](https://reactjs.org/docs/components-and-props.html)

## 4. Identify Design Tokens
When styling a component, it is important to identify which design tokens will be used to style the different parts of a given component. 

The design token list is published to the storybook, under the Design Tokens story, for example:
[Design Tokens / All Design Tokens](https://61093bf948df55003971c946-ebtbvofajv.chromatic.com/?path=/story/design-tokens--all-design-tokens) (Pending to update after merging)

The tokens to use are generated at the Figma Design System documentation, and are imported to Core-UI and React Native Core UI (check [takeoff-com/design-tokens](https://github.com/takeoff-com/design-tokens) for more info). Also, look at the documentation in Core-ui or React Native Core UI for more info on how this will be used. 

There are a few things to note:

* **Token name differences from Figma**: 
  As we do some processing of the tokens exported from Figma, we might end up with slightly different names in the final repository. Please check the Storybook (in Chromatic or ran locally), to search for the token names, and be sure that you are referencing the right values. 

* **Debugging**: 
  There will be warnings showing in the Chrome console when you try to reference an non-existing design token. There might be good reasons on why a design token is not present, but is a good practice to check this for ensuring there are not hidden broken links.

* **Dimension / Space Tokens**: 
  to dimension a component, a developer need to make use of dimension properties such as padding, margin, height and width. When dealing with these there are two style token groups, to use:
   - **height**: When deciding the height of a component, look for tokens that start with, height:
   - **space**: Used in margins and padding. 
   - **If no match for any of these rules**, or there is no specific token described in the component designs, an explicit value is allowed.

* **Typography**: 
  Typographies are identified in the design system in Figma with a specific style name that encompasses all the properties.
  To use a specific typography, you need to ensure that all the typography properties for this specific typography style, these are: ```font-weight```, ```font-size```, ```font-family```, ```font-weight```, ```letter-spacing```, ```word-spacing```.
  To do this without adding all these properties one by one, you can use the ```Typography``` component or the ```fontDefinition``` function. for example:
  
  ```<Typography format="label-01">This code is in label-01</Typography>```
  
  or
  
  ```const styleProperties = fontDefinition("label-01");```
  
  Which will generate the necessary properties to build the whole font Definitions, please look for repository documentation for more details.
  
## 5. Document the Component

After completing the development work (component code, stories and tests), it is important to write documentation that allows other users to understand how to use the newly created component.

This documentation will live in the ```docs/component``` folder in the repository, in markdown format. 

This documentation should contain the following sections:

  * **Description**: A short description of the component.

  * **Props**: provide a list of the different props that are available to the component. In this section is important to list all the properties, and whether they can be optional or mandatory, and provide a description of the property. 

    If a prop is marked as optional, a default value must be implemented. for example: 
    [Visible field in React Native Core UI Dialog](https://github.com/takeoff-com/react-native-core-ui/blob/d4afee8cdc8bdde3d23b31e0c7b40b72fb885205/src/components/Dialog/index.jsx#L17)

    If a prop has a type that is a list of possible values, this needs to be documented in a separate document, called typed Values, for example, for ButtonSize, the list needs to be document at:
    [Core UI - TypeValues](https://github.com/takeoff-com/core-ui/blob/master/docs/components/typeValues.md#buttonsize)
    and cross referenced from the Button doc: [Core UI - Button](https://github.com/takeoff-com/core-ui/blob/master/docs/components/Button.md).

  * **Usage**: Example code on how to use the component. 

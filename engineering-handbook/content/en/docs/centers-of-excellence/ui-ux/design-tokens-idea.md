---
title: "Design Tokens Idea"
linkTitle: "Design Tokens Idea"
date: 2021-11-26
type: docs
tags: ["how-to"]
weight: 2
---

## Introduction

Design tokens can be described as a dictionary or hierarchical list of style properties and values that can be used to style a web or application component in a certain format.

Some examples of design tokens can be:

- Colors
- Typefaces.
- Typography, such as letter spacing, size, line height, etc.
- Borders
- Iconography

## Takeoff design tokens idea
The Takeoff design tokens solution and pipeline consist in defining the mechanisms to:

1. Allow designers to manage the tokens (properties, aliases, or assets)
2. Use CI/CD pipelines to convert and publish these tokens to artifacts that can be used in other applications for example css or json files.
3. Use these tokens in the applications to style components.

**Allow designers to manage the tokens (properties, aliases, or assets)**
Currently, the design system is defined in a Figma file workspace, this contains the base styles and this will act as the base for the design tokens. 

There are two **options** to build tokens from here:
1. Use the design tokens Figma plugin [lukasoppermann/design-tokens](https://github.com/lukasoppermann/design-tokens). This plugin allows exporting the values in a JSON schema that can be ingested and processed by style-dictionary (* tool to process design tokens).
2. Use [https://app.toolabs.com](https://app.toolabs.com) as a tool to manage the tokens. 

This tool will pull the tokens from Figma via a plugin and will allow visualizing these tokens into a format that is simple to manage. With this tool, we can export these tokens into a format that can be ingested by style-dictionary. For this option to work, the best format to generate this is the YAML format, as there are bugs with the JSON format.

*Both solutions are capable of managing and exporting the tokens, a decision on what is the best solution to meet this requirement needs to be made by the designer group.*

These values will be added to the Takeoff design-tokens repository inside the tokens/base.json (or Yaml) of the repository. Adding it here will allow exporting and making these tokens available for applications to use.

**Add other tokens or aliases.**

If there are other tokens required that don’t reside in the design system or are alias values of existing tokens, this can be added manually to a JSON or Yaml file of the repository.
*For example: In file tokens/colors.yaml:*
```
colors:
  my-new-component-background-color:
      value: "{colors.green-green-1}" 
 ```
 
 This will point to the ```{colors.green-green-1}``` that was generated from the design system.
 
 **Add icons or assets as tokens**
 
 Another feature of the design tokens solution is the ability to add icons and export them as tokens that can be imported by the client applications.
To do this, we need to add the file inside the assets folder of the repository:

Inside:
```<repo-root>/assets/alert-circle.svg```

And add a reference to the design file, for example: ```icon.yaml:```
```
asset:
  icon:
    alert-circle:
      value: assets/icons/alert-circle.svg
```
This will allow exporting the token as a base64 property that can be used in the client applications.

**Use CI/CD pipelines to convert and publish these tokens to artifacts that can be used in other applications for example CSS or JSON files.**

Using the **`style-dictionary`** package, the project in the design-tokens repository allows processing the design token files (YAML or JSON) and converting them to files that can be used in the client applications. 

We first need to configure a style dictionary to process the design token files and convert them to style files that can be used in applications:
```
const yaml = require('yaml');

module.exports = {
    parsers: [{
        pattern: /\.yaml$/,
        parse: ({ contents, filePath }) => yaml.parse(contents)
    }],
    source: [`tokens/**/*.yaml`],
    platforms: {
        css: {
            transformGroup: 'css',
            buildPath: 'build/',
            files: [{
                destination: 'variables.css',
                format: 'css/variables'
            }]
        },
        "scss": {
            "transformGroup": "scss",
            "buildPath": "build/",
            "files": [
                {
                    "destination": "scss/_variables.scss",
                    "format": "scss/variables"
                }
            ]
        },
        "json": {
            "transformGroup": "web",
            "buildPath": "build/json/",
            "files": [
                {
                    "destination": "variables.json",
                    "format": "json/flat"
                }
            ]
        },
        "assets/embed/json": {
            "transforms": [
                "attribute/cti",
                "name/cti/kebab",
                "asset/base64"
            ],
            "buildPath": "build/json/",
            "files": [
                {
                    "destination": "assets_icons.json",
                    "format": "json/flat",
                    "filter": {
                        "attributes": {
                            "category": "asset",
                            "type": "icon"
                        }
                    }
                },
                {
                    "destination": "assets_images.json",
                    "format": "json/flat",
                    "filter": {
                        "attributes": {
                            "category": "asset",
                            "type": "image"
                        }
                    }
                },
                {
                    "destination": "assets_fonts.json",
                    "format": "json/flat",
                    "filter": {
                        "attributes": {
                            "category": "asset",
                            "type": "font"
                        }
                    }
                }
            ]
        }
    }
}
```
This configuration, for instance, will take YAML files, and generate CSS, SCSS, and JSON files, and will include assets (icons, images, or typefaces).

To do this, we will run the command like:
```style-dictionary build```

And this will generate the files.

The aim will be to add this build process to the CI/CD so this can be versioned and validated when the design tokens are updated.
We will publish these tokens to two places:

1. As a NPM package that can be added as a dependency to the client software.
2. As a publicly available downloadable set of files in a GC bucket. This will allow us to import override our styles using dynamic loading of style files in web or mobile applications.

**Use these tokens in the applications to style components**

To style components in web we have various options:

1. SCSS:
Referencing the SCSS values for example 
```color: $green-color-1;```
This needs to ensure the SASS module is enabled in the project.

2. CSS:
Once the css is imported in the page, we could use the values using the CSS properties syntax:
Referencing the SCSS values for example 
```color: var(--green-color-1)```

3. JSS or style in JS.
This entails to import the JSON file and parse into a Javascript object, and use the values in the code.

4. For SVG icons
```
…   
   const dataUri = `url("data:image/svg+xml,${base64Token}")`;
      return (
        <div
          className='image'
          style={{
            background: dataUri,
            width: 500,
            height: 500,
          }}
        />
      );
  ```
  
  Or React Native:
  ```
  import { SvgXml } from 'react-native-svg';

        const DATA_IMAGE = atob('some base 64 string')

        

        <View>
           <SvgXml xml={DATA_IMAGE} width='50' height='50' /> 
        </View>
  ```

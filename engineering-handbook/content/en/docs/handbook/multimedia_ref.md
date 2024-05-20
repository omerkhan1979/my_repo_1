---
title: "Multimedia Reference"
linkTitle: "Multimedia Reference"
weight: 4
date: 2017-07-14
description: >
  Guidelines for adding images, video, presentations, diagrams, and more.
---
This page provides best practices for adding multimedia to this site. 

**Table of Contents**
  - [Add Images](#add-images)
  - [Embed Videos](#embed-videos-and-presentations)
  - [Embed Google Slides Presentations](#google-slides-presentation)
  - [Embed Microsoft Powerpoint Presentations](#microsoft-powerpoint)
  - [Embed spreadsheets](#embed-a-google-sheet-spreadsheet)
  - [Embed a PDF from Google Drive](#embed-a-pdf-hosted-on-google-drive)
  - [Plant UML Diagrams](#Diagrams)


## Add Images

1. Add your image to the sub-folder of the **/static** root directory that corresponds (mirrors) the **/content** sub-directory where your page is located.
  
    For example, if your markdown file is located here:
    ```
    content/en/docs/Handbook/example.md
    ```
    Then your image file must be located here (if you have to create a new directory, that's fine):
    ```
    static/images/en/docs/Handbook/exampleimage.png
    ```

2. Reference the image within your page using the following markdown:
    ```
    ![image alt text](/images/en/docs/Guilds/Architecture/takeoffsig.jpg) 
    ```
    {{< alert title="Note:" >}}Be aware that the directory path reference is **case sensitive**.{{< /alert >}}

<!-- 3. (*Optional*) Format your image using standard html tags. -->

### Example file 

The image below is located here:

    ```
    \static\images\en\docs\Architecture\takeoffsig.jpg
    ```
![Example Image](/images/en/docs/Guilds/Architecture/takeoffsig.jpg) 


The markdown used must have alt text (text used if the image cannot be displayed) within "[]" and the directory path (again, case-sensitive), in the "()" parens.
```
![Example Image](/images/en/docs/Guilds/Architecture/takeoffsig.jpg) 
```
### Image Formatting
It is possible to use [Shortcodes](https://www.docsy.dev/docs/adding-content/shortcodes/#imgproc) and inline html to format images as well. 


## Embed Videos and Presentations

We strongly recommend embedding assets such as presentations, external spreadsheets, PDFs, and videos rather than attaching or pasting into this handbook. 

This avoids creating duplicate copies, and ensures that the content displayed in the handbook always matches the source. 

The static site theme we use includes shortcodes that allow us to perform actions that are not otherwise possible solely through markdown. More info is available [here](https://www.docsy.dev/docs/adding-content/shortcodes/), but more relevant examples are as follows: 

The examples below are all iframes. Note that you can use other html5 parameters to modify the display of these iframes as well. 

### Google Slides Presentation

If you have view-only permissions, copy the url for the presentation and replace "/view" with "/embed", and make sure the height is 710. 
<!-- This instruction could be improved - there is a no border and auto-size parameter that can be used. -->


```html
---
<iframe src="<https://link to file>/embed" 
title="All Hands June 2021" width=100% height=710></iframe>"
---
```


### Microsoft Powerpoint

Go to **File** > **Share** > **Embed**, and share the embed code for 1186x691 dimensions.    

    
```html
---
<iframe src="<https://file url goes here>" width="1186px" height="691px"
 frameborder="0">This is an embedded <a target="_blank" 
 href="https://office.com">Microsoft Office</a> 
 presentation, powered by <a target="_blank" 
 href="https://office.com/webapps">Office</a>.</iframe>"
---
```

## Embed a Google Sheet (Spreadsheet)

Use an iframe to embed the sheet, but replace "/view" with "preview". It will look a little worse, but it will be functional.

```html
---
<iframe src="<file url goes here>/preview" 
width=100% height=1000></iframe>
---
```


## Embed a PDF Hosted on Google Drive

```html
---
<iframe src="<file url goes here>" width="1000px" height="600px"></iframe>"
---
```

## Diagrams

Many times an explanation can be aided by a diagram. Whenever presenting a diagram, we should still allow everyone to contribute. Where possible, take advantage of the handbook’s support for Plant UML diagrams. If you are new to using [Plant UML](https://plantuml.com/) and need help troubleshooting errors in your diagram code, the [PlantUML Live editor](https://www.planttext.com/) can be a helpful tool. Where taking advantage of these diagram tools isn’t possible, link to the original diagram or embed it in the page so that the diagram can be edited by anyone.

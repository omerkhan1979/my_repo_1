---
title: "Site Reference"
linkTitle: "Site Reference"
weight: 6
date: 2017-07-14
description: >
  What is a static site, hugo, Docsy theme, shortcodes, and more.
---

Static site intro
Hugo 
Docsy Theme
Shortcodes
Linking between articles


**Table of Contents**
  - [Handbook Overview](#Overview)
  - [Directories](#content)
  - [Images](#add-images)
  - [Videos](#videos)
  - [Reference](#reference)

## Handbook Overview

- [Why does this handbook exist and why do we use a static website instead of Confluence?](../handbook/handbook_first.md) 
- This handbook uses the static site generator [Hugo](https://gohugo.io/about/what-is-hugo/). We chose Hugo because it is created by Google and written in Go, so it was the natural choice for our all-in approach to GCP. 
- Hugo uses [Goldmark](https://github.com/yuin/goldmark/) as its Markdown parser by default.
- For code syntax highlighting, Hugo uses [Chroma](https://gohugo.io/content-management/syntax-highlighting/). 
- The theme template we use is called [Docsy](https://www.docsy.dev/about/). 
- What is [markdown](https://guides.github.com/features/mastering-markdown)? 
- [How do I contribute?](../handbook/contributing/)



## Content root directory

You add content for our site under the **content root directory** of our Hugo site project `content/en`. The main exception here is static files that you don't want built into our site, like images. You can find out more about where you add these below in [Adding images](#adding-static-content). The files in our content root directory are grouped in subdirectories corresponding to our site's sections and templates, which we'll look at in [Content sections and templates](#content-sections-and-templates).

You can find out more about Hugo directory structure in [Directory Structure Explained](https://gohugo.io/getting-started/directory-structure/#directory-structure-explained).

## Content sections and templates

Hugo builds our site pages using the content files you provide plus any templates provided by our site's theme. These templates (or *"layouts"* in Hugo terminology) include things like our page's headers, footers, navigation, and links to stylesheets: essentially, everything except our page's specific content. The templates in turn can be made up of *partials*: little reusable snippets of HTML for page elements like headers, search boxes, and more.

Because most technical documentation sites have different sections for different types of content, the Handbook theme comes with the [following templates](https://github.com/google/docsy/tree/master/layouts) for top-level site sections that you might need:

* [`docs`](https://github.com/google/docsy/tree/master/layouts/docs) is for pages in our site's Documentation section.
* [`blog`](https://github.com/google/docsy/tree/master/layouts/blog) is for pages in our site's Blog.
* [`community`](https://github.com/google/docsy/tree/master/layouts/community) is for our site's Community page.

It also provides a [default "landing page" type of template](https://github.com/google/docsy/tree/master/layouts/_default) with the site header and footer, but no left nav, that you can use for any other section. In this site and our example site it's used for the site [home page](/) and the [About](/about/) page.

Each top-level **section** in our site corresponds to a **directory** in our site content root. Hugo automatically applies the appropriate **template** for that section, depending on which folder the content is in. For example, this page is in the `docs` subdirectory of the site's content root directory `content/en/`, so Hugo automatically applies the `docs` template. You can override this by explicitly specifying a template or content type for a particular page.

If you've copied the example site, you already have appropriately named top-level section directories for using Docsy's templates, each with an index page ( `_index.md` or `index.html`) page for users to land on. These top-level sections also appear in the example site's [top-level menu](/docs/adding-content/navigation/#top-level-menu). 

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
### Custom sections

If you've copied the example site and *don't* want to use one of the provided content sections, just delete the appropriate content subdirectory. Similarly, if you want to add a top-level section, just add a new subdirectory, though you'll need to specify the layout or content type explicitly in the [frontmatter](#page-frontmatter) of each page if you want to use any existing Docsy template other than the default one. For example, if you create a new directory `content/en/amazing` and want one or more pages in that custom section to use Docsy's `docs` template, you add `type: docs` to the frontmatter of each page:

```yaml
---
title: "My amazing new section"
weight: 1
type: docs
description: >
  A special section with a docs layout.
---
```

Alternatively, create our own page template for our new section in our project's `layouts` directory based on one of the existing templates.

You can find out much more about how Hugo page layouts work in [Hugo Templates](https://gohugo.io/templates/). The rest of this page tells you about how to add content and use each of Docsy's templates.

### Alternative site structure

As noted above, by default our site has a home page (using the `_default` layout), a docs section under `/docs/`, a blog section under `/blog/` and a community section under `/community/`.   [The type](https://gohugo.io/content-management/types/) of each section (which determines the layout it uses) matches its directory name.

In some cases, you may want to have a different directory structure, but still make use of Docsy's layouts. A common example is for a "docs site", where most of the pages (including the home page) use the docs layout, or perhaps you'd rather have a `/news/` directory treated with the blog layout.

Since Hugo 0.76, this has become practical without copying layouts to our site, or having to specify `type: blog` on every single page by making use of [target specific cascading front matter](https://gohugo.io/content-management/front-matter/#target-specific-pages).

For example, for the `/news/` section, you can specify the following front matter in the index page which will change the type of the section and everything below it to "blog":

```yaml
---
title: "Latest News"
linkTitle: "News"
menu:
  main:
    weight: 30

cascade:
- type: "blog"
---
```

If you want to create a "docs" site, specifying something like the following in the top level `_index.md` will set all top level sections to be treated as "docs", except for "news":

```yaml
---
title: "My Wonderful Site"

cascade:
- type: "blog"
  toc_root: true
  _target:
    path: "/news/**"
- type: "docs"
  _target:
    path: "/**"
---
```

Note the addition of `toc_root` here.  Setting that to true for a section causes it to be treated as a separate part of the site, with its own left hand navigation menu.

An example docs-based site that uses this technique can be found at the [mostly docs](https://github.com/gwatts/mostlydocs/) repo.

## Page frontmatter

See [How to Contribute](../docs/handbook/tech_ref.md)

<!-- ## Page contents and markup

By default you create pages in a Docsy site as simple [Markdown or HTML files](https://gohugo.io/content-management/formats/) with [page frontmatter](#page-frontmatter), as described above. Versions of Hugo before 0.60 use [BlackFriday](https://github.com/russross/blackfriday) as its Markdown parser. From 0.60, Hugo uses [Goldmark](https://github.com/yuin/goldmark/) as its Markdown parser by default.

{{% alert title="Tip" %}}
If you've been using earlier versions of Hugo, you may need to make some small changes to our site to work with the current Markdown parser. In particular, if you cloned an earlier version of our example site, add the following to our `config.toml` to allow Goldmark to render raw HTML as well as Markdown:

```
[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true
```

Alternatively, if you want to continue using Blackfriday, you can follow the instructions in the [Hugo documentation](https://gohugo.io/getting-started/configuration-markup#blackfriday) to change the Markdown parser.
{{% /alert %}}

In addition to our marked-up text, you can also use Hugo and Docsy's [shortcodes](/docs/adding-content/shortcodes): reusable chunks of HTML that you can use to quickly build our pages. Find out more about shortcodes in [Docsy Shortcodes](/docs/adding-content/shortcodes).

{{% alert title="Note" color="info" %}}
Hugo also supports adding content using other markups using [external parsers as helpers](https://gohugo.io/content-management/formats/#additional-formats-through-external-helpers). For example, you can add content in RST using `rst2html` as an external parser (though be aware this does not support all flavors of RST, such as Sphinx RST). Similarly, you can use `asciidoctor` to parse Asciidoc files, or `pandoc` for other formats.

External parsers may not be suitable for use with all deployment options, as you'll need to install the external parser and run Hugo ourself to generate our site (so, for example, you won't be able to use [Netlify's continuous deployment feature](/docs/deployment/#deployment-with-netlify)). In addition, adding an external parser may cause performance issues building larger sites.
{{% /alert %}} -->

### Working with links

Hugo lets you specify links using normal Markdown syntax, though remember that you need to specify links relative to our site's root URL, and that relative URLs are left unchanged by Hugo in our site's generated HTML.

Alternatively you can use Hugo's helper [`ref` and `relref` shortcodes](https://gohugo.io/content-management/cross-references/) for creating internal links that resolve to the correct URL. However, be aware this means our links will not appear as links at all if a user views our page outside our generated site, for example using the rendered Markdown feature in GitHub's web UI.

You can find (or add!) tips and gotchas for working with Hugo links in [Hugo Tips](/docs/best-practices/site-guidance).

### Content style

We don't mandate any particular style for our page contents. However, if you'd like some guidance on how to write and format clear, concise technical documentation, we recommend the [Google Developer Documentation Style Guide](https://developers.google.com/style/), particularly the [Style Guide Highlights](https://developers.google.com/style/highlights).

## Page bundles

You can create site pages as standalone files in their section or subsection directory, or as folders where the content is in the folder's index page. Creating a folder for our page lets you [bundle](https://gohugo.io/content-management/page-bundles/) images and other resources together with the content. 

You can see examples of both approaches in this and our example site. For example, the source for this page is just a standalone file `/content/en/docs/adding-content.md`. However the source for [Docsy Shortcodes](/docs/adding-content/shortcodes/) in this site lives in `/content/en/docs/adding-content/shortcodes/index.md`, with the image resource used by the page in the same `/shortcodes/` directory. In Hugo terminology, this is called a *leaf bundle* because it's a folder containing all the data for a single site page without any child pages (and uses `index.md` without an underscore).

You can find out much more about managing resources with Hugo bundles in [Page Bundles](https://gohugo.io/content-management/page-bundles/).

## Adding docs and blog posts

The template you'll probably use most often is the [`docs` template](https://github.com/google/docsy/blob/master/layouts/docs/baseof.html) (as used in this page) or the very similar [`blog` template](https://github.com/google/docsy/blob/master/layouts/blog/baseof.html). Both these templates include:

* a left nav
* GitHub links (populated from our site config) for readers to edit the page or create issues
* a page menu

as well as the common header and footer used by all our site's pages. Which template is applied depends on whether you've added the content to the `blog` or `docs` content directory. You can find out more about how the nav and page menu are created in [Navigation and Search](/docs/adding-content/navigation/). 

### Organizing our documentation

While Docsy's top-level sections let you create site sections for different types of content, you may also want to organize our docs content within our `docs` section. For example, this site's `docs` section directory has multiple subdirectories for **Getting Started**, **Content and Customization**, and so on. Each subdirectory has an `_index.md` (it could also be an `_index.html`), which acts as a section index page and tells Hugo that the relevant directory is a subsection of our docs.

Docsy's `docs` layout gives you a left nav pane with an autogenerated nested menu based on our `docs` file structure. Each standalone page or subsection `_index.md` or `_index.html`  page in the `docs/` directory gets a top level menu item, using the link name and `weight` metadata from the page or index. 

To add docs to a subsection, just add our page files to the relevant subdirectory. Any pages that you add to a subsection in addition to the subsection index page will appear in a submenu (look to the left to see one in action!), again ordered by page `weight`. Find out more about adding Docsy's navigation metadata in [Navigation and Search](/docs/adding-content/navigation/)

If you've copied the example site, you'll already have some suggested subdirectories in our `docs` directory, with guidance for what types of content to put in them and some example Markdown pages. You can find out more about organizing our content with Docsy in [Organizing our Content](/docs/best-practices/organizing-content/).


## Working with top-level landing pages.

Docsy's [default page template](https://github.com/google/docsy/blob/master/layouts/docs/baseof.html) has no left nav and is useful for creating a home page for our site or other "landing" type pages.

### Customizing the example site pages

If you've copied the example site, you already have a simple site landing page in `content/en/_index.html`. This is made up of Docsy's provided Hugo shortcode [page blocks](/docs/adding-content/shortcodes/#shortcode-blocks).

To customize the large landing image, which is in a [cover](/docs/adding-content/shortcodes/#blockscover) block, replace the `content/en/featured-background.jpg` file in our project with our own image (it can be called whatever you like as long as it has `background` in the file name). You can remove or add as many blocks as you like, as well as adding our own custom content. 

The example site also has an About page in `content/en/about/_index.html` using the same Docsy template. Again, this is made up of [page blocks](/docs/adding-content/shortcodes/#shortcode-blocks), including another background image in `content/en/about/featured-background.jpg`. As with the site landing page, you can replace the image, remove or add blocks, or just add our own content.

### Building our own landing pages

If you've just used the theme, you can still use all Docsy's provided [page blocks](/docs/adding-content/shortcodes/#shortcode-blocks) (or any other content you want) to build our own landing pages in the same file locations.


## RSS feeds

Hugo will, by default, create an RSS feed for the home page and any section. For the main RSS feed you can control which sections to include by setting a site param in our `config.toml`. This is the default configuration:

```toml
rss_sections = ["blog"]
```
To disable all RSS feeds, add the following to our `config.toml`:

```toml
disableKinds = ["RSS"]
```

## Sitemap

Hugo creates a `sitemap.xml` file for our generated site by default: for example, [here's the sitemap](/sitemap.xml) for this site.

You can configure the frequency with which our sitemap is updated, our sitemap filename, and the default page priority in our `config.toml`:

```toml
[sitemap]
  changefreq = "monthly"
  filename = "sitemap.xml"
  priority = 0.5
```

To override any of these values for a given page, specify it in page frontmatter:

```yaml
---
title: "Adding Content"
linkTitle: "Adding Content"
weight: 1
description: >
  Add different types of content to our Docsy site.
sitemap:
  priority: 1.0
---
```

To learn more about configuring sitemaps, see [Sitemap Template](https://gohugo.io/templates/sitemap-template/).

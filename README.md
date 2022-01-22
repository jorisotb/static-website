# JorisotB's Static site generator
This project contains both my personal website and the python script used to compile it.

The website is entirely static, no PHP, no JavaScript.

## Includes
As a substitute for the include functionality, I wrote include_htm.py.
The script crawls the website's source code directory (default: /src/) looking for the the following statement:
```
@include|some-file
```
In the output directory (default: /out/), this statement is replaced with the contents of the corresponding file. This file should be located in the includes directory (default: /includes/).

## Blog Post Templates
The tool also generates the blog posts themselves. It scans a provided template file (default: /template.html) for the following statements:
```
@date
@title
@content
```
These statements are then replaced with the date, title and body of each post. Posts are stored in .htm files in the blog directory (default: /blog/). They must have the following format:
```
dd/mm/yyyy
title
content
```
The resulting .html files replace these files in the output directory.

## Linking
The generated blog posts are automatically linked usign the following statements:
```
@bloglist
@latest
```
The 'bloglist' statement is replaced with a list of links to all blogposts, ordered new to old.
The 'latest' statement is replaces with a link to the latest blogpost.

Todo:
  * [x] add generation of blog posts
  * [x] add automatic linking to blog posts
  * [x] add cmd flags
  * [x] support for different directory structures
  * [ ] support for different file types

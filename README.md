# JorisotB's Static site generator
This project contains both my personal website ([jorisotb.net](https://jorisotb.net)) and the python script used to compile it.

The website is entirely static, no PHP, no JavaScript.

## Includes
As a substitute for PHP's include functionality, `include_htm.py` crawls the website's source code directory (default: `/src/`) looking for the the following statement:
```
@include|some-file
```
In the output directory (default: `/out/`), this statement is replaced with the contents of the corresponding file. This file should be located in the includes directory (default: `includes/`).

## Blog Post Templates
The script can also generate blog posts. It scans a provided template file (default: `template.html`) for the following statements:
```
@posted
@edited
@title
@content
```
These statements are then replaced with the dates, title and body of each post.

Posts are stored in `.htm` files in the blog directory (default: `blog/`). They must have the following format, where dates are written as `dd-mm-yyyy`:
```
posted date
edited date
title
content
```
The resulting `.html` files replace these files in the output directory.

If your site has no blog, this functionality can be turned off by adding `--disable-blog` to the execution of the script.

## Linking
The generated blog posts are automatically linked using the following statements:
```
@bloglist
@latest
```
`@bloglist` is replaced with a list of links to all blogposts, ordered new to old. By default, posts are ordered by the date on which they were posted, but you can add `-l edited` to the execution to order them by the dates on which they were edited.

`@latest` is replaced with a link to the latest blogpost. This is the most recent post according to the same sorting order as the bloglist.

The `--disable-blog` option also disables linking.

## Newsfeed
When running the script, a `feed.atom` file is generated in the output directory. The contents of this file can be adjusted by changing the `atom_header`, `atom_entry`, and `atom_footer` strings at the top of `include_htm.py`, and the `do_atomfeed` function. Only the generation of the Atom file is handled by the script, you will need to add a link to it manually.

This functionality can be disabled by adding `--disable-feed` to the execution.

### Todo:
  * [x] add generation of blog posts
  * [x] add automatic linking to blog posts
  * [x] add cmd flags
  * [x] add support for different directory structures
  * [x] add blog post sorting options (posted date/edited date)
  * [x] rss/atom feed support
  * [ ] support for different file types

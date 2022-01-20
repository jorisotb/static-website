# static-website
This is my personal static website project.

It is entirely static, no PHP, no JavaScript. As a substitute for the include functionality, I wrote include_htm.py. 
The script crawls the website's source code looking for the following syntax:
```
@include|<some-file>
```
When this snippet is encountered, it looks in the /includes directory for the corresponding htm file and replaces it with the contents of that file.

Todo:
  - support for different directory structures
  - support for different file types

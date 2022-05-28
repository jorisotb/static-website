import os
import argparse

from re import sub
from shutil import copyfile
from datetime import datetime
from time import time

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Enable verbose printing')
parser.add_argument('-c', '--clean', default=False, action='store_true', help='!WARNING! be very careful with this option, it WILL delete all contents of the output directory. Clean output directory before copying files')
parser.add_argument('-s', '--source', type=str, default='src/', help='Specify source directory (default: src/)')
parser.add_argument('-o', '--output', type=str, default='out/', help='Specify output directory (default: out/')
parser.add_argument('-i', '--include', type=str, default='includes/', help='Specify includes directory (default: includes/)')
parser.add_argument('-b', '--blog', type=str, default='blog/', help='Specify blog directory (default: blog/)')
parser.add_argument('-t', '--template', type=str, default='template.html', help='Specify template file (default: template.html)')
parser.add_argument('-l', '--list-order', type=str, default='posted', help='Specify ordering of the bloglist (posted or edited) (default: posted)')

parser.add_argument('--disable-blog', default=False, action='store_true', help='Disable blogging functionality. Use this if you have no blog directory, or the directory is empty')
parser.add_argument('--disable-feed', default=False, action='store_true', help='Disable Atom newsfeed functionality')
args = parser.parse_args()

atom_header = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>JorisotB.net Blog</title>
    <subtitle>The latest blog posts from JorisotB.net</subtitle>
    <link href="https://jorisotb.net/feed.atom" rel="self" />
    <link href="https://jorisotb.net/" />
    <id>https://jorisotb.net/</id>
    <author>
        <name>JorisotB</name>
    </author>
    <updated>{0}</updated>
'''
atom_entry = '''    <entry>
        <title>{0}</title>
        <link href="https://jorisotb.net/{1}" />
        <id>https://jorisotb.net/{1}</id>
        <author>
            <name>JorisotB</name>
        </author>
        <summary>A blogpost titled &#39;{0}&#39; from JorisotB.net</summary>
        <published>{2}</published>
        <updated>{3}</updated>
    </entry>
'''
atom_footer = '''</feed>
'''

blogposts = []

class blogpost:
    def __init__(self, posted, edited, title, content):
        self.posted = posted
        self.edited = edited
        self.title = title
        self.content = content

def debug_print(s):
    if args.verbose:
        print(s)

def filepath(path, filename, target, source):
    '''Generate nice filepaths because os.crawl() is strange.'''
    if not path.endswith('/'):
        path += '/'
    return target+path.split(source, maxsplit=1)[1]+filename

def blogpost_filepath(post):
    '''Generate post filepaths from title and date. All non-alphanumerical
    characters are stripped. Titles are cut of after 32 characters.'''
    clean_title = sub(r'\W+', '-', post.title[:32])
    return args.blog+post.posted+'-'+clean_title+'.html'

def atom_title(title):
    '''Replace characters that would cause errors in xml with their
    escape sequences.'''
    for pattern, repl in [['&',  '&#38;'],
                          ['<',  '&#60;'], ['>',  '&#62;'],
                          ['\'', '&#39;'], ['\"', '&#34;']]:
        title = sub(pattern, repl, title)
    return title

def date_format(date):
    '''Convert post date strings formatted as dd-mm-yyyy to datetime objects.'''
    return datetime.strptime(date, '%d-%m-%Y')

def atom_date_format(date):
    '''Convert datetime objects to strings that follow the date format
    used by Atom.'''
    return date.strftime('%Y-%m-%dT%XZ')

def do_copy():
    '''Copy the source directory to the working directory.'''
    print('Copying files to output directory...')

    for path, dirs, files in os.walk(args.source):
        for file in files:
            if not file.endswith('.hidden'):
                debug_print('    '+filepath(path,file,args.output,args.source)+'...')

                if not os.path.exists(filepath(path, '', args.output, args.source)):
                    os.makedirs(filepath(path, '', args.output, args.source))

                copyfile(filepath(path, file, args.source, args.source),
                         filepath(path, file, args.output, args.source))

def do_blogposts():
    '''Generate blog post HTML files from the htm files in the blog
    directory using the template file.'''
    print('Processing blog posts...')

    blog_dir = args.output+args.blog
    for file in os.listdir(blog_dir):
        if file.endswith('.htm'):
            debug_print('    '+filepath(args.output,file,args.output,args.output)+'...')
            post_file = open(blog_dir+file, 'r', encoding='utf8')
            blogposts.append(blogpost(post_file.readline().strip(),
                                      post_file.readline().strip(),
                                      post_file.readline().strip(),
                                      ''.join(post_file.read().strip())))
            post_file.close()

    if (args.list_order == 'edited'):
        blogposts.sort(key = lambda post: date_format(post.edited), reverse=True)
    elif (args.list_order == 'posted'):
        blogposts.sort(key = lambda post: date_format(post.posted), reverse=True)

    for post in blogposts:
        src_file = open(args.output+args.template, 'r', encoding='utf8')
        out_file = open(args.output+blogpost_filepath(post), 'a', newline='\r\n', encoding='utf8')
        out_file.truncate(0)

        for line in src_file:
            if '@posted' in line:
                out_file.write(post.posted)
            elif '@edited' in line:
                out_file.write(post.edited)
            elif '@title' in line:
                out_file.write(post.title)
            elif '@content' in line:
                out_file.write(post.content)
            else:
                out_file.write(line)

        src_file.close()
        out_file.close()

def do_atomfeed():
    '''Generate a feed.atom file from the strings specified at the top of this file.'''
    out_file = open(args.output+'feed.atom', 'a', newline='\r\n', encoding='utf8')
    out_file.truncate(0)

    out_file.write(atom_header.format(atom_date_format(datetime.now())))
    for post in blogposts:
        out_file.write(atom_entry.format(atom_title(post.title),
                                         blogpost_filepath(post),
                                         atom_date_format(date_format(post.posted)),
                                         atom_date_format(date_format(post.edited))))
    out_file.write(atom_footer)

    out_file.close()

def do_includes(link_mode=False):
    '''Replace @include|<some file> statements with the contents of
    corresponding file.
    If link_mode is true, instead replace @bloglist and @latest statements
    with the relevant links.'''
    if link_mode:
        print('Processing links...')
    else:
        print('Processing includes...')

    for path, dirs, files in os.walk(args.output):
        for file in files:
            if file.endswith('.html'):
                debug_print('    '+filepath(path,file,args.output,args.output)+'...')

                src_file = open(filepath(path, file, args.output, args.output), 'r', encoding='utf8')
                out_file = open(filepath(path, file+'.tmp', args.output, args.output), 'a', newline='\r\n', encoding='utf8')
                out_file.truncate(0)

                for line in src_file:
                    if not link_mode and '@include' in line:
                        inc_file = open(args.source+args.include+line.strip().split('|')[1], 'r')
                        for t_line in inc_file:
                            out_file.write(t_line)
                        inc_file.close()
                    elif link_mode and '@bloglist' in line:
                        for post in blogposts:
                            if (args.list_order == 'edited'):
                                out_file.write('<dd><a href="/'+blogpost_filepath(post)+'">'+post.edited+' - '+post.title+'</a></dd>')
                            elif (args.list_order == 'posted'):
                                if date_format(post.edited) > date_format(post.posted):
                                    out_file.write('<dd><a href="/'+blogpost_filepath(post)+'">'+post.posted+' - '+post.title+'</a><sup>*</sup></dd>')
                                else:
                                    out_file.write('<dd><a href="/'+blogpost_filepath(post)+'">'+post.posted+' - '+post.title+'</a></dd>')
                    elif link_mode and '@latest' in line:
                        post = blogposts[0]
                        if (args.list_order == 'edited'):
                            out_file.write('<a href="/'+blogpost_filepath(post)+'">'+post.edited+' - '+post.title+'</a>')
                        elif (args.list_order == 'posted'):
                            out_file.write('<a href="/'+blogpost_filepath(post)+'">'+post.posted+' - '+post.title+'</a>')
                    else:
                        out_file.write(line)

                src_file.close()
                out_file.close()
                os.remove(filepath(path, file, args.output, args.output))
                os.rename(filepath(path, file+'.tmp', args.output, args.output),
                          filepath(path, file, args.output, args.output))

def do_cleanup(full_clean_mode=False):
    '''Clean htm files and empty directories from the working directory.'''
    if full_clean_mode:
        print('Emptying output directory...')
    else:
        print('Removing unnecessary files...')
    for path, dirs, files in os.walk(args.output):
        for file in files:
            if full_clean_mode or file.endswith('.htm'):
                debug_print('    '+filepath(path,file,args.output,args.output)+'...')
                os.remove(filepath(path, file, args.output, args.output))

    if not full_clean_mode:
        print('Removing empty directories...')
    for path, dirs, files in os.walk(args.output):
        if not dirs and not files:
            debug_print('    '+path+'...')
            os.rmdir(path)

if __name__ == "__main__":
    start_time = time()
    print('running include_htm with\n  source = ' + args.source + '\n  output = ' + args.output)

    if args.clean:
        do_cleanup(full_clean_mode=True)

    do_copy()
    do_includes()
    if not args.disable_blog:
        do_blogposts()
        do_includes(link_mode=True)
    if not args.disable_feed:
        do_atomfeed()
    do_cleanup()

    delta_time = time() - start_time
    debug_print('Finished in '+str(round(delta_time, 3))+'s')

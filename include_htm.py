import os
import argparse

from shutil import copyfile
from datetime import datetime
from time import time

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', type=str, default='src/', help='Source directory')
parser.add_argument('-o', '--output', type=str, default='out/', help='Output directory')
parser.add_argument('-b', '--blog', type=str, default='blog/', help='Blog directory')
parser.add_argument('-i', '--include', type=str, default='includes/', help='Includes directory')
parser.add_argument('-t', '--template', type=str, default='template.html', help='Template file')
parser.add_argument('-c', '--clean', type=bool, default=False, help='Clean output directory before starting')
args = parser.parse_args()

blog_posts = []

def filepath(path, filename, target, source):
    '''Generate nice filepaths because os.crawl() is strange.'''
    if not path.endswith('/'):
        path += '/'

    return target+path.split(source, maxsplit=1)[1]+filename

def do_copy():
    '''Copy the source directory to the working directory.'''
    print('Copying files to destination folder...')
    for path, dirs, files in os.walk(args.source):
        for file in files:
            print('    '+filepath(path,file,args.output,args.source)+'...')

            if not os.path.exists(filepath(path, '', args.output, args.source)):
                os.makedirs(filepath(path, '', args.output, args.source))

            copyfile(filepath(path, file, args.source, args.source),
                     filepath(path, file, args.output, args.source))

def do_blog_posts():
    '''Generate blog post HTML files from the htm files in the blog
    directory using the template file.'''
    print('Processing blog posts...')

    for path, dirs, files in os.walk(args.output+args.blog):
        for file in files:
            if file.endswith('.htm'):
                print('    '+filepath(path,file,args.output,args.output)+'...')
                post = open(path+file, 'r')

                blog_posts.append([])
                for line in post:
                    blog_posts[-1].append(line.strip())
                post.close()

        blog_posts.sort(key = lambda post: datetime.strptime(post[0], '%d/%m/%Y'), reverse=True)

        for post in blog_posts:
            date = post[0]
            title = post[1]
            content = ' '.join(i for i in post[2:])

            src_file = open(args.output+args.template, 'r')
            out_file = open(args.output+args.blog+title+'.html', 'a')
            out_file.truncate(0)

            for line in src_file:
                if '@title' in line:
                    out_file.write(title)
                elif '@date' in line:
                    out_file.write(date)
                elif '@content' in line:
                    out_file.write(content)
                else:
                    out_file.write(line)

            src_file.close()
            out_file.close()

def do_includes(link_mode = False):
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
                print('    '+filepath(path,file,args.output,args.output)+'...')

                src_file = open(filepath(path, file, args.output, args.output), 'r')
                out_file = open(filepath(path, file+'.tmp', args.output, args.output), 'a')
                out_file.truncate(0)

                for line in src_file:
                    if not link_mode and '@include' in line:
                        inc_file = open(args.source+args.include+line.strip().split('|')[1])
                        for t_line in inc_file:
                            out_file.write(t_line)
                        inc_file.close()
                    elif link_mode and '@bloglist' in line:
                        for post in blog_posts:
                            out_file.write('<dd><a href="/blog/'+post[1]+'.html">'+post[0]+' - '+post[1]+'</a></dd>')
                    elif link_mode and '@latest' in line:
                        post = blog_posts[0]
                        out_file.write('<a href="/blog/'+post[1]+'.html">'+post[0]+' - '+post[1]+'</a>')
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
        print('Emptying working directory...')
    else:
        print('Removing unnecessary files...')
    for path, dirs, files in os.walk(args.output):
        for file in files:
            if full_clean_mode or file.endswith('.htm'):
                print('    '+filepath(path,file,args.output,args.output)+'...')
                os.remove(filepath(path, file, args.output, args.output))

    if not full_clean_mode:
        print('Removing empty directories...')
    for path, dirs, files in os.walk(args.output):
        if not dirs and not files:
            print('    '+path+'...')
            os.rmdir(path)

if __name__ == "__main__":
    start_time = time()
    print('running include_htm with\n      source = ' + args.source + '\n destination = ' + args.output)

    if (args.clean):
        do_cleanup(full_clean_mode=True)

    do_copy()
    do_blog_posts()
    do_includes()
    do_includes(link_mode=True)
    do_cleanup()

    delta_time = time() - start_time
    print('finished in '+str(delta_time)+'s')

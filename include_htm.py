import os

from shutil import copyfile
from time import time
from datetime import datetime
from tkinter.tix import Tree

# Options (will probably add cmd args for these)
src_dir   = 'src/'
out_dir   = 'out/'
temp_file = 'template.html'
blog_dir  = 'blog/'
inc_dir   = 'includes/'

blog_posts = []

def filepath(path, filename, target, source):
    '''Generate nice filepaths because os.crawl() is strange.'''
    if not path.endswith('/'):
        path += '/'

    return target+path.split(source)[1]+filename

def do_copy():
    '''Copy the source directory to the working directory.'''
    print('Copying files to destination folder...')
    for path, dirs, files in os.walk(src_dir):
        for file in files:
            print('    '+filepath(path,file,out_dir,src_dir)+'...')

            if not os.path.exists(filepath(path, '', out_dir, src_dir)):
                os.makedirs(filepath(path, '', out_dir, src_dir))

            copyfile(filepath(path, file, src_dir, src_dir),
                     filepath(path, file, out_dir, src_dir))

def do_blog_posts():
    '''Generate blogpost HTML files from the htm file in the blog
    directory using the template file.'''
    print('Processing blog posts...')

    for path, dirs, files in os.walk(out_dir+blog_dir):
        for file in files:
            if file.endswith('.htm'):
                print('    '+filepath(path,file,out_dir,out_dir)+'...')
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

            src_file = open(out_dir+temp_file, 'r')
            out_file = open(out_dir+blog_dir+title+'.html', 'a')
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

    for path, dirs, files in os.walk(out_dir):
        for file in files:
            if file.endswith('.html'):
                print('    '+filepath(path,file,out_dir,out_dir)+'...')

                src_file = open(filepath(path, file, out_dir, out_dir), 'r')
                out_file = open(filepath(path, file+'.tmp', out_dir, out_dir), 'a')
                out_file.truncate(0)

                for line in src_file:
                    if not link_mode and '@include' in line:
                        inc_file = open(src_dir+inc_dir+line.strip().split('|')[1])
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
                os.remove(filepath(path, file, out_dir, out_dir))
                os.rename(filepath(path, file+'.tmp', out_dir, out_dir),
                          filepath(path, file, out_dir, out_dir))

def do_clean():
    '''Clean htm files and empty directories from the working directory.'''
    print('Removing unnecessary files...')
    for path, dirs, files in os.walk(out_dir):
        for file in files:
            if file.endswith('.htm'):
                print('    '+filepath(path,file,out_dir,out_dir)+'...')
                os.remove(filepath(path, file, out_dir, out_dir))

    print('Removing empty directories...')
    for path, dirs, files in os.walk(out_dir):
        if not dirs and not files:
            print('    '+path+'...')
            os.rmdir(path)

if __name__ == "__main__":
    start_time = time()
    print('running include_htm with\n      source = ' + src_dir + '\n destination = ' + out_dir)

    do_copy()
    do_blog_posts()
    do_includes()
    do_includes(link_mode=True)
    do_clean()

    delta_time = time() - start_time
    print('finished in '+str(delta_time)+'s')

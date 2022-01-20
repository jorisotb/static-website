import sys
import os

from shutil import copyfile
from time import time

if len(sys.argv) > 1:
    src_dir = sys.argv[1]+'/'
    out_dir = sys.argv[2]+'/'
else:
    src_dir = 'src/'
    out_dir = 'out/'

def filepath(path, filename, target):
    if target == 'out':
        return out_dir+path.split(src_dir)[1]+'/'+filename

    elif target == 'src':
        return src_dir+path.split(src_dir)[1]+'/'+filename

if __name__ == "__main__":
    start_time = time()
    print('running include_htm with\n      source = ' + src_dir + '\n destination = ' + out_dir)

    for path, dirs, files in os.walk(src_dir):
        for file in files:
            if 'includes' not in path:
                print('scanning file '+path+'/'+file+'...')

                if not os.path.exists(filepath(path, '', 'out')):
                    os.makedirs(filepath(path, '', 'out'))

                if 'html' in file:
                    src_file = open(filepath(path, file, 'src'), 'r')

                    out_file = open(filepath(path, file, 'out'), 'a')
                    out_file.truncate(0)

                    for line in src_file:
                        if '@include' in line:
                            inc_file = open(src_dir+'includes/'+line.strip().split('|')[1])
                            for t_line in inc_file:
                                out_file.write(t_line)
                        else:
                            out_file.write(line)
                else:
                    copyfile(filepath(path, file, 'src'), filepath(path, file, 'out'))

    delta_time = time() - start_time
    print('finished in '+str(delta_time)+'s')

import os
import sys
from tqdm import tqdm

class bcolors:
    HEADER = '\033[96m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def usage():
    usage_str = '''
        [Usage]: python3 keyreplace find key path keyfile
                 python3 keyreplace replace key path keyfile
                1.find all keys and record them in keyfile
                2.comment keys in keyfile that do not want to be replaced
                3.replace keys accroding to keyfile
    '''

    keyfile_str = '''
        [keyfile format]: take 'tutu' as key for example
                ;line start with ';' is a commment line

                ;line start with 'dir:' is a dir that has key in its name
                dir: path/tutu/

                ;line start with 'file:' is a file that has key in its name
                file: path/tutu/tutu.txt

                ;line start with 'text:' is a key in file's content,follow by a newline that show 
                ;the content of that line
                text: path/tutu/tutu.txt 10(linenum) 33(posinline) 
                'this is the line that contained tutu'
    '''
    print(bcolors.OKGREEN + usage_str +bcolors.ENDC)
    print(bcolors.OKGREEN + keyfile_str +bcolors.ENDC)



def countDir(path):
    dirs_all = []
    files_all = []
    for root, dirs, files in os.walk(path):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for d in dirs:
            if os.path.islink(os.path.join(root,d)) == False:
                dirs_all.append(os.path.join(root,d))
        for f in files:
            if os.path.islink(os.path.join(root,f)) == False:
                files_all.append(os.path.join(root,f))
    return dirs_all, files_all

def fgrep(key, path):
    #-bno
    res = os.popen('rg -bn '+key+ ' '+path).readlines()
    return res

def findkey(key, path, keyfile):
    dirs, files = countDir(path)
    dirnum, filenum = len(dirs), len(files)
    print("total dirs count:", dirnum)
    print("total files count:", filenum)

    print(bcolors.OKGREEN + "find key in dir name" +bcolors.ENDC)
    dirhit = []
    for i in tqdm(range(dirnum)): 
        if(os.path.basename(dirs[i]).find(key) != -1):
            dirhit.append(dirs[i])
    print("find {} dir, that has {} in its name".format(len(dirhit), key))

    print(bcolors.OKGREEN + "find key in file name" +bcolors.ENDC)
    filehit = []
    for i in tqdm(range(filenum)): 
        if(os.path.basename(files[i]).find(key) != -1):
            filehit.append(files[i])
    print("find {} file, that has {} in its name".format(len(filehit), key))

    print(bcolors.OKGREEN + "find key in file text" +bcolors.ENDC)
    texthit = []
    for i in tqdm(range(filenum)): 
        text = fgrep(key, files[i])
        texthit.extend(text)
    print("find {} lines, that has {} in its text".format(len(texthit), key))

    with open(keyfile, 'w+') as f:
        for i,d in enumerate(dirhit):
            f.write("dir:{} {}\n".format(i,d))
        for i,f in enumerate(filehit):
            f.write("file:{} {}\n".format(i,f))




if __name__ == "__main__":
    if len(sys.argv) != 5:
        usage()
        sys.exit()

    op = sys.argv[1]
    key = sys.argv[2]
    path = sys.argv[3]
    keyfile = sys.argv[4]
    if os.path.exists(keyfile):
        os.remove(keyfile)

    if op == 'find':
        findkey(key, path, keyfile)
    elif op == 'replace':
        replacekey(key, path, keyfile)
    else:
        print(bcolors.FAIL + "err:only find/replace support" +bcolors.ENDC)

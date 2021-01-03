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

def color_str(s, color):
    return color + s +bcolors.ENDC 

def rmEOL(s):
    return s.replace('\n', '').replace('\r', '')


def usage():
    usage_str = '''
        [Usage]: python3 keyreplace find key root keyfile
                 python3 keyreplace replace key root keyfile
                1.find all keys and record them in keyfile
                2.comment keys in keyfile that do not want to be replaced
                3.replace keys accroding to keyfile
    '''
    print(color_str(usage_str, bcolors.OKGREEN))


def listDir(path):
    dirs_all = []
    dirs = os.listdir(path)
    for d in dirs:
        if((d.startswith('.') == False) and
                (os.path.islink(os.path.join(path,d)) == False) and 
                (os.path.isdir(os.path.join(path,d)) == True)):
            dirs_all.append([path,d])
    return dirs_all

def walkDir(path):
    dirs_all = []
    files_all = []
    for root, dirs, files in os.walk(path):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for d in dirs:
            if os.path.islink(os.path.join(root,d)) == False:
                dirs_all.append([root,d])
        for f in files:
            if os.path.islink(os.path.join(root,f)) == False:
                files_all.append([root,f])
    return dirs_all, files_all

def pathdepth(path):
    a = os.path.abspath(path)
    return len(a.split('/'))

def relpathdepth(root, path):
    return pathdepth(path)-pathdepth(root)

def dgrep(key, root, path):
    if(relpathdepth(root, path) < 1):
        res = os.popen('rg -bn --max-depth 1 '+key+ ' "'+path+'"').readlines()
    elif(relpathdepth(root, path) == 1):
        res = os.popen('rg -bn '+key+ ' "'+path+'"').readlines()
    else:
        pass
    return res

def findkey(key, root, keyfile):
    dirs, files = walkDir(root)
    dirnum, filenum = len(dirs), len(files)
    print("total dirs count:", dirnum)
    print("total files count:", filenum)

    print(color_str("find key in dir name", bcolors.OKGREEN))
    dirhit = []
    for i in tqdm(range(dirnum)): 
        if(dirs[i][1].find(key) != -1):
            dirhit.append(dirs[i])
    print("find {} dir, that has {} in its name".format(len(dirhit), key))
    dirhit.sort(key=lambda elem: elem[0], reverse=False)

    print(color_str("find key in file name", bcolors.OKGREEN))
    filehit = []
    for i in tqdm(range(filenum)): 
        if(files[i][1].find(key) != -1):
            filehit.append(files[i])
    print("find {} file, that has {} in its name".format(len(filehit), key))

    dirs_l2 = listDir(root)
    print(color_str("find key in file text", bcolors.OKGREEN))
    texthit = []
    text = dgrep(key, root, root)
    texthit.extend(text)
    for i in tqdm(range(len(dirs_l2))): 
        text = dgrep(key, root, os.path.join(dirs_l2[i][0],dirs_l2[i][1]))
        texthit.extend(text)
    print("find {} lines, that has {} in its text".format(len(texthit), key))

    print("wirte result to keyfile:", keyfile)
    with open(keyfile, 'w') as kf:
        kf.write("config:{}\n".format(key))
        kf.write("\n;find {} dir, that has {} in its name\n".format(len(dirhit), key))
        for i,d in enumerate(dirhit):
            kf.write("dir:{}:{}:{}\n".format(i,d[0],d[1]))
        kf.write("\n;find {} file, that has {} in its name\n".format(len(filehit), key))
        for i,f in enumerate(filehit):
            kf.write("file:{}:{}:{}\n".format(i,f[0],f[1]))
        kf.write("\n;find {} lines, that has {} in its text\n".format(len(texthit), key))
        for i,t in enumerate(texthit):
            kf.write("text:{}:{}\n".format(i,rmEOL(t)))


def replacekey(key, root, keyfile):
    old_key = ''
    texthit = []
    filehit = []
    dirhit = []
    with open(keyfile) as kf:
        for line in kf.readlines():
            if line.startswith("config:"):
                old_key = rmEOL(line.split(':')[1])
            elif line.startswith("dir:"):
                _,_,root,d = line.split(':')
                dirhit.append([root,rmEOL(d)])
            elif line.startswith("file:"):
                _,_,root,f = line.split(':')
                filehit.append([root,rmEOL(f)])
            elif line.startswith("text:"):
                _,_,f,l = line.split(':')[0:4]
                texthit.append([l,f])
            else:
                pass
    #replace text first, then filename, finally dirname
    print(color_str("replace key in file text", bcolors.OKGREEN))
    for i in tqdm(range(len(texthit))): 
        os.system("sed -i '{}s/{}/{}/g' '{}'".format(texthit[i][0],old_key,key,texthit[i][1]))

    print(color_str("replace key in file name", bcolors.OKGREEN))
    for i in tqdm(range(len(filehit))): 
        os.system("mv '{}' '{}'".format(os.path.join(filehit[i][0],filehit[i][1]), 
                                    os.path.join(filehit[i][0],filehit[i][1].replace(old_key,key))))

    print(color_str("replace key in dir name", bcolors.OKGREEN))
    #sort dirhit by path depth
    dirhit.sort(key=lambda elem: elem[0], reverse=True)
    for i in tqdm(range(len(dirhit))): 
        os.system("mv '{}' '{}'".format(os.path.join(dirhit[i][0],dirhit[i][1]), 
                                    os.path.join(dirhit[i][0],dirhit[i][1].replace(old_key,key))))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        usage()
        sys.exit()

    op = sys.argv[1]
    key = sys.argv[2]
    root = sys.argv[3]
    keyfile = sys.argv[4]

    if op == 'find':
        findkey(key, root, keyfile)
    elif op == 'replace':
        replacekey(key, root, keyfile)
    else:
        print(color_str("err:only find/replace support"), bcolors.FAIL)

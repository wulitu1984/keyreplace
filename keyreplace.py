import os
import sys

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
        [Usage]: python3 keyreplace find/replace keyfile path
                1.find all keys in path and record them in keyfile
                2.comment keys in keyfile that do not want to be replaced
                3.replace keys accroding to keyfile
    '''

    keyfile_str = '''
        [keyfile format]: take 'tutu' as key for example
                ;line start with ';' is a commment line

                ;line start with 'path:' is a path that has key in its name
                path: ./path/tutu/

                ;line start with 'file:' is a file that has key in its name
                file: ./path/tutu/tutu.txt

                ;line start with 'text:' is a key in file's content,follow by a newline that show 
                ;the content of that line
                text: ./path/tutu/tutu.txt 10(linenum) 33(posinline) 
                'this is the line that contained tutu'
    '''
    print(bcolors.WARNING + usage_str +bcolors.ENDC)
    print(bcolors.OKGREEN + keyfile_str +bcolors.ENDC)


def countDir(path):
    c0 = 0
    c1 = 0
    for root, dirs, files in os.walk(path):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for d in dirs:
            if os.path.islink(os.path.join(root,d)) == False:
                c0 += 1

        for f in files:
            if os.path.islink(os.path.join(root,f)) == False:
                c1 += 1

    print("total dirs count:", c0)
    print("total files count:", c1)

    os.system('ls '+path+' -lR|grep "^d"| wc -l')
    os.system('ls '+path+' -lR|grep "^-"| wc -l')



if __name__ == "__main__":
    if len(sys.argv) != 4:
        usage()
        sys.exit()

    path = sys.argv[3]
    countDir(path)

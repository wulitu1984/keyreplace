# keyreplace

find keys in dirname/filename/file-content and replace them

# usage
## find
```shell
python3 keyreplace find key root keyfile
```

keys found will be save in keyfile, which can be edited
so that you can choose which inst should be skipped.
## replace
```shell
python3 keyreplace replace key root keyfile
```

note: subdir name will be replaced first

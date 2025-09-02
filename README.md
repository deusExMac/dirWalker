
# DirWalker

A python program that traverses local file system (fs) structures and can currently apply three operations on the traversed items: 
1) export filesystem structure in desired formats such as html, json and other
2) search for files/directories and
3) displays the differences between two directories and synchronize their contents.

Exporting the a directory structure in html is the default operation. The general idea is to offer an convenient way to browse/navigate the directory/files
Works also for network mapped drives (more testing needed though).

# Version

v0.5b@01092025

  This is the successor of project fsTraversal.

# TODO

There are still some open issues


# How to execute
The operation mode is determined/activated based on the arguments provided. 
- For searching for directory files:
  
```python
dirWalker [regular expression] 
```
searches for files and directories whose name matches [regular expression] 

NOTE: By default, search is case sensitive. Case insesitive search can be supported using global flags in the regular expression. To avoid "global flags not at the start of the expression..." errors when doing case insensitive search global flags should be used as follows: (?i:d) e.g. for case insensitive search containing d .
See https://stackoverflow.com/questions/75895460/the-error-was-re-error-global-flags-not-at-the-start-of-the-expression-at-posi


- For comparing two directories
  
```python
dirWalker -LDIR [directory A path] -RDIR [directory B path] 
```
compares directories [directory A] (left side) and [directory B] (right side) and displays their differences in directories, files as well as the common files. Depending on additiona options can synchronize their contents

- Exporting the directory structure in various formats (in html/json):
 
```python
    dirWalker
```

exports the strcture of the (default) directory in html

All operation modes can be modified with arguments which are shown below.



# Supported arguments

Supported arguments:

## applicable to all operations

```-d [directory]``` : directory to start traversing and apply operation

```-NR```  : non recursive. Won't go into subdirectories

```-mxl [integer]``` : largest level to delve into. Defaults to -1 which means traverse all levels.

```-mxt [duration]``` : how long to execute the operation/traversal. Places a time constraint on traversal. duration is the amount of time in seconds. After [duration] of seconds, an exception is raised and traversal of directories is stopped. Thw walked directories up to that point is shown. Defaults to -1 which means no time constraint. Useful when walking into large/deep directory structures.

```-fip [regular expression]``` : file inclusion regular expression. Regular expression that the file names must match. Only those file names are processed whose names matches this pattern. Defaults to '' which means any file name.

-fxp [regular expression] : file exclusion regular expression. Regular expression that the file names must NOT match. Only those file names are processed whose name does NOT MATCH this pattern. Defaults to '' which means no exclusion constraint on file name. (thos option for convenience)

-dip [regular expression] : directury inclusion regular expression. Regular expression that the DIRECTORY names must match. Only those directory names are processed whose names matches this pattern. Defaults to '' which means any directory name.

-dxp [regular expression] : directory exclusion regular expression. Regular expression that the DIRECTORY names must NOT match. Only those DIRECTORY names are processed whose name does NOT MATCH this pattern. Defaults to '' which means no exclusion constraint on DIRECTORY names. (this option for convenience)

-fsz [file size] : exact size of file to match (currectly in bytes). Defaults to -1 meaning any file size.

-mns [file size] : minimum file size to match. Matches files with a file size of >= [file_size]. Defaults to -1 meaning any file size.

-mxs [file size] : maximum file size to match. Matches files with a file size of < [file_size]. Defaults to -1 meaning any file size.

-nf [number of files] : number of FILES to process. Walking stopes after that number of files have been encountered. Defaults to -1 meaning no constraint on number of files.


-nd [number of directories] : number of DIRECTORIES to process. Walking stopes after that number of directories have been encountered. Defaults to -1 meaning no constraint on number of directories.






-P [html template file] : html template file to use when exporting and displaying fs structure in html. For templating, see section html templates.

-o [file name] : output html file

-s [css style file] : CSS stylesheet file to use

-I [text or file] : Content to use as introduction when exporting in html. Text is first interpreted as a file name. If such file is present, the contents of the file is used as intro. Otherwise the text itself.

-T [string] : Title of the exported html file

-e : urlencode URLs

-O : when exporting  structure as a html tree, expand all subfolders

-D : Open the exported html file in browser

-f : export format. Currently html or json supported. Default html

-LDIR [directory] : First (left) directory of comparison. If this is non empty, difference operation is activated.

-RDIR [directory] : Second (right) director of comparison


# html templates

When exporting directory structure to html, a templating mechanism is used to properly format the encountered objects and page. The templating mechanism features the following:

- a template to format each encountered directory
- a template to format each encountered file
- a template to format the page contining the exported and html formatted fs objects
- a set of pseudovariables to reference specific information of the encountered objects. Pseudovariables are used in templates

Templates are stored in html template files. Template files are structured and contain the templates for each of the mentioned object types above (templates for directories/files/page). Separators define the template sections inside the template files:
<! ---directorytemplate--- > <! ---filetemplate--- > <! ---pagetemplate--- >

Example html template files can be found in folder html/


## Pseudovariables
Pseudovariables are used to reference specific info of objects inside templates. Supported pseudovariables include:

```${CSSFILE}``` : stylesheet file to use in web page

```${BGCOLOR}```: Background color of web page

```${INTROTEXT}```: text to display as introduction

```${TITLE}``` : Title of web page

```${ID}``` : unique id of directory used as element id in html

```${DIRNAME}``` : name of directory

```${SUBDIRECTORY}``` : the formatted traversal content of the directory (recursive or not depending on the settings)

```${DIRLINK}``` : URL to directory

```${FILENAME}``` : name of file

```${PARENTPATH}``` : path to directory containing current directory or file

```${NDIRS}``` : Total number of directories from that level and downwards (recursive)

```${LNDIRS}``` : number of directories in current (local) directory level only (does not include directories in deeper levels)

```${LNFILES}``` : number of files in current (local) directory level only (does not include files in deeper levels)

```${NFILES}``` : Total number of files from that level and downwards (recursive)

```${FILEEXTENSION}``` : extention of file

```${FILELINK}``` : URL to file

```${FILESIZE}``` : size of file

```${FILELASTMODIFIED}``` : last modified date of file

```${LEVEL}``` : level at which directory or file is located

```${INITIALDIRECTORY}``` : the root directory where the traversal started

```${TABLEOFDICTIONARIES}``` : List of directories only

```${RLVLCOLOR}``` : Random color calculated for each level





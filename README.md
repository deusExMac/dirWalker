
# fsTraversal

A python program that traverses local file system (fs) structures and can apply three different operations: 
1) export filesystem structure in html/json
2) search for files/directories and
3) displays the differences between two directories.

Exporting the fs structure in html is the default operation. The general idea is to offer an convenient way to browse/navigate the directory/files
Works also for network mapped drives (more testing needed though).

# Version

v0.9b@29062025

  First version. This project was called dirsToHtml and has been moved here (after major refactoring).

# TODO

Use the visitor design pattern for traversal code.


# How to execute
The operation mode is determined/activated based on the arguments provided. 
- For searching for directory files:
  
```python
fsTraversal [regular expression] 
```
searches for files/directories whose name matches [regular expression] 

NOTE: By default, search is case sensitive. Case insesitive search can be supported using global flags in the regular expression. To avoid "global flags not at the start of the expression..." errors when doing case insensitive search global flags should be used as follows: (?i:d) e.g. for case insensitive search containing d .
See https://stackoverflow.com/questions/75895460/the-error-was-re-error-global-flags-not-at-the-start-of-the-expression-at-posi


- For comparing two directories
  
```python
fsTraversal -LDIR [directory A] -RDIR [directory B]
```
compares directories [directory A] (left side) and [directory B] (right side) and displays their differences in directories, files as well as the common files

- For exporting the directory structure (in html/json):
 
```python
    fsTraversal
```

exports the strcture of the (default) directory in html

All operation modes can be modified with arguments which are shown below.



# Supported arguments

Some command line arguments:

-d [directory] : directory to start traversing and apply operation

-NR  : non recursive. Won't traverse going into subdirectories

-X [regular expression]: exclude directories/files with name matching [regular expression]

-C [regular expression]: include only those directories/files whose names match [regular expression]

-L [integer]: maximum level to delve into during traversal

-S [integer]: minimum file size

-Z [integer]: maximum file size

-Y : ignore directories during traversal

-F : ignore files during traversal

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





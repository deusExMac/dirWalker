
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

## Supported formats

dirWalker supports templates that allows to format the export in any way desired. When exporting, two settings should not be explicitly set:

```-RE``` option to specify how to display empty directories

```-tis``` option to specify the separator between exported items (e.g. empty spacebar for html, , (comma) for json etc)


# Supported arguments

Supported arguments:

## applicable to all operations

```-d [directory]``` : directory to start traversing and apply operation(s)

```-NR```  : non recursive. Won't go into subdirectories

```-mxl [integer]``` : largest level to delve into. Defaults to -1 which means traverse all levels.

```-mxt [duration]``` : how long to execute the operation/traversal. Places a time constraint on traversal. duration is the amount of time in seconds. After [duration] of seconds, an exception is raised and traversal of directories is stopped. Thw walked directories up to that point is shown. Defaults to -1 which means no time constraint. Useful when walking into large/deep directory structures.

```-fip [regular expression]``` : file inclusion regular expression. Regular expression that the file names must match. Only those file names are processed whose names matches this pattern. Defaults to '' which means any file name.

-```fxp [regular expression]``` : file exclusion regular expression. Regular expression that the file names must NOT match. Only those file names are processed whose name does NOT MATCH this pattern. Defaults to '' which means no exclusion constraint on file name. (this option for convenience)

-```-dip [regular expression]``` : directury inclusion regular expression. Regular expression that the DIRECTORY names must match. Only those directory names are processed whose names matches this pattern. Defaults to '' which means any directory name.

-```-dxp [regular expression]``` : directory exclusion regular expression. Regular expression that the DIRECTORY names must NOT match. Only those DIRECTORY names are processed whose name does NOT MATCH this pattern. Defaults to '' which means no exclusion constraint on DIRECTORY names. (this option for convenience)

```-fsz [file size]``` : exact size of file to match (currectly in bytes). Defaults to -1 meaning any file size.

```-mns [file size]``` : minimum file size to match. Matches files with a file size of >= [file_size]. Defaults to -1 meaning any file size.

```-mxs [file size]``` : maximum file size to match. Matches files with a file size of < [file_size]. Defaults to -1 meaning any file size.

```-nf [number of files]``` : number of FILES to process. Walking stops after that number of files have been processed. Defaults to -1 meaning no constraint on number of files.


```-nd [number of directories]``` : number of DIRECTORIES to process. Walking stops after that number of directories have been processed. Defaults to -1 meaning no constraint on number of directories.

```-cdo [relation]``` : the relation to apply on the creation date. Can take the following values: > meaning that the file's creation date should be AFTER the date specified in the cd option, < meaning that the file's creation date should be BEFORE the date specified in the cd option and == meaning that the file's creation date should be exactly equal to the value specified in cd.  Defaults to == .


```-cd [date]``` : creation date. The creation date value in the form of day/month/year with which the creation date is compared to. Defaults to '' meaning no creation date constraint. Creation date constraint applies to files only.


```-lmdo [relation]``` : the relation to apply on the last modification date. Can take the following values: > meaning that the file's last modification date should be AFTER the date specified in the lmd option, < meaning that the file's last modified date should be BEFORE the date specified in the lmd option and == meaning that the file's last modified date should be exactly equal to the value specified in lmd.  Defaults to == .

```-lmd [date]``` : last modification date. The last modification date value in the form of day/month/year with which the file last modification date is compared to. Defaults to '' meaning no last modification date constraint. Last modification date constraint applies to files only.

## Search related

```-P``` : show progress. If present, a window is displayed showing the current progress of the search process.

```-NF``` : no files. Don't search for files.

```-ND``` : no directories. Don't search for directories.

```-I``` : interactive mode. If specified, enters interactive search mode where a trivial interface is shown that allows entering search terms and conduct searches.


## Comparison related

```-LDIR``` : left side directory. During the comparison of two directories one is considered the left side and the other the right side.

```-RDIR``` : right side directory. 

```-sync``` : full synchronization. Synchronizes the directories which after this process will have exactly the same directory and files.

```-fl``` : from left directory side. Add to the directory of the right side the directories and files that are only in the left side. 

```-fr``` : from right directory side. Add to the directory of the left side the directories that are only in the right side. 


## Export related

```-tp [template file]``` : The template file to use for export.

```-tis [string]``` : The character or string to use as separator for the exported and formatted items. Defaults to ''

```-o [filename]``` : The name of the file to save the exported directory traversal


```-s [css files]``` : The list of css files to use for html exports. Can specify more than one css file. In this case, the css files have to be separated by commas (,)


```-i [text]``` : Text to use for introduction. If text is a file, the contents of that file is used as the introduction. Used during export.

```-tl [title]``` : The title of the html page. Defaults to ''.

```-RE``` : Replace empty subdirectories when exporting. Defaults to False

```-E``` : encode URLs. 




# Templates

When exporting directory structures, a templating mechanism is used to properly format the exported directories and files. A template specifies the placeholders using pseudovariables that will be replaced with specific values during export. 

The templating mechanism features the following:

- a template to format each seen directory
- a template to format each seen file
- a template to format the page containing the exported file system objects (file or directory)
- a set of pseudovariables to reference specific information of the encountered objects. Pseudovariables are used in templates

Templates are stored in template files (have the extension .tmpl). Template files are structured and contain the templates for each of the mentioned object types above (templates for directories/files/page). Separators define the template sections inside the template files:
<! ---directorytemplate--- > <! ---filetemplate--- > <! ---pagetemplate--- >

Some example template files, that export the traversed directories in html and json, can be found in folder templates/


## Pseudovariables

Pseudovariables are used to reference specific information of objects inside templates. Pseudovariables are replaced by specific information of objects. These objects include directories, files, exported file, export settings, css files and some other such as title, introduction etc.  

### Directory pseudovariables

For directories, the following pseudovariables are supported:

```${DIRNAME}``` : the name of the directory. 

```${PATH}```: the fullpath of the directory

```${RLVLCOLOR}```: a random color from a pallette. Changes for each directory in each level

```${OPESTATE}``` : In the export, should this directory appear collapsed or not (i.e. showing all its contents)

```${PARENTPATH}``` : Full path of parent

```${LEVELTABS}``` : Number of consecutive tab (\t) characters. Number equals the level of the directory.

```${LEVELNSBP}``` : Number of consecutive tab &NBSP (no break space) characters (used in html documents). Number equals the level of the directory.


```${LNDIRS}``` : number of directories in current (local) directory level only (does not include directories in deeper levels)

```${LNFILES}``` : number of files in current (local) directory level only (does not include files in deeper levels)

```${NFILES}``` : Total number of files from that level and downwards (recursive)

```${NDIRS}``` : Total number of directories from that level and downwards (recursive)



```${SUBDIRECTORY}``` : the formatted traversal content of the directory (recursive or not depending on the settings)


### File pseudovariables

For files, the following pseudovariables are supported:


```${FILENAME}``` : name of file

```${PARENTPATH}``` : path to directory containing current directory or file


```${FILEEXTENSION}``` : extention of file

```${FILELINK}``` : URL to file

```${FILESIZE}``` : size of file

```${FILELASTMODIFIED}``` : last modified date of file

```${LEVEL}``` : level at which directory or file is located

```${INITIALDIRECTORY}``` : the root directory where the traversal started

```${TABLEOFDICTIONARIES}``` : List of directories only

```${RLVLCOLOR}``` : Random color calculated for each level





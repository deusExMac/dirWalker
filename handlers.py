import sys
from abc import ABC, abstractmethod
import os
import re
import clrprint
import datetime
from dateutil.parser import parse

import random

# for stacks
from collections import deque


from utilities import searchNameComplies, printPath, fileInfo, strToBytes, normalizeDateTime, nameMatches



# Colors to choose from if color cycling is enabled (-c)
fontColorPalette = ['#4287f5', '#801408', '#08259c', '#4560d1', '#0a690a', '#9c5f1e', '#9c1e87', '#1313f2', '#f21313', '#34ba4a', '#19084a', '#27889c', '#317534', '#e8740e', '#000000',
                    '#1e5f85', '#2f2561', '#5c0c25', '#324530', '#f07e0c', '#e04e14', '#8f8824', '#478072', '#05998d',  '#1890a8', '#033e6b', '#0a2940', '#281a75', '#453043', '#b50e40',
                    '#fcad03', '#03a1fc', '#24b332', '#851767', '#156e82', '#8c0a0a', '#b51d39', '#232791', '#6e8c0a', '#cc7a16', '#cc4016', '#051c80', '#9e981e', '#409e1e', '#09979c', '#9c0975']



# List of pseudovariable.
# Keys will be replaced in templates by eval-ing the values of the keys.
#
# TODO: Place this in different file?

DIRECTORYPSEUDOVARIABLES = {'${ID}': 'dId',
                            '${DIRNAME}': 'name',
                            '${PATH}':'path',
                            '${RLVLCOLOR}':'random.choice(fontColorPalette)',
                            '${LEVEL}': 'str(level)',
                            '${OPENSTATE}': '""',
                            '${PARENTPATH}':'parent',
                            '${LEVELTABS}':'level*"\t"',
                            '${LEVELNSBP}':'level*"&nbsp;"'}


FILEPSEUDOVARIABLES = {'${ID}': 'dId',
                       '${FILELINK}':'makeHtmlLink(path, name, False)',
                       '${FILENAME}': 'name', '${PATH}':'path', '${RLVLCOLOR}':'random.choice(fontColorPalette)',
                       '${LEVEL}': 'str(level)',
                       '${FILESIZE}': 'str(finfo["size"])',
                       '${FILELASTMODIFIED}':"finfo['lastmodified'].strftime('%d/%m/%Y %H:%M:%S')",
                       '${FILECREATED}': "finfo['creationdate'].strftime('%d/%m/%Y %H:%M:%S')",
                       '${PARENTPATH}':'parent',
                       '${LEVELTABS}':'level*"\t"',
                       '${LEVELNSBP}':'level*"&nbsp;"'}










# Special exception class.
#
# Exception raised when *some* criteria do not hold such as maxDirs or maxFiles.
# Used to terminate traversal immediately without requiring to unfold
# the entire execution stack. Makes things faster.
class criteriaException(Exception):

      def __init__(self, code=-1, message=''):
          super().__init__(message)
          self.errorCode = code
          





# 1. Define the Visitable interface
# Files/Directories extend this class
class Visitable(ABC):

    @abstractmethod
    def accept(self, visitor):
        pass


        

# 2. Define the Visitor interface
# Visitor, which has implemented the actual behaviors i.e. what and how to handle
# each File/directory, is implemented by overriding visit_file and visit_directory.
class Visitor(ABC):

    def __init__(self):
        self.nIgnored = 0
        
    @abstractmethod
    def getCriterium(self, cname='', default=-1):
        pass
    
    @abstractmethod
    def visit_file(self, name, path, level, parent, finfo={}):
        pass

    @abstractmethod
    def visit_directory(self, name, path, level, parent, ldc, lfc, finfo={}):
        pass

    #TODO: Is this correct?
    # Will get overwritten in derived classes if so needed
    def updateCounts(self, path, ldc, lfc, tdc, tfc):
        return

    
    # TODO: is this correct?
    def ignored(self):
        self.nIgnored += 1





###################################################################
#
#  Concrete element classes (Files and Directories).
#  Handle encountered elements while traversing.
#
###################################################################



class File(Visitable):
    def __init__(self, name, path, level=0, parent="", finfo={}):
        self.name = name
        self.path = path
        self.level = level
        self.parent = parent
        self.fileMeta = finfo
        self.ignored = False

    def accept(self, visitor):
        status=visitor.visit_file(self.name, self.path, self.level, self.parent, self.fileMeta)
        if status < 0:
           self.ignored = True 
        


class Directory(Visitable):
    def __init__(self, name, path, level, parent, ldc, lfc):
        self.name = name
        self.path = path
        self.level = level
        self.parent = parent
        self.localDirCount = ldc
        self.localFileCount = lfc
        self.ignored = False


    def accept(self, visitor):
        status=visitor.visit_directory(self.name, self.path, self.level, self.parent,  self.localDirCount, self.localFileCount)
        if status < 0:
           self.ignored = True 


    # Updates the number of local files and directories inside a directory, i.e. not counting into
    # subdirectories. 
    def setLocalCounts(self, ldc, lfc, tdc, tfc, visitor):

        if self.ignored:
           return
        
        self.localDirCount = ldc
        self.localFileCount = lfc
        visitor.updateCounts(self.path, ldc, lfc, tdc, tfc)






        
#####################################################################
#
#
#
# Actual visitor implementations
#
#
#
#####################################################################





#####################################################################
#
#     HTML Exporter
#
#####################################################################




def makeHtmlLink(itemPath, displayAnchor, urlEncode):
    
    if urlEncode:
      return '<a href="' + urllib.parse.quote(itemPath.encode('utf8') ) + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 

    # TODO: Do we need encode/decode here???
    if os.path.isabs(itemPath):
       return '<a href="file://' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>'
    else:
       return '<a href="' + itemPath.encode('utf8').decode() + '" target="_blank" rel="noopener noreferrer">' + displayAnchor + '</a>' 
  




class ExportVisitor(Visitor):
    
    def __init__(self, dirT, fileT, pageT, criteria):

        super().__init__()
        
        self.file_count = 0
        self.directory_count = 0
        self.directoryList = []
        
        self.dirTemplate = dirT
        self.fileTemplate = fileT
        self.pageTemplate = pageT
        self.criteria = criteria
        
        self.stack = deque()


    
    def getCriterium(self, cname='', default=-1):
        return(self.criteria.get(cname, default))
    

    # TODO: Check this
    def showStack(self):
        elem = []
        pos = 0
        while True:
              if len(self.stack) <= 0 :
                 break
                
              sItem = self.stack.pop()
              clrprint.clrprint(f'{len(self.stack) - pos}) {sItem["name"]}', clr='maroon')
              elem.append(sItem)  

        # put back
        for sI in elem[::-1]:
            self.stack.append(sI)




    # Collapses the items in the stack.
    #
    # Stack contains the visited directories in order (as visited) to create the desired html output.
    # Directories in the stack are represented using dictionaries with the following keys:
    # type: type of item (file or directory)
    # collapsed: whether this directory has been collapsed i.e. all its subdirectories have been
    #            visited, the respective html of subdirectories have been calculated and replaced
    #            the subdirectory psudovariable of this directory
    # level: level of item
    # name: full path of item
    # dname: only the name of item
    # html: the html formated item using the loaded templates. If the subdirectory pseudovariable
    #       of this key has been replaced, the directory is considered as collapsed
    #
    # An instance of a stack (first element in stack is always the initial root directory): 
    # 
    # {type:file, level:2, name:testDir0/1/excelFile.xlsx, html:''}
    # {type:file, level:2, name:testDir0/1/anImageFile.jpg, html:''}
    # {type:file, level:1, name:testDir0/1/, html:'...${SUBDIRECTORY}'}
    # {type:file, level:0, name:testDir0/}
    #
    # If collapsed, the stack will become:
    #
    # {type:file, level:1, name:testDir0/1/, html:'...<html of excelFile.xlsx, html of anImageFile.jpg>'}
    # {type:file, level:0, name:testDir0/}
    #
    # in the above example, directory 1 has been collapsed.
    # If exampleDir0 would have another dir (e.g. 2), the stack would become:
    #
    # {type:file, level:1, name:testDir0/2/, html:'...${SUBDIRECTORY}'}
    # {type:file, level:1, name:testDir0/1/, html:'...<html of excelFile.xlsx, html of anImageFile.jpg>'}
    # {type:file, level:0, name:testDir0/}
    #
    # All items in level 1 would be collapsed if all level 1 items have been exhausted (visited). The signal that
    # all items in level 1 have been exhausted is generated when a new directory at a higher/upward level
    # (smaller level) is encountered.
    #
    # By collapsing, the html for the directory that has been exhausted (i.e. all its containing items
    # have been processed) is generated.
    
    def collapse(self, newD={'type':'directory', 'level':0, 'name':''}, stk=None, final=False):


          if stk is None:
             stk = self.stack
             
          #clrprint.clrprint(f"Seen: [{newD['name']}] Level[{newD['level']}]", clr='maroon')
          sDir = ''
          
            
          if len(stk) <= 0:
             return

          top = stk.pop()
          if newD['level'] >= top['level']:
             stk.append(top)
             return
                     
          
          if top['level'] - newD['level'] > 0:
             #clrprint.clrprint(f"Entering collapse", clr='maroon')
              
             # The new directory that WILL be added is at a higher level than to current
             # top of the list. i.e. we went one or more levels up.
             # At this point top is the last directory/file found at the deepest level.
             # Start collapsing now...

                
             # This means that the new directory encounterred
             # is at a higher level. Hence collect all at the
             # same level and merge/concatenate them
             sDir = top['html']
             nAtLevel = 0
             while True:

                 if len(stk) <= 0:
                     break

                 # get object below top (deepest encounterred)   
                 s = stk.pop()
                 #clrprint.clrprint(f"[Collapse]: popped [{s['name']}][{s['level']}]->[{s['collapsed']}] [top:{top['name']}][{top['level']}]->[{top['collapsed']}] [newD:{newD['name']}] [{newD['level']}]", clr='maroon') 
                 if s['level'] == newD['level']:
                    top['html'] = sDir
                    s['html'] = s['html'].replace('${SUBDIRECTORY}', top['html'])
                    s['collapsed'] = True
                    stk.append(s) 
                    stk.append(top)
                    return
                
                
                 if s['level'] == top['level']:
                    nAtLevel += 1 
                    #clrprint.clrprint(f"\t[Collapse]: Adding to [{s['name']}]", clr='yellow') 
                    if s['type']=='directory': 
                       sDir = s['html'] + self.criteria.get('templateItemsSeparator', ' ')  + sDir
                    else:
                       sDir = sDir + self.criteria.get('templateItemsSeparator', ' ') + s['html']
                       
                 elif top['level'] - s['level'] == 1:  
                      sDir = s['html'].replace('${SUBDIRECTORY}', sDir)
                      top = {'type':'directory', 'collapsed':True, 'level':s['level'], 'name':s['name'], 'dname':s['dname'], 'html':sDir}
                      sDir = top['html']
                      nAtLevel = 0
                      
                      
          # TODO: Do we need this?   
          return(sDir)



    def visit_file(self, name, path, level, parent, finfo={}, urlEncode=False):

                
        if self.criteria.get('maxFiles', -1) > 0:
           if self.file_count >= self.criteria.get('maxFiles', -1):
              raise criteriaException(-9, 'Maximum number of FILES reached.')

        if not nameMatches(name, self.criteria.get('fileexclusionPattern', ''), self.criteria.get('fileinclusionPattern', '') ):
           clrprint.clrprint(f'Ignoring FILE [{name}] due to NAME criteria', clr='red')
           self.ignored()
           return(-200)


        if self.criteria.get('minFileSize', -1) >= 0:
           if int(finfo['size']) < self.criteria.get('minFileSize', -1):
              self.ignored() 
              return(-201)

        if self.criteria.get('maxFileSize', -1) >= 0:
           if int(finfo['size']) > self.criteria.get('maxFileSize', -1):
              self.ignored() 
              return(-202)    


        if self.criteria.get('creationDate', '') != '':
           try:
              if self.criteria.get('creationDateOp', '==') == '=':
                 clrprint.clrprint(f"[WARNING] Did you mean == (seen {self.criteria.get('creationDateOp', '==')}")
                 
              expr = f"finfo['creationdate'].date() {self.criteria.get('creationDateOp', '==')} normalizeDateTime(self.criteria.get('creationDate', ''))"
              if not eval(expr):
                 clrprint.clrprint(f'Ignoring FILE [{name}] due to CREATION DATE criteria file created: {finfo["creationdate"].strftime("%d/%m/%Y")}', clr='red') 
                 self.ignored()
                 return(-203)
           except Exception as dateEx:
                 print(f"Invalid date [{self.criteria.get('creationDate', '')}]. Ignored CREATIONDATE constraint. Message:", str(dateEx))
                 

        if self.criteria.get('lastModifiedDate', '') != '':
           try:
              if self.criteria.get('lastModifiedDateOp', '==') == '=':
                 clrprint.clrprint(f"[WARNING] Did you mean == (seen {self.criteria.get('lastModifiedDateOp', '==')}")
                 
              expr = f"finfo['lastmodified'].date() {self.criteria.get('lastModifiedDateOp', '==')} normalizeDateTime(self.criteria.get('lastModifiedDate', ''))"
              if not eval(expr):
                 clrprint.clrprint(f'Ignoring FILE [{name}] due to MODIFIED DATE criteria file created: {finfo["lastmodified"].strftime("%d/%m/%Y")}', clr='red') 
                 self.ignored()
                 return(-203)
           except Exception as dateEx:
                 print(f"Invalid date [{self.criteria.get('lastModifiedDate', '')}]. Ignored MODIFIEDDATE constraint. Message:", str(dateEx))

                 
        self.file_count += 1

        dId = "f" + str(level) + "-" + str( random.randint(0, 1000000) )
        nF={'type':'file',  'collapsed':False, 'level':level, 'name':path, 'dname':name, 'html':''}

        # TODO: Test this more
        nF['html'] = self.fileTemplate
        for k, v in FILEPSEUDOVARIABLES.items():
            nF['html'] = nF['html'].replace(k, eval(v))
            
        #nF['html'] = self.fileTemplate.replace('${FILELINK}', makeHtmlLink(path, name, False)).replace('${FILENAME}', name).replace('${PATH}', path).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', str(level)).replace('${FILESIZE}', str(finfo['size'])).replace('${FILELASTMODIFIED}', finfo['lastmodified'].strftime('%d/%m/%Y %H:%M:%S')).replace('${FILECREATED}', finfo['creationdate'].strftime('%d/%m/%Y %H:%M:%S')).replace('${PARENTPATH}', parent)
        filename, fileExtension = os.path.splitext(path)
        
        if fileExtension == '':
           fileExtension = '.ukn'
        
        # fileExtension starts with a dot
        nF['html'] = nF['html'].replace('${FILEEXTENSION}', fileExtension[1:])

        # Add to stack
        self.stack.append(nF)
        return(0)




    def visit_directory(self, name, path, level, parent, ldc, lfc):

            
        if self.criteria.get('maxDirs', -1) > 0:
           if self.directory_count >= self.criteria.get('maxDirs', -1):
              raise criteriaException(-10, 'Maximum number of DIRECTORIES reached.')
            
        if not nameMatches(name, self.criteria.get('direxclusionPattern', ''), self.criteria.get('dirinclusionPattern', '')):
           clrprint.clrprint(f'Ignoring DIRECTORY [{name}] due to name criteria', clr='red')
           self.ignored()
           return(-201)


        
            
        self.directory_count += 1

        # Add to directory list. Will be used for  ${LISTOFDIRECTORIES}  
        self.directoryList.append(path)
        
        # Add to stack
        nD = {'type':'directory', 'collapsed':False, 'level':level, 'name':path, 'dname':name, 'lndir':-1, 'lnfiles':-1, 'html':''}

        # See if stack can be collapsed
        self.collapse(newD=nD)

        # Add to stack
        dId = "d" + str(level) + "-" + str( random.randint(0, 1000000) )

        # TODO: more tests for this
        nD['html'] = self.dirTemplate
        for k,v in DIRECTORYPSEUDOVARIABLES.items():
            nD['html'] = nD['html'].replace(k, eval(v))
        
        #nD['html'] = self.dirTemplate.replace('${ID}', dId).replace('${DIRNAME}', name).replace('${PATH}', path).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', str(level)).replace("${OPENSTATE}", "").replace('${PARENTPATH}', parent)
        self.stack.append(nD)
        
        return(0)




    # TODO: Add comment.
    def updateCounts(self, path, ldc, lfc, tdc, tfc):
          stkbfr = []
          nPops = 0
          #clrprint.clrprint(f'Searching {path} in stack. Size:{len(self.stack)}')
          while True:  
              itm = self.stack.pop()
              nPops += 1
              if itm['name'] == path:
                  #clrprint.clrprint(f'Found path [{path}]  in stack after {nPops} pops...')
                  itm['html'] = itm['html'].replace('${LNDIRS}', str(ldc)).replace('${LNFILES}', str(lfc)).replace('${NDIRS}', str(tdc)).replace('${NFILES}', str(tfc))
                  self.stack.append(itm)
                  break

              stkbfr.append(itm)

          # put items back with the same order 
          for i in stkbfr[::-1]:
              self.stack.append(i)
              

     
          






#####################################################################
#
#     Search
#
#####################################################################

           
class SearchVisitor(Visitor):
      
      def __init__(self, qry, criteria):

        # TODO: Do we need this?
        #self.scanned_cound = 0

        super().__init__()
        
        self.file_count = 0
        self.directory_count = 0

        self.query = qry
        self.criteria = criteria
        
        self.matches = []




      def getCriterium(self, cname='', default=-1):

          if self.criteria is None:
             return(default)
            
          return(self.criteria.get(cname, default))



      # TODO: change all finfo[] expressions with .get()  
      def visit_file(self, name, path, level, parent, finfo={}):

            
            if self.criteria.get('noFiles', False):
               self.ignored() 
               return(0) 
            
            if self.criteria.get('maxFiles', -1) > 0:
               if self.file_count >= self.criteria.get('maxFiles', -1):
                  raise criteriaException(-9, 'Maximum number of FILES reached.')

            matchedFileName = searchNameComplies(name, self.criteria.get('fileexclusionPattern', ''),
                                                 self.criteria.get('fileinclusionPattern', ''), r'/\1/', False)
            if matchedFileName == '':
               self.ignored() 
               return(0)

            
            if self.criteria.get('fileSize', -1) >= 0:
               if int(finfo['size']) != self.criteria.get('fileSize', -1):
                  self.ignored()
                  return(0)
                   
            if self.criteria.get('minFileSize', -1) >= 0:
               if int(finfo['size']) < self.criteria.get('minFileSize', -1):
                   self.ignored() 
                   return(0)

            if self.criteria.get('maxFileSize', -1) >= 0:
               if int(finfo['size']) > self.criteria.get('maxFileSize', -1):
                   self.ignored() 
                   return(0)

            if self.criteria.get('creationDate', '') != '':
               try:
                 if self.criteria.get('creationDateOp', '==') == '=':
                    clrprint.clrprint(f"[WARNING] Did you mean == (seen {self.criteria.get('creationDateOp', '==')}")
                 
                 expr = f"finfo['creationdate'].date() {self.criteria.get('creationDateOp', '==')} normalizeDateTime(self.criteria.get('creationDate', ''))"
                 if not eval(expr):
                    clrprint.clrprint(f'Ignoring FILE [{name}] due to CREATION DATE criteria file created: {finfo["creationdate"].strftime("%d/%m/%Y")}', clr='red') 
                    self.ignored()
                    return(0)
               except Exception as dateEx:
                    print(f"Invalid date [{self.criteria.get('creationDate', '')}]. Ignored CREATIONDATE constraint. Message:", str(dateEx))
                 

            if self.criteria.get('lastModifiedDate', '') != '':
               try:
                 if self.criteria.get('lastModifiedDateOp', '==') == '=':
                    clrprint.clrprint(f"[WARNING] Did you mean == (seen {self.criteria.get('lastModifiedDateOp', '==')}")
                 
                 expr = f"finfo['lastmodified'].date() {self.criteria.get('lastModifiedDateOp', '==')} normalizeDateTime(self.criteria.get('lastModifiedDate', ''))"
                 if not eval(expr):
                    clrprint.clrprint(f'Ignoring FILE [{name}] due to MODIFIED DATE criteria file created: {finfo["lastmodified"].strftime("%d/%m/%Y")}', clr='red') 
                    self.ignored()
                    return(0)
                
               except Exception as dateEx:
                 print(f"Invalid date [{self.criteria.get('lastModifiedDate', '')}]. Ignored MODIFIEDDATE constraint. Message:", str(dateEx))



            self.file_count += 1

            clrprint.clrprint('\t[F] ', clr='green', end='')
            clrprint.clrprint(f' [{finfo["size"]}][{finfo["creationdate"].strftime("%d/%m/%Y %H:%M:%S")}][{finfo["lastmodified"].strftime("%d/%m/%Y %H:%M:%S")}] ', clr='yellow', end='')
            self.matches.append(path)
            printPath(parent, matchedFileName, '/', 'green')
            return(0)

            


            

      def visit_directory(self, name, path, level, parent, ldc, lfc):

            # noDirs means in essense don't process directories. Just traverse into them.
            # noDirs ignores any directory related constraints.
            if self.criteria.get('noDirs', False):
               # It would be wrong to signal this as ignored here.
               # If ignored, this will result into not traversing into it 
               return(0)
            
            if self.criteria.get('maxDirs', -1) > 0:
               if self.directory_count >= self.criteria.get('maxDirs', -1):
                  raise criteriaException(-10, 'Maximum number of DIRECTORIES reached.')

            # TODO: Should creation/modified date checked as well?
            
            
            matchedDirName = searchNameComplies(name, self.criteria.get('direxclusionPattern', ''), self.criteria.get('dirinclusionPattern', ''), r'/\1/', False)
            if matchedDirName == '':
               self.ignored()  
               return(0)



            self.directory_count += 1
            
            clrprint.clrprint('\t[D] ', clr='red', end='')
            self.matches.append(path)
            printPath(parent, matchedDirName, '/', 'red')
            return(0)





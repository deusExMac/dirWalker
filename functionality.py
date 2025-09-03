# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in
#      the documentation and/or other materials provided with the distribution
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


"""
  Traverses a directory structure on disk and is capable of applying various operations on the encountered
  directories and files. This implementation has support for:
     * exporting and saving directory structure in various formats (html, json, plain text etc) based on a
       templating mechanism
     * searching for directories and files
     * comparing the contents of 2 directories and displaying their differences

  All above behaviors can be modified using criteria.
  For exports, a templating mechanism is used to format the output

  v0.5/mmt/Aug 2025
  
"""


import os
from os.path import join, commonprefix, relpath
import sys
import time

from filecmp import dircmp

import re
import random
import datetime
import clrprint

import json

import shutil # for copying directories

import configparser
import argparse



from utilities import fontColorPalette, readTemplateFile, normalizedPathJoin, fileInfo, strToBytes, nameMatches, getCurrentDateTime, tabularDisplay, getRelativePath
import handlers
import GUI




# Global flag
ON_TRAVERSE_ERROR_QUIT = False

timeStarted = None







# Works only for function traverseDirectory.

def timeit(f):
    
    def timed(*args, **kw):

        # This is done to avoid calling function for every call in
        # recursive functions
        if (f.__name__ == 'export1' ):
            return( f(*args, **kw) )
        
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('[TIMING] func:%r took: %2.4f sec' % \
                 (f.__name__,  te-ts) )
        return result
        

    return(timed)


#####################################################
#
#
#
# Functions traversing directory structure 
#
#
#
#####################################################

# Ths core part of the file system traversal. This traverses all objects.
# How encountered files/directories should be handled are in the visitor classes  
# NOTE: the idea was to keep this function as generic as possible
#
# TODO: Looks too large. Needs to be optimized?
       
def fsTraversal(root, lvl, visitor=None):


    # TODO: check this
    global timeStarted



    #########################################################################################
    # Check if traversal should continue based on the specified constraints. 
    # Some constraints (general purpose such as related to level and execution time
    # are checked at this level.
    #########################################################################################
    
    maxTime = visitor.getCriterium('maxTime', -1)
    if maxTime > 0:
       if timeStarted is None:
          timeStarted = time.perf_counter()
       else:
          # Elapsed in seconds. 
          elapsed = time.perf_counter() - timeStarted
          if elapsed >= maxTime: 
             raise handlers.criteriaException(-10, f'Maximum time constraint of {maxTime}s reached (elapsed:{elapsed:.4f}s).')


      
   # Maximum number of levels to delve into.
   # This is checked here; makes things easier
    mxLvl = visitor.getCriterium('maxLevels', -1)
    if mxLvl > 0:
       if lvl > mxLvl:
          return(0, 0, 0, 0, 0)

    # Update window if gui version is used
    guiWin = visitor.getCriterium('guiwindow', None)
    if guiWin is not None:
       try: 
          visitor.getCriterium('guiprogress', None).configure(text=f'{root}')
          if visitor.file_count + visitor.directory_count > 0:
             visitor.getCriterium('guistatus', None).configure(text_color='green')
             
          visitor.getCriterium('guistatus', None).configure(text=f'Found: {visitor.file_count + visitor.directory_count} (dirs:{visitor.directory_count} files:{visitor.file_count})')
          visitor.getCriterium('guiwindow', None).update_idletasks()
          visitor.getCriterium('guiwindow', None).update()
       except Exception as updEx:
          pass 


    #
    # Ok, get actual list of directories and files
    #
    try:
      path, dirs, files = next(os.walk(root) )
    except Exception as wEx:
      print('Exception during walk:', str(wEx) )
      if ON_TRAVERSE_ERROR_QUIT:
         return(-2, 0, 0, 0, 0)
      else:
         return(0, 0, 0, 0, 0)

        
    dirs.sort()
    files.sort()


    #
    # Handle files
    #
    
    lfc = 0 # local file count
    tfc = 0 # total file count until here
    for encounteredFile in files:
        sys.stdout.flush()
        
        filePath = normalizedPathJoin(root, encounteredFile)          
        fMeta = fileInfo(filePath)
        fv = handlers.File(encounteredFile, filePath, lvl, root, fMeta)
        fv.accept(visitor)
        # TODO: Check this
        if not fv.ignored: 
           lfc += 1
           tfc += 1 

           
    #
    # Handle directories
    #
    
    ldc = 0 # local directory count
    tdc = 0 # total directory count until here 
    for encounteredDirectory in dirs:
        sys.stdout.flush()
        
        directoryPath = normalizedPathJoin(root, encounteredDirectory)           
        dH = handlers.Directory(encounteredDirectory,
                               directoryPath,
                               lvl,
                               root,
                               -1,
                               -1)
        dH.accept(visitor)
        # if not ignored, traverse into if so specified
        if not dH.ignored:
           ldc += 1
           tdc += 1 

           if not visitor.getCriterium('nonRecursive', False):
              # Since not ignored, go into subdirectory and traverse it
              subDirData = fsTraversal(directoryPath, lvl+1, visitor)
              # Update local directory and file counts
              dH.setLocalCounts(subDirData[1], subDirData[2], subDirData[3], subDirData[4], visitor)
              tdc += subDirData[3]
              tfc += subDirData[4]
              if subDirData[0] < 0:
                 return(subDirData[0], ldc, lfc, tdc, tfc)
     
    
    return 0, ldc, lfc, tdc, tfc





###########################################################################
#
#
#
# Actual implementations of specific applications based on the above general
# directory structure function fsTraversal().
#
#
#
###########################################################################




###########################################################################
# Export 
###########################################################################



# TODO: More tests needed
@timeit
def export(criteria={}):
    global timeStarted

    timeStarted = None
    if not os.path.isdir(criteria.get('directory', 'testDirectories/testDir0')):
       clrprint.clrprint(f'[Error] Not such directory [{criteria.get("directory", "testDirectories/testDir0")}]', clr="red")
       return((-2, 0, 0, 0, 0))

    try: 
       dTemp, fTemp, pTemp = readTemplateFile(criteria.get('template', 'templates/htmlTemplate.tmpl'))
    except Exception as tmpException:
       clrprint.clrprint(f'[Error] Error loading template file [{criteria.get("template", "templates/htmlTemplate.tmpl")}]', clr="red") 
       sys.exit(-4)
       
    # Create visitor
    hE = handlers.ExportVisitor(dTemp, fTemp, pTemp, criteria)
    

    
    # Add starting directory to stack
    hE.stack.append({'type':'directory',
                     'collapsed':False,
                     'level':0,
                     'name':criteria.get('directory', 'testDirectories/testDir0'),
                     'dname':criteria.get('directory', 'testDirectories/testDir0'),
                     'html':dTemp.replace('${ID}', '-8888').replace('${DIRNAME}', criteria.get('directory', 'testDirectories/testDir0')).replace('${PATH}', criteria.get('directory', 'testDirectories/testDir0')).replace('${RLVLCOLOR}', random.choice(fontColorPalette)).replace('${LEVEL}', '0')})

    try:
      res=fsTraversal(criteria.get('directory', 'testDirectories/testDir0'), 1, visitor=hE)
    except handlers.criteriaException as ce:
      clrprint.clrprint('Terminated due to criteriaException. Message:', str(ce), clr='red')
      res = (ce.errorCode, -1, -1, hE.directory_count, hE.file_count) # TODO: check and fix this.
    else:
      clrprint.clrprint(f'[{getCurrentDateTime()}] Terminated.', clr='yellow')
      
    # Final merge
    #clrprint.clrprint('\n\n#################################\n##    FINAL MERGE\n#################################\n', clr='yellow')
    hE.collapse(final=True)

    
    
    #
    # Saving to file
    #
    

    # if no directories and no files are in the initial folder,
    # generate an empty result for the SUBDIRECTORY template variable.  
    if res[3] == 0 and res[4] == 0:
       subD = {'html': ''}
    else:   
       subD = hE.stack.pop()

    fullTree = hE.stack.pop()
    fullTree['html'] = fullTree['html'].replace('${LEVELTABS}', "")

    
    #
    # Prepare page template 
    #

    # Replacing external css files in page template.
    # Note: if many css files are specified, separate them with a comma (,)
    cssImports = ''
    for cssFile in criteria.get('css', '').split(','):
         cssImports = cssImports + '<link rel="stylesheet" type="text/css" ' +  'href="'+ cssFile.strip() +'"><br>'

    # These keys have non-seriazable values and hence must be removed before replacing
    # psudovariable ${CRITERIA}
    excludeKeys = ['guiwindow', 'guiprogress', 'guistatus']


    # Start replacements
    
    # Replace psudovariables related to traversal
    h = pTemp.replace('${SUBDIRECTORY}', subD['html']).replace('${TRAVERSALROOTDIR}', criteria.get('directory', 'testDirectories/testDir0')).replace('${LNDIRS}', str(res[1])).replace('${LNFILES}', str(res[2])).replace('${NDIRS}', str(res[3])).replace('${NFILES}', str(res[4])).replace('${TERMINATIONCODE}', str(res[0])).replace('${TREE}', fullTree['html']).replace("${OPENSTATE}", "open").replace("${CRITERIA}", json.dumps({k: criteria[k] for k in set(list(criteria.keys())) - set(excludeKeys)}))
   
    # Replace psudovariables related to page
    h = h.replace('${TITLE}', criteria.get('title', '')).replace('${INTROTEXT}', criteria.get('introduction', ''))
    h = h.replace('${CSS}', cssImports)

    # Should remaining ${SUBDIRECTORY} -signifying empty directories - be replaced?
    if criteria.get('replaceEmptySubdirs', False):
       h = h.replace('${SUBDIRECTORY}', '')

    # Replacements done. Save to file
    with open(criteria.get('outputFile', 'index'+'-'+getCurrentDateTime().replace(':', '-') + '.html'), 'w', encoding='utf8') as sf:
         sf.write(h)

    clrprint.clrprint(f'[{getCurrentDateTime()}] Total file count:{hE.file_count} Total directory count:{hE.directory_count}. Ignored:{hE.nIgnored}', clr='yellow')
  

    return(res)






###########################################################################
# Search 
###########################################################################


# Searching
# NOTE: to avoid error messages when using case insensitive regex, use the following way:
#       (?i:<matching pattern>)
@timeit  
def search(query='', criteria={}):

    global timeStarted

    timeStarted = None
    if query=='':
       # TODO: how to join escaped? 
       q = ' '.join(criteria.get('searchquery', []))
    else:
       q = query
       
      
    criteria['fileinclusionPattern'] = fr'({q})'
    criteria['dirinclusionPattern'] = fr'({q})'

    sV = handlers.SearchVisitor(query, criteria)

    clrprint.clrprint(f'Search results for {q}:', clr='maroon')
    try:
      fsTraversal(criteria.get('directory', 'testDirectories/testDir0'), 1, visitor=sV)
    except handlers.criteriaException as ce:
      clrprint.clrprint('Terminated due to criterialException. Message:', str(ce), clr='red')
    

    clrprint.clrprint(f'\nFound {sV.file_count} files and {sV.directory_count} directories. Ignored:{sV.nIgnored}\n', clr='maroon')
    return(0, sV.directory_count, sV.file_count, sV.nIgnored)




###########################################################################
# Comparing directories and synchronization
# NOTE: implementation is not based on traversal function above.
###########################################################################


#
# Directory and File handlers.
# Used only for the dirDifference function.
#

def defaultDH(l=1, side='right', path='') -> None:
    """
      Default Directory Handler displaying only formatted side and path of Directories
      
      :param l: current level of traversal.
      :param side: left or right sided directory the object specified by path belongs to
      :param path: full path of object.
      :return: None
    """
    pass



def defaultFH(l=1, side='right', path=''):
    """
      Default File Handler displaying only formatted side and path of Files
      
      :param l: current level of traversal.
      :param side: left or right sided directory the object specified by path belongs to
      :param path: full path of object.
      :return: None
    """  
    pass





def dirDifference(L_dir, R_dir, lvl=1, mxLvl=-1, dirOnly=False, matchFilter='', dirHandler=None, fileHandler=None, verbose=False, progress=None):

  """
       Traverses recursively directories and calculates the differences (in terms of directories and files) between
       two directories.
       NOTE: matchFilter does not work as expected. 
       
      :param L_dir: One directory path- left side
      :param fname: Second directory path - right side
      :param lvl: Current level of traversal
      :param dirOnly: If True calculates differences for directories only. Otherwise, also files are taken
      into consideration.
      :param matchFilter: regular expression directory and file names must match. Empty string indicates no filter.
      :param dirHandler: Function to call for each directory encountered
      :param fileHandler:Function to call for each file encountered 
      :return: tuple indicatins status, total objects matching, list of objects only in left side, list of objects only in right side
  """
  
        
  localTotal = 0
  prefix = '\t'*lvl
  L_only, R_only, C_only = {'D':[], 'F':[]}, {'D':[], 'F':[]}, {'D':[], 'F':[]}

  if mxLvl > 0:
     if lvl > mxLvl:
        return (0, localTotal, L_only, R_only, C_only) 


  
  verbose and print('\t'*lvl, f'{40*"+"}\n', '\t'*lvl, f'[L:{lvl}] Comparing ', f'[{L_dir}] ', 'to ', f'[{R_dir}]\n', sep='') 
  

  if L_dir == R_dir:
     verbose and print(f"{L_dir} / {R_dir}")   
     return(-2, 0, L_only, R_only, C_only)

  try:  
    dcmp = dircmp(L_dir, R_dir)
    if not dcmp:
       return(-7, 0, L_only, R_only, C_only)   
              
    L_only['D'] = [ join(L_dir, f)  for f in dcmp.left_only if  (os.path.isdir( join(L_dir, f)  ) and nameMatches(on=f, xP='', iP=matchFilter))  ]
    R_only['D'] = [ join(R_dir, f)  for f in dcmp.right_only if (os.path.isdir( join(R_dir, f)  ) and nameMatches(on=f, xP='', iP=matchFilter))]
    # for common files, take relative paths
    C_only['D'] = [ f  for f in dcmp.common_dirs if nameMatches(on=f, xP='', iP=matchFilter)  ]
    
    if not dirOnly:       
       L_only['F'] = [ join(L_dir, f)  for f in dcmp.left_only if ((not os.path.isdir( join(L_dir, f))) and nameMatches(on=f, xP='', iP=matchFilter)) ]
       R_only['F'] = [ join(R_dir, f)  for f in dcmp.right_only if ((not os.path.isdir( join(R_dir, f))) and nameMatches(on=f, xP='', iP=matchFilter))]
       # We use the left-sided root as the prefix for common files.
       # TODO: relative here too? 
       C_only['F'] = [ join(L_dir, f) for f in dcmp.common_files if nameMatches(on=f, xP='', iP=matchFilter)  ]

    
    
    # TODO: This is not correct. Recheck and redesign it   
    if dirHandler:  
       for d in L_only['D']:
           dirHandler(lvl, 'left', d)
           
       for d in R_only['D']:
           dirHandler(lvl, 'right', d)

       for cd in  dcmp.common_dirs:
           dirHandler(lvl, 'common', cd)    


    if (not dirOnly) and fileHandler:
       for f in L_only['F']:    
           fileHandler(lvl, 'left', f)
       
       for f in R_only['F']:    
           fileHandler(lvl, 'right', f) 

       for cf in  dcmp.common_files:
           fileHandler(lvl, 'common', cf)          

    
    
    verbose and print('\t'*lvl + f'l_only={len(L_only["D"]) + len(L_only["F"])} r_only={len(R_only["D"]) + len(R_only["F"])} common_dirs={len(dcmp.common_dirs)} common_files={len(dcmp.common_files)}')  
    
    localTotal = len(L_only['D']) + len(L_only['F']) + len(R_only['D']) + len(R_only['F']) + len(dcmp.common_dirs) + len(dcmp.common_files)

    
    
    # Handle directories having common names. I.e. traverse these and
    # find their differences
    #
    # TODO: optimize next two lines?
    
    cd =  C_only['D'].copy()
    C_only['D'] = [ join(L_dir, f) for f in cd]
    for sub_dir in cd:
                 
        s, lt, new_L, new_R, new_C = dirDifference(join(L_dir, sub_dir), join(R_dir, sub_dir), (lvl+1), mxLvl, dirOnly, matchFilter, dirHandler, fileHandler, verbose, progress)

        if s < 0:
           return(s, localTotal, L_only, R_only, C_only)
      
        L_only['D'].extend(new_L['D'])
        if not dirOnly:
           L_only['F'].extend(new_L['F'])

        R_only['D'].extend(new_R['D'])
        if not dirOnly:
           R_only['F'].extend(new_R['F'])

        C_only['D'].extend( new_C['D'] )
        if not dirOnly:
           C_only['F'].extend( new_C['F'] )
        
        verbose and print('\t'*lvl,  f'>> # items from level below {lt}', sep='')  
        localTotal = localTotal + lt

    verbose and print('\t'*lvl + f'returning {localTotal}\n', '\t'*lvl, f'{40*"-"}', sep='')           
    return(0, localTotal, L_only, R_only, C_only)

  except KeyboardInterrupt as kI:
         #
         # Do a full/cascading unrolling. raising exceptions until
         # top level is reached; from which it is returned
         #
         print(f'\n\n[L:{lvl}] Interupted in {L_dir} {R_dir}. Terminating: Total:{localTotal}')
         if lvl > 1:
            raise kI
         else:
            return( -1, localTotal, L_only, R_only, C_only )  






# This is to be called for comparing directories
def compareDirectories(cfg={}):
    
    sts, ltotal, lonly, ronly, conly = dirDifference(L_dir=cfg.get('leftdirectory', 'testDirectories/testDir0'),
                                                     R_dir=cfg.get('rightdirectory', 'testDirectories/testDir1'),
                                                     lvl=1,
                                                     matchFilter=cfg.get('fileinclusionPattern', ''))
    tabularDisplay(cfg.get('leftdirectory', 'testDirectories/testDir0'), lonly,
                              cfg.get('rightdirectory', 'testDirectories/testDir1'), ronly,
                              conly)

    # TODO: Next needs refactoring. It's ugly
    if cfg.get('synchronize', False):
       print('Synchronizing...')
       print('\tSynchronizing directories')
       
       for i, d in enumerate(lonly['D']):    
           destPath = cfg.get('rightdirectory', 'testDirectories/testDir0') + os.sep + getRelativePath(d, cfg.get('leftdirectory', 'testDirectories/testDir0'))
           print(f"\t\t{i}/{len(lonly['D']) + len(ronly['D'])} copying {d} to {destPath}")
           shutil.copytree(d, destPath, dirs_exist_ok=True)
           
       for i, d in enumerate(ronly['D']):
           destPath = cfg.get('leftdirectory', 'testDirectories/testDir0') + os.sep + getRelativePath(d, cfg.get('rightdirectory', 'testDirectories/testDir1'))
           print(f"\t\t{i+len(lonly['D'])}/{len(ronly['D']) + len(lonly['D'])} copying {d} to {cfg.get('leftdirectory', 'testDirectories/testDir0')}")
           shutil.copytree(d, destPath, dirs_exist_ok=True)

       print('\tSynchronizing files')     
       for f in lonly['F']:
           parent, nm = os.path.split(f)
           newPath = cfg.get('rightdirectory', 'testDirectories/testDir1') + os.sep + nm
           print(f"\t\tcopying {f} to {newPath}")
           shutil.copy(f, newPath)

       for f in ronly['F']:
           parent, nm = os.path.split(f)
           newPath = cfg.get('leftdirectory', 'testDirectories/testDir0') + os.sep + nm
           print(f"\t\tcopying {f} to {newPath}")
           shutil.copy(f, newPath)
    elif cfg.get('fromleftonly', False):
         print(f"Copying ONLY from left side {cfg.get('leftdirectory', 'testDirectories/testDir0')}...")
         for i, d in enumerate(lonly['D']):    
           destPath = cfg.get('rightdirectory', 'testDirectories/testDir0') + os.sep + getRelativePath(d, cfg.get('leftdirectory', 'testDirectories/testDir0'))
           print(f"\t\t{i}/{len(lonly['D']) + len(ronly['D'])} copying {d} to {destPath}")
           shutil.copytree(d, destPath, dirs_exist_ok=True)

         for f in lonly['F']:
           parent, nm = os.path.split(f)
           newPath = cfg.get('rightdirectory', 'testDirectories/testDir1') + os.sep + nm
           print(f"\t\tcopying {f} to {newPath}")
           shutil.copy(f, newPath)
    elif  cfg.get('fromrightonly', False):
          print(f"Copying ONLY from right side {cfg.get('rightdirectory', 'testDirectories/testDir1')}...")
          for i, d in enumerate(ronly['D']):
           destPath = cfg.get('leftdirectory', 'testDirectories/testDir0') + os.sep + getRelativePath(d, cfg.get('rightdirectory', 'testDirectories/testDir1'))
           print(f"\t\t{i+len(lonly['D'])}/{len(ronly['D']) + len(lonly['D'])} copying {d} to {cfg.get('leftdirectory', 'testDirectories/testDir0')}")
           shutil.copytree(d, destPath, dirs_exist_ok=True)

          for f in ronly['F']:
           parent, nm = os.path.split(f)
           newPath = cfg.get('leftdirectory', 'testDirectories/testDir0') + os.sep + nm
           print(f"\t\tcopying {f} to {newPath}")
           shutil.copy(f, newPath) 

           









def interactiveSearch(cfg={}):
    
     while (True):
            q = input('Give query (regular expression - use (?i:<matching pattern>) for case sensitive search)> ')
            if q == '':
               continue

            if q.lower()=='eof':
               print('terminating.') 
               break

            if cfg.get('progress', False):
               GUI.progressCommand('search', q, cfg) 
            else:
               # Simple search without progress 
               res = search(q,  cfg)
               print(res)
               





def selector(mode='export', cfg={}):
      
    clrprint.clrprint(f"\nStarting [{mode}] mode from root [{cfg.get('directory', 'testDirectories/testDir0')}] with following paramters:")
    clrprint.clrprint(f"{cfg}\n", clr='yellow')
    for i in range(6):
        clrprint.clrprint(f'[{5-i}]', clr=random.choice(['red', 'blue', 'green', 'yellow', 'purple', 'black']), end='')
        time.sleep(1)

    clrprint.clrprint(f'\n[{getCurrentDateTime()}] Started', clr='yellow')
    time.sleep(0.5) # small delay to allow starting messages to appear (even when executed from within IDLE)  


    if mode == 'export':
       if not cfg.get('progress', False): 
          result = export(cfg)
          print(result)
       else:
          GUI.progressCommand('export', '', cfg)  
    elif mode == 'search':
         if cfg.get('interactive'):
            interactiveSearch(cfg)
         elif not cfg.get('progress', False): 
               result=search(query='', criteria=cfg)
               print(result)
         else:
               GUI.progressCommand('search', ' '.join(cfg.get('searchquery', [])), cfg)  
    else:
         compareDirectories(cfg)
         
            

























     


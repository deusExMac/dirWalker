#
# This program traverses a directory structure on the disk and depending on its operation mode:
#
#    1) exports the directory structure and files in json or html format that can be navigated
#    2) searches for directories/files complying to criteria.
#
# Without any arguments, the script operates in export functionality. To activate search functionality
# simply add a search string
#
#
#   How to execute to export directories/files for export in navigationable html form:
#      -c -I intro.txt -d ./ManolisMTzagarakis -T "Δημοσιέυσεις Εμμανουήλ Μ. Τζαγκαράκη"
#
#
# NOTES:
#  Does not work YET as indended. The main problem is that some
#  links aren't working. Probably has to do with spaces in file names.
#
#
# VERSION HISTORY:
#
#  -28/06/2025: v0.9
#      * Refactored major parts.
#
#  -29/12/2022: v0.8b
#      * Complete and major overhaul of source code. functions refactored and added, arguments
#        added, templating redesigned.
#
#  -12/02/2021: v0.1
#      * first working (more or less) release.
#
#
#   v0.9  rd28062025
#   v0.8b rd29122022 
#   v0.1 rd12022021 




 

import os
import os.path
import sys, getopt

import configparser
import argparse
import json

import re
import io
import random


import webbrowser

import utilities





backgroundPalette = ['#FAF4B7', '#F9F9F9', '#CDF0EA', '#FFF5E4', '#C8FFD4',
                     '#FDFDBD', '#F5EFE6', '#E8DFCA', '#AEBDCA', '#D2DAFF',
                     '#C4DFAA', '#90C8AC', '#F0EBE3', '#FAF0D7', '#68A7AD',
                     '#F8ECD1','#F3E9DD',  '#F3E9DD', '#C3DBD9', '#D3DEDC',
                     '#F0ECE3', '#D3E4CD', '#F6EABE', '#FEF5ED']

backgroundPalette = [
    "#ffe9ee",  # lighter pink
    "#def3ff",  # lighter sky blue
    "#e1fff0",  # lighter mint green
    "#ffffe1",  # lighter pastel yellow
    "#f2e6ff",  # lighter lavender
    "#fff2e6",  # lighter peach
    "#edf9f7",  # lighter pale aqua
    "#fbf2f7",  # lighter blush
    "#eafaff",  # lighter soft blue
    "#f5faef",  # lighter pale lime
    "#ffeeef",  # lighter baby pink
    "#f9f6e7",  # lighter light beige
    "#f6ecff",  # lighter light violet
    "#fceef4",  # lighter pink mist
    "#e8f7e4",  # lighter tea green
    "#f9fff9",  # lighter honeydew
    "#fff3f6",  # lighter rose
    "#eef6f7",  # lighter very light blue
    "#ecfdf0",  # lighter mint ice
    "#fff8fa",  # lighter lavender blush
    "#f9f7da",  # lighter lemon chiffon
    "#fef1f2",  # lighter light coral
    "#eaf6ff",  # lighter baby blue eyes
    "#f9fff5",  # lighter pale green
    "#f9f2ff",  # lighter soft orchid
    "#e4fefa",  # lighter pale turquoise
    "#f4fbf8",  # lighter very light mint
    "#fff4eb",  # lighter light apricot
    "#f7fbff",  # lighter alice blue
    "#fcf9f0",  # lighter pale almond
]





def strToBool(v):
  return v.lower() in ("yes", "true", "t", "1")



#
# Takes as input a string that is a data size measurement
# and converts it to bytes returning is at an integer.
# The input string may also have a measurement in the form
# of K, M, G, T for kilo-, mega-, giga-, tera,
#
def strToBytes( amount ):
    if amount.lower().endswith('k'):
        try:
          sz = int( amount[:-1] )*1024
        except Exception as convEx:
          return(-3)
        
    elif amount.lower().endswith('m'):
       try:
          sz = int( amount[:-1] )*1024*1024
       except Exception as convEx:
          return(-3)

    elif amount.lower().endswith('g'):
       try:
          sz = int( amount[:-1] )*1024*1024*1024
       except Exception as convEx:
          return(-3)
    elif amount.lower().endswith('t'):
       try:
          sz = int( amount[:-1] )*1024*1024*1024*1024
       except Exception as convEx:
          return(-3)
    else:
         try:
          sz = int(amount)
         except Exception as convEx:
            return(-3) 
        
    return(sz)


def generateDefaultConfiguration():
    cS = configparser.RawConfigParser(allow_no_value=True)
    cS.add_section('operation')
    cS.add_section('traversal')
    cS.add_section('export')
    cS.add_section('html')
    cS.add_section('json')
    cS.add_section('search')
    cS.add_section('difference')
    
    cS.add_section('Rules')
    cS.add_section('Crawler')
    cS.add_section('Storage')
    cS.add_section('Shell')
    return(cS)


# TODO: Check if all command line arguments are included
def updateConfiguration( c, ar ):
   
    if ar['directory'] != '':
       c.set('traversal', 'directory', ar['directory'] )
    else:
        if c.get('traversal', 'directory', fallback='') == '':
           c.set('traversal', 'directory', 'exampleDir' )

    if ar['nonrecursive']:
       c.set('traversal', 'nonrecursive', 'True' )

    if ar['included'] != '':  
       c.set('traversal', 'included', ar['included'])

    if ar['excluded'] != '':   
       c.set('traversal', 'excluded', ar['excluded'])

    if ar['maxlevel'] != '':   
       c.set('traversal', 'maxlevel', ar['maxlevel'])


    if ar['exportformat'] != '': 
       c.set('export', 'exportformat', ar['exportformat'] )

    if ar['htmltemplate'] != '': 
       c.set('html', 'htmltemplate', ar['htmltemplate'] )

    if ar['outputhtmlfile'] != '':   
       c.set('html', 'outputhtmlfile', ar['outputhtmlfile'])

    if ar['cssfile'] != '':        
       c.set('html', 'cssfile', ar['cssfile'])

    if ar['urlencode']:        
       c.set('html', 'urlencode', 'True' )

    if ar['introduction'] != '':         
       c.set('html', 'introduction', ar['introduction'] )

    if ar['title'] != '':    
       c.set('html', 'title', ar['title'] )

    if ar['opendirectories']:   
       c.set('html', 'opendirectories', 'True' )

    if ar['displayoutput']:   
       c.set('export', 'displayoutput', 'True' )


    if ar['searchquery']:
       c.set('search', 'searchquery', ' '.join(ar['searchquery']) )

    if ar['nofiles']:   
       c.set('search', 'nofiles', 'True' )

    if ar['nodirectories']:   
       c.set('search', 'nodirectories', 'True')

    if ar['debug']:
        c.set('traversal', 'debug', 'True') 

    if ar['minfilesize'] != '':
       c.set('traversal', 'minfilesize', ar['minfilesize'])

    if ar['maxfilesize'] != '':
       c.set('traversal', 'maxfilesize', ar['maxfilesize'])

    if ar['ldir'] != '':
       c.set('difference', 'ldir', ar['ldir'])

    if ar['rdir'] != '':
       c.set('difference', 'rdir', ar['rdir'])     
    




def printConfiguation(cfg):
     for s in cfg.sections():
         print("Section [", s, "]", sep="")
         for key, value in cfg[s].items():
             print( "\t-", key, "=", value)




###################################################
#
# TODO: main() needs serious refactoring.
#       Currently it is only here to demonstrate
#       the functions in utilities.py
#
###################################################

def main():


  # 
  # Parse command line arguments - if any
  #
  try:
      
   cmdArgParser = argparse.ArgumentParser(description='Command line arguments', add_help=False)

   # Configuration file
   cmdArgParser.add_argument('-c', '--config', default="fsTraversal.conf")
    
   # Directory traversal related and criteria
   cmdArgParser.add_argument('-d', '--directory', default="exampleDir")
   cmdArgParser.add_argument('-NR', '--nonrecursive', action='store_true')
   cmdArgParser.add_argument('-X', '--excluded', default="")
   cmdArgParser.add_argument('-C', '--included', default="")
   cmdArgParser.add_argument('-L', '--maxlevel', default='')
   cmdArgParser.add_argument('-S', '--minfilesize',  default='')
   cmdArgParser.add_argument('-Z', '--maxfilesize',  default='')


   # SEARCH functionality related
   # If set, don't search for files. 
   cmdArgParser.add_argument('-F', '--nofiles', action='store_true')
   # If set, don't search for directories
   cmdArgParser.add_argument('-Y', '--nodirectories', action='store_true')

  
   # REMAINDER is searchquery. Search query is interpreted as a regular expression
   cmdArgParser.add_argument('searchquery', nargs=argparse.REMAINDER, default=[])
   

  
   # EXPORT functionality related.
   # html related output

   # Template to use.
   cmdArgParser.add_argument('-P', '--htmltemplate', default="html/template1.html")
   cmdArgParser.add_argument('-o', '--outputhtmlfile', default="index.html")
   cmdArgParser.add_argument('-s', '--cssfile', default="html/style.css")
   cmdArgParser.add_argument('-I', '--introduction', default="")
   cmdArgParser.add_argument('-T', '--title', default="")
   cmdArgParser.add_argument('-e', '--urlencode', action='store_true')
   # In case directories are displayed hierarchical, should they
   # appear fully open or closed
   cmdArgParser.add_argument('-O', '--opendirectories', action='store_true')


   

   
   # Automatically open the outputfile with a browser when exporting
   # directory structure  
   cmdArgParser.add_argument('-D', '--displayoutput', action='store_true')
   
   cmdArgParser.add_argument('-G', '--debug', action='store_true')


   
   # What to do: export or simple search? 
   #cmdArgParser.add_argument('-m', '--mode', default="export")
   # Export format
   # Two values supported: html and json
   cmdArgParser.add_argument('-f', '--exportformat', default="")



   # DIRECTORY DIFFERENCE functionality related
   cmdArgParser.add_argument('-LDIR', '--ldir', default="")
   cmdArgParser.add_argument('-RDIR', '--rdir', default="")


   
   # We only parse known arguments (see previous add_argument calls) i.e. arguments
   # that the app requires for starting.
  
   knownArgs, unknownArgs = cmdArgParser.parse_known_args()
   args = vars( knownArgs )
   
  except Exception as argumentException:
    print('Argument error:', str(argumentException))
    sys.exit(-4)


  #
  # Read configuration file
  #
  configFile = args['config']
  config = generateDefaultConfiguration()
  if os.path.exists(configFile):
     print('\n\nLoading configuration settings from [', configFile, ']\n', sep='' ) 
     config.read(configFile)
     #print( config.get('html', 'directoryTemplate', fallback='${DIRECTORYNAME}') )

     if args['htmltemplate'] != '':
        #config['htmltemplate'] = args['htmltemplate']
        config.set('html', 'htmltemplate', args['htmltemplate'] )



  # Override any config setting with args setting, if set
  # Below this point, only config[xxx] expressions should be used.
  
  updateConfiguration( config, args )
  


  
   
   
  # Setting the mode (search or extract directory structure). This
  # is how it is determined if the script operates in export or search mode.
  #
  # This is determined based on arguments: if a query is provided
  # the script enters search mode. If query is missing, it's in
  # export mode.
  #
  if config.get('search', 'searchquery', fallback='') != '':
     config.set('operation', 'mode', 'search')
     # make a capturing group from regex given
     # TODO: check if it is already a capturing group
     #args['included'] =  args['searchquery'][0]
     config.set('traversal', 'included', config.get('search', 'searchquery', fallback='') )
  elif config.get('difference', 'ldir', fallback='') != '':
       config.set('operation', 'mode', 'difference') 
  else:
     config.set('operation', 'mode', 'export') 
     


  
  if config.getboolean('traversal', 'debug', fallback=False):
     print("\n>>>Program starting with following options:")
     print("\t-Root directory:", config.get('traversal', 'directory', fallback='exampleDir') )
     print("\t-Max level:", config.get('traversal', 'maxlevel', fallback='-1') )
     print("\t-Recursive directories:", not config.getboolean('traversal', 'nonrecursive', fallback=False ) )
     print("\t-Output file:", config.get('html', 'outputhtmlfile', fallback='index.html') )
     print("\t-Html encoding:", "???")
     print("\t-Color cycling:", "???")
     print("\t-Debug mode:", "???" )
     print("\t-Excluded file list:", config.get('traversal', 'excluded', fallback='') )
     print("\t-Included file list:", config.get('traversal', 'included', fallback='') )
     print("\t-Mode:", config.get('operation', 'mode', fallback='export'))
     print("\t-Format:", config.get('export', 'exportformat', fallback='html'))
     print("\t-Template file:", config.get('html', 'htmltemplate', fallback='html/template3.html') )
     print("\t-Style sheet:", config.get('html', 'cssfile', fallback='') )
     print("\t-Title text:", config.get('html', 'introduction', fallback='')  )
     print("\t-Intro text:", config.get('html', 'title', fallback='') )
     print("\t-Include directories in search:", not config.getboolean('search', 'nodirectories', fallback=False) )
     print("\t-Include files in search:", not config.getboolean('search', 'nofiles', fallback=False) )




  if (not os.path.isdir( config.get('traversal', 'directory', fallback='exampleDir') )):
      print("\n\nError:Root directory [", config.get('traversal', 'directory', fallback='exampleDir'),"] is not a valid directory. Please make sure that the directory exists and is accessible.\n")
      sys.exit(-2)


  # TODO: Added for debugging reasons. 
  #sys.exit(-8)

  
  ###################################################
  #
  # Export functionality
  #
  ###################################################

  if config.get('operation', 'mode', fallback='export') == 'export':

     if config.get('export', 'exportformat', fallback='html') == 'json':
        #print('Exporting in json format')
        print(30*'*')
        print('* Entering JSON export mode...')
        print(30*'*')
        dCnts = utilities.jsonTraverseDirectory(config.get('traversal', 'directory', fallback='exampleDir'),
                                                1,
                                                not config.getboolean('traversal', 'nonrecursive', fallback=False ),
                                                config.getint('traversal', 'maxlevel', fallback=-1),
                                                config.get('traversal', 'excluded', fallback=''),
                                                config.get('traversal', 'included', fallback=''),
                                                config.getboolean('html', 'urlencode', fallback=False))
                                          
        print( json.dumps(dCnts) )
        with open("fsStructure.json", "w") as outfile:
          json.dump(dCnts, outfile)

        if config.getboolean('export', 'displayoutput', fallback=False):
           outputFullPath = os.path.join(os.getcwd(), 'fsStructure.json')
           webbrowser.open('file://' + outputFullPath)
     
        
           
     elif config.get('export', 'exportformat', fallback='html') == 'html':
  
          ###################################################
          #
          # Export (html output)
          #
          ###################################################
          dT, fT, pT = utilities.readHTMLTemplateFile(config.get('html', 'htmltemplate', fallback='html/template1.html' ),
                                              dm='<!---directorytemplate--->\n',
                                              fm='<!---filetemplate--->\n',
                                              pm='<!---pagetemplate--->\n')

  
          config.set('html', 'directoryTemplate', dT)
          config.set('html', 'fileTemplate', fT) 
          config.set('html', 'pageTemplate', pT)
  
          print(30*'*')
          print('* Entering HTML export mode...')
          print(30*'*')
          print(f'Exporting {args["directory"]} in html...') 
          print('\tUsing template file:', config.get('html', 'htmltemplate', fallback='html/template1.html'))
          print('\tSaving output to:', config.get('html', 'outputhtmlfile', fallback='index.html') )


          dL = []
          fL = []
          d, f, ld, lf, traversalResult = utilities.traverseDirectory(
                                                      config.get('traversal', 'directory', fallback='exampleDir'),
                                                      1,
                                                      not config.getboolean('traversal', 'nonrecursive', fallback=False),
                                                      config.getint('traversal', 'maxlevel', fallback=-1),
                                                      config.get('traversal', 'excluded', fallback=''),
                                                      config.get('traversal', 'included', fallback=''),
                                                      dL, fL,
                                                      config.getboolean('html', 'urlencode', fallback=False),
                                                      config.get('html', 'directoryTemplate', fallback=''),
                                                      config.get('html', 'fileTemplate', fallback=''),
                                                      False)


          #
          #
          # Prepare html output using the html template
          #
          # TODO: needs serious refactoring
          #
          #


          
          # Read template file. Exit in case of error
          # TODO: this needs to go.
          htmlTemplate = ""
          try:
            with open( config.get('html', 'htmltemplate', fallback='html/template1.html'), 'r', encoding='utf8') as content_file:
                 htmlTemplate = content_file.read()
          except Exception as rdEx:
                 print('Error reading template html file [', config.get('html', 'htmltemplate', fallback='html/template1.html'),']:', str(rdEx))
                 sys.exit(-3)


          # TODO: This replaces above. More tests needed.
          htmlTemplate = config.get('html', 'pageTemplate', fallback='')
          

          
          # Check if introdution is a file. If so, read its contents
          # and use this as the introduction to the html export.
          if (os.path.isfile(config.get('html', 'introduction', fallback='')) ):
              try:
                with open( config.get('html', 'introduction', fallback=''), encoding="utf-8" ) as introf:
                     #args['introduction'] = introf.read() 
                     config.set('html', 'introduction', introf.read() ) # replace it
              except Exception as introLoadEx:
                     print('ERROR: Error reading file [', config.get('html', 'introduction', fallback=''), ']:', str(introLoadEx) )
                     sys.exit(-1)


          #    
          # Replace all pseudovariables in the template file
          #
          htmlTemplate = htmlTemplate.replace("${CSSFILE}", config.get('html', 'cssfile', fallback='html/style.css') )
          htmlTemplate = htmlTemplate.replace("${BGCOLOR}", random.choice(backgroundPalette) )
          
          htmlTemplate = htmlTemplate.replace("${TITLE}", config.get('html', 'title', fallback='') )
          htmlTemplate = htmlTemplate.replace("${INTROTEXT}", config.get('html', 'introduction', fallback='') )


  
          
          # Replace OPENSTATE pseudovariable that specifies if
          # directories should be shown expanded or not.
          if config.getboolean('html', 'opendirectories', fallback=False):
             traversalResult = traversalResult.replace("${OPENSTATE}", "open")
          else:
             traversalResult = traversalResult.replace("${OPENSTATE}", "") 


          #
          # Replace pseudovariables for source directory in the template file - 
          # source directory is not returned by traversals.
          htmlTemplate = htmlTemplate.replace("${INITIALDIRECTORY}", config.get('html', 'initialdirectorytext',
                                                                                fallback=config.get('traversal', 'directory', fallback='exampleDir') ) )
          
          
          # The actual traversed directories formatted in html          
          htmlTemplate = htmlTemplate.replace("${SUBDIRECTORY}", traversalResult )
          
          htmlTemplate = htmlTemplate.replace("${LNDIRS}", str(ld) )
          htmlTemplate = htmlTemplate.replace("${LNFILES}", str(lf) )

          # Generating directory index 
          tod = '<ul>'
          for dEntry in dL:
              tod = tod + '<li>' + '<a href="#' + dEntry['id'] + '">' + dEntry['name'] + '</a></li>'

          tod = tod + '</ul>'

          
          
          htmlTemplate = htmlTemplate.replace('${LISTOFDIRECTORIES}', tod)
          
          print('\nDirectory [', config.get('traversal', 'directory', fallback='exampleDir') , ']:')
          print("\tTotal number of directories:", d)
          print("\tTotal number of files:", f)
          
          
          with io.open(config.get('html', 'outputhtmlfile', fallback='index.html'), 'w', encoding='utf8') as f:
               f.write(htmlTemplate)

          if config.getboolean('export', 'displayoutput', fallback=False):
             outputFullPath = config.get('html', 'outputhtmlfile', fallback='index.html')
             if not os.path.isabs(outputFullPath):
                outputFullPath = os.path.join(os.getcwd(), config.get('html', 'outputhtmlfile', fallback='index.html') )

             webbrowser.open('file://' + outputFullPath)
     
     else:
          print('Invalid export format:', config.get('export', 'exportformat', fallback='html') )
          sys.exit(-9)
           



  ###################################################
  #
  # search functionality
  #
  ###################################################
  if config.get('operation', 'mode', fallback='export') == 'search':

     print(30*'*')
     print('* Entering SEARCH mode...')
     print(30*'*')
     print(f"Searching for {config.get('traversal', 'included', fallback='')} in {args['directory']}\n\n")
     print("Result list:")
     config.set('traversal', 'included', "("+config.get('traversal', 'included', fallback='') +")" )
     #args['included'] = '(' + args['included'] + ')'  
     results=[]
     fCriteria = {'minfilesize': strToBytes(config.get('traversal', 'minfilesize', fallback='-1') ),
                  'maxfilesize': strToBytes(config.get('traversal', 'maxfilesize', fallback='-1') )}
     
     status, ntotal, nfound = utilities.searchDirectories(
                                                  config.get('traversal', 'directory', fallback='exampleDir'),
                                                  1,
                                                  not config.getboolean('traversal', 'nonrecursive', fallback=False ),
                                                  config.getint('traversal', 'maxlevel', fallback=-1),
                                                  config.get('traversal', 'excluded', fallback=''),                                                  
                                                  config.get('traversal', 'included', fallback=''),
                                                  not config.getboolean('search', 'nodirectories', fallback=False),
                                                  not config.getboolean('search', 'nofiles', fallback=False),
                                                  fCriteria,
                                                  results, 0, 0,
                                                  config.getboolean('traversal', 'debug', fallback=False) )
     
     
     
     absRootPath = config.get('traversal', 'directory', fallback='exampleDir')
     if not os.path.isabs(absRootPath):
        absRootPath = os.getcwd()

     
     
     print('\n\n', 30*'#', '\n # Found:', nfound, 'Checked:', ntotal, '\n', 30*'#', '\n')
     if nfound > 0:

       while True:
           
         try:  
           command = input('Which file to open?(enter number from 1 up until ' + str(nfound) + '. Type q to quit.) >> ')
           if command=='':
              continue
         
            
           if command == 'q':
              break

           try:
             command = int(command)
           except Exception as iEx:
               continue

           if (command <= 0) or (command > len(results)):
               print('Invalid. Number of results ', len(results)) 
               continue

           fpath =  results[command-1]
           if not os.path.isabs(results[command-1]):
              fpath = os.path.join(absRootPath, results[command-1])
            
           print('Opening', os.path.abspath(fpath) )
           utilities.openFile( os.path.abspath(fpath ) )

         except KeyboardInterrupt:
             continue     

     sys.exit(-3)





  ###################################################
  #
  # directory difference functionality
  #
  ###################################################
  if config.get('operation', 'mode', fallback='export') == 'difference':

     print(30*'*')
     print('* Entering DIFFERENCE mode...')
     print(30*'*')
     print(f"Comparing directories [{config.get('difference', 'ldir', fallback='')}] and [{config.get('difference', 'rdir', fallback='')}]\n\n") 
     sts, t, a, b, c = utilities.dirDifference(L_dir=config.get('difference', 'ldir', fallback=''),
                                               R_dir=config.get('difference', 'rdir', fallback=''),
                                               lvl=1,
                                               mxLvl=-1, dirHandler=None, fileHandler=None, dirOnly=False,
                                               matchFilter='', verbose=False, progress=0.01) 
     utilities.tabularDisplay(config.get('difference', 'ldir', fallback=''), a,
                              config.get('difference', 'rdir', fallback=''), b,
                              c)
      




# main guard
if __name__ == '__main__':
   main() 







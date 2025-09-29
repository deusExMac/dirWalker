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


#import os
import sys
#import time

#import datetime
import clrprint

#import json

import configparser
import configargparse
import argparse


import functionality




# Global flag
ON_TRAVERSE_ERROR_QUIT = False











###############################################################################
#
# Main parses command line arguments and sets up the configuration
#
###############################################################################   

def main():

   cmdArgParser = configargparse.ArgParser(default_config_files=['dirWalker.conf', 'dWalker.conf', 'dirW.conf'])
   
   #cmdArgParser = argparse.ArgumentParser(description='Command line arguments', add_help=False)

   # Configuration file
   cmdArgParser.add_argument('-c', '--config', default="dirWalker.conf")
    
   # Directory TRAVERSAL related and CRITERIA
   cmdArgParser.add_argument('-d', '--directory', default="testDirectories/testDir0")
   cmdArgParser.add_argument('-mxt', '--maxTime',  type=float, default=-1)
   cmdArgParser.add_argument('-mxl', '--maxLevels', type=int, default=-1)
   cmdArgParser.add_argument('-fip', '--fileinclusionPattern', default="")
   cmdArgParser.add_argument('-fxp', '--fileexclusionPattern', default="")

   cmdArgParser.add_argument('-dip', '--dirinclusionPattern', default="")
   cmdArgParser.add_argument('-dxp', '--direxclusionPattern', default="")
   cmdArgParser.add_argument('-fsz', '--fileSize', type=float, default=-1) 
   cmdArgParser.add_argument('-mns', '--minFileSize', type=float, default=-1)
   cmdArgParser.add_argument('-mxs', '--maxFileSize', type=float, default=-1)
   cmdArgParser.add_argument('-nd', '--maxDirs', type=int, default=-1)
   cmdArgParser.add_argument('-nf', '--maxFiles', type=int,  default=-1)
   cmdArgParser.add_argument('-cdo', '--creationDateOp',  default='==')
   cmdArgParser.add_argument('-cd', '--creationDate',  default='')
   cmdArgParser.add_argument('-lmdo', '--lastModifiedDateOp',  default='==')
   cmdArgParser.add_argument('-lmd', '--lastModifiedDate',  default='')
   cmdArgParser.add_argument('-NR', '--nonRecursive', action='store_true')
   

   # SEARCH functionality related
   # If set, exclude files. 
   cmdArgParser.add_argument('-NF', '--noFiles', action='store_true')
   # If set, exclude directories
   cmdArgParser.add_argument('-ND', '--noDirs', action='store_true')
   cmdArgParser.add_argument('-I', '--interactive', action='store_true')


   # If set, this will display a gui showing the progress of search as it
   # proceeds.
   cmdArgParser.add_argument('-P', '--progress', action='store_true')
   
   # EXPORT TEMPLATE  related
   cmdArgParser.add_argument('-tp', '--template', default="")
   # How the (replaced) template items (files/directories) should be spararated
   cmdArgParser.add_argument('-tis', '--templateItemsSeparator', default='')
   cmdArgParser.add_argument('-o', '--outputFile', default="index.html")
   # Note: if many css files are specified, enclose the arguments in double quotes "" and
   # separate individual css files with a comma (,) e.g. -s "a.css, folder/b.css, c.css"
   cmdArgParser.add_argument('-s', '--css', default="html/style.css")
   cmdArgParser.add_argument('-i', '--introduction', default="")
   cmdArgParser.add_argument('-tl', '--title', default="")
   cmdArgParser.add_argument('-E', '--urlencode', action='store_true')
   cmdArgParser.add_argument('-RE', '--replaceEmptySubdirs', action='store_true')
   
   # DIRECTORY COMPARISON related
   cmdArgParser.add_argument('-LDIR', '--leftdirectory', default='')
   cmdArgParser.add_argument('-RDIR', '--rightdirectory', default='')
   cmdArgParser.add_argument('-sync', '--synchronize', action='store_true')
   cmdArgParser.add_argument('-fl', '--fromleftonly', action='store_true')
   cmdArgParser.add_argument('-fr', '--fromrightonly', action='store_true')

   
   # Debugging
   # TODO: Not yet used
   cmdArgParser.add_argument('-D', '--debugmode', action='store_true')

   # REMAINDER is always the searchquery. Search query is interpreted as a regular expression.
   # NOTE: if a remainder exists, the mode is set to search.  
   cmdArgParser.add_argument('searchquery', nargs=argparse.REMAINDER, default=[])

   knownArgs, unknownArgs = cmdArgParser.parse_known_args()
   #args = vars(knownArgs)
   config = vars(knownArgs)  
   
   mode = ''
   # If there is a searchquery of interactive mode, we do search
   if config.get('searchquery', []) != []:
      mode = 'search'
   elif config.get('leftdirectory', '') != '' or  config.get('rightdirectory', '') or config.get('synchronize', False):
        mode = 'compare'
   else:
        mode = 'export'
        
      
   
   # Settings done. Now, execute operation based on mode   
   functionality.selector(mode, config, cmdArgParser)
   



# Main guard   
if __name__ == "__main__":
   main() 
























     


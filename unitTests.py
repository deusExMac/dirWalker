
#
#
#
# TODO: Incomplete
#
#
#

import unittest

import pathlib as pl

import GUI
import functionality 




class TestCriteria(unittest.TestCase):

      # TODO: Is it good practice to have many assert in a test?
      def test_search_simpleSearch(self):
          tCriteria = {'directory':'testDirectories/testDir0'}
          # There are exactly 5 files with extension .jpg in this directory
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=functionality.search(query=r'\.jpg$', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Should return 0 DIRECTORIES.')
          self.assertEqual(result[2], 5, 'Should return 5 FILES with extension .jpg (case sensitive)')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)


      # TODO: do we need this?
      def test_search_matchName(self):
          # NOTE: there is one file with an exact size of 176820 bytes
          tCriteria = {'directory':'testDirectories/testDir0'}
          
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=functionality.search(query=r'Cod', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Should return 0 DIRECTORIES.')
          self.assertEqual(result[2], 4, 'Should return 4 FILES with filesize exactly equal to 176821 Bytes')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)

 

      # TODO: Is it good practice to have many assert in a test?
      def test_search_zeroMatchingResults(self):
          tCriteria = {'directory':'testDirectories/testDir0'}
          # There are exactly 5 files with extension .jpg in this directory
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=functionality.search(query=r'manolis', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Should return 0 DIRECTORIES.')
          self.assertEqual(result[2], 0, 'Should return 0 FILES')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)    



      # TODO: Is it good practice to have many assert in a test?
      def test_search_searchDirectoryContainingOnlyEmptySubdirectories(self):
          # This directory contains 10 empty subdirectories 
          tCriteria = {'directory':'testDirectories/testDir1'}
          
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=functionality.search(query=r'.*', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 10, 'Number of total DIRECTORIES should be 10')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)


          

      # TODO: Is it good practice to have many assert in a test?
      def test_search_searchDirectoryContainingOnlyFiles(self):
          tCriteria = {'directory':'testDirectories/testDir2'}
          # This subdirectory does not contain subdirectories; only files.
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=functionality.search(query=r'\.pdf$', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Directory should not contain any SUBDIRECTORY')
          self.assertEqual(result[2], 6, 'Directory should contain ONLY 6 pdf FILES')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)


          
      # TODO: Is it good practice to have many assert in a test?
      def test_search_searchEmptyDirectory(self):
          tCriteria = {'directory':'testDirectories/testDir3'}
          # This directory is empty.
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=functionality.search(query=r'.*', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Directory should not contain any SUBDIRECTORY')
          self.assertEqual(result[2], 0, 'Directory should not contain any FILES')
          self.assertEqual(result[3], 0, 'Number of ignored objects (DIRECTORIES and FILES) should 0')
               

      def test_search_exactFileSize(self):
          # Return ONLY ONE files with file size equal to 176820 Bytes
          # noDirs must be set manually here
          tCriteria = {'directory':'testDirectories/testDir0',
                       'fileSize':176820,
                       'noDirs':True}
          
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=functionality.search(query=r'.*', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Should return 0 DIRECTORIES.')
          self.assertEqual(result[2], 1, 'Should return 1 FILE with filesize exactly equal to 176820 Bytes')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)



      def test_search_almostExactFileSizeByOne(self):
          # Return NO files with file size equal to 176821 bytes
          # NOTE: there is one file with an exact size of 176820 bytes
          tCriteria = {'directory':'testDirectories/testDir0',
                       'fileSize':176821, # off by one byte
                       'noDirs':True}
          
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=functionality.search(query=r'.*', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Should return 0 DIRECTORIES.')
          self.assertEqual(result[2], 0, 'Should return 0 FILES with filesize exactly equal to 176821 Bytes')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)



      def test_search_minimumFileSizeOnlyFiles(self):
          # Return ONLY FILES with minimum file size 1118488 Bytes
          # NOTE: there is one file with size exactly equal to 1118487 Bytes
          tCriteria = {'directory':'testDirectories/testDir0',
                       'minFileSize':1118488,
                       'noDirs':True}
          
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=functionality.search(query=r'.*', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 0, 'Should return 0 DIRECTORIES.')
          self.assertEqual(result[2], 4, 'Should return 4 FILES  with filesize >= 1118488 Bytes')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)


      def test_search_onlyDirectories(self):
          # Return ONLY FILES with minimum file size 1118488 Bytes
          # NOTE: there is one file with size exactly equal to 1118487 Bytes
          tCriteria = {'directory':'testDirectories/testDir0',
                       'noFiles':True}
          
          # NOTE: search returns a tuple with the following values:
          #       (status, <number of matching directories>, <<number of matching files>, <number of ignored objects>)
          result=functionality.search(query=r'2', criteria=tCriteria)
          self.assertEqual(result[0], 0, 'Status should be 0')
          self.assertEqual(result[1], 13, 'Should return 13 DIRECTORIES.')
          self.assertEqual(result[2], 0, 'Should return 0 FILES due to noFiles option')
          # NOTE: number of ignored objects is not compared since they may differ for win and mac machines (due to .DS_Store files)



      #
      # Export tests
      #

      def test_export_checkExportFileExistens(self):
          tCriteria = {'outputFile':'unitTest_checkExportFileExistens.html'}
          
          path = pl.Path(tCriteria['outputFile'])
          result = functionality.export(tCriteria)
          self.assertEqual((path, path.is_file()), (path, True))
   


if __name__ == "__main__":
    unittest.main(verbosity=2)

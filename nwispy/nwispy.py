# -*- coding: utf-8 -*-
"""
:Module: nwispy.py

:Author: Jeremiah Lant
 
:Email: jlant@usgs.gov

:Purpose: 

Read, process, print, and plot information from USGS National
Water Information System (NWIS) data files.

"""

import pdb
import os
import sys
import argparse
import Tkinter, tkFileDialog
from urllib2 import URLError

# my modules
import nwispy_helpers
import nwispy_filereader
import nwispy_viewer
import nwispy_webservice

def process_files(file_list, arguments):
    """    
    Process a list of files according to options contained in arguments.
    
    *Parameters:*
        file_list : list of files to process
        arguments : argparse object; created by parser.parse_args()          
    
    *Return:*
        No return  
        
    """
    for f in file_list:
        filedir, filename = nwispy_helpers.get_filedir_filename(f)
          
        # create output directory     
        outputdirpath = nwispy_helpers.make_directory(path = filedir, directory_name = '-'.join([arguments.outputdir, filename]))      
        
        # read and plot data
        data = nwispy_filereader.read_file(f, error_path = outputdirpath)                              
        nwispy_viewer.plot_data(data, is_visible = arguments.showplot, save_path = outputdirpath)             
                
        # print file information if requested
        if arguments.verbose: 
            nwispy_viewer.print_info(data)  
    
def main():  
    '''
    Run as a script. Prompt user for NWIS file, process the file, print information, 
    and plot data. Information is printed to the screen.  Plots are saved to a directory 
    called 'figs' which is created in the same directory as the data file. A
    log file called 'nwis_error.log' is created if any errors are found in the 
    data file.
    
    '''    
    # parse arguments from command line
    parser = argparse.ArgumentParser(description = 'Read, process, print, and plot information from USGS \
                                                    National Water Information System (NWIS) data files.') 
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--files', nargs = '+', help = 'Input NWIS file(s) to be processed')
    group.add_argument('-fd', '--filedialog', action = 'store_true', help = 'Open a file dialog menu to select datafiles.')
    parser.add_argument('-o', '--outputdir', default = 'output', help = 'Output directory name to hold plots and error log')
    parser.add_argument('-v', '--verbose', action = 'store_true',  help = 'Print general information about NWIS file(s)')
    parser.add_argument('-p', '--showplot', action = 'store_true',  help = 'Show plots of data contained in NWIS file(s)')
    parser.add_argument('-web', '--getwebdata', action = 'store_true',  help = 'Get data from the web')
    args = parser.parse_args()  

    try:
        
        # process file(s) written as arguments
        if args.files:
            process_files(file_list = args.files, arguments = args)
            
        # process file(s) from a Tkinter file dialog
        elif args.filedialog:
            root = Tkinter.Tk() 
            files = tkFileDialog.askopenfilenames(title = 'Select USGS NWIS File(s)', filetypes = [('Text file','*.txt'), ('All files', '.*')])
            root.destroy()          
            process_files(file_list = root.tk.splitlist(files), arguments = args)
            
        # process file(s) using standard input
        else:
            data = nwispy_filereader.read_file_in(sys.stdin) 
            outputdirpath = nwispy_helpers.make_directory(path = os.getcwd(), directory_name = args.outputdir)
            nwispy_viewer.plot_data(data, is_visible = args.showplot, save_path = outputdirpath) 
                    
            if args.verbose: 
                nwispy_viewer.print_info(data)
            
    except IOError as error:
        sys.exit('IO error: {0}'.format(error.message))
        
    except ValueError as error:
        sys.exit('Value error. {0}'.format(error.message))

    except IndexError as error:
        sys.exit('Index error: {0}'.format(error.message))

    except URLError as error:
        sys.exit('Url error: {0}'.format(error.message))
        
if __name__ == "__main__":
    # read file, print results, and plot 
    main()
    

  

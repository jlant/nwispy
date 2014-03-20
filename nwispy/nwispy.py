# -*- coding: utf-8 -*-
"""
:Module: nwispy.py

:Author: Jeremiah Lant
 
:Email: jlant@usgs.gov

:Purpose: 

Main controller that controls user input options and calls the appropriate modules.

"""

import pdb
import os
import sys
import argparse
import Tkinter, tkFileDialog
from urllib2 import URLError, HTTPError
import logging

# my modules
import nwispy_helpers
import nwispy_filereader
import nwispy_viewer
import nwispy_webservice
import nwispy_logging

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
        outputdirpath = nwispy_helpers.make_directory(path = filedir, directory_name = '-'.join([filename.split(".txt")[0], "output"]))      
        
        # initialize error logging
        nwispy_logging.initialize_loggers(output_dir = outputdirpath)        
        
        # read data
        data = nwispy_filereader.read_file(f)  

        # plot data                            
        nwispy_viewer.plot_data(data, is_visible = arguments.showplot, save_path = outputdirpath)             
                
        # print data
        if arguments.verbose: 
            nwispy_viewer.print_info(data)  

        # close error logging
        nwispy_logging.remove_loggers()
    
def main():  
    """
    Run program based on user input arguments. Program will automatically process file(s) supplied or downloaded,
    log any errors found in the data file, and will save plots of every parameter. Error log and plots are saved to 
    a directory (tagged with 'output') at the same level as the supplied or downloaded data files.
    """    
    # parse arguments from command line
    parser = argparse.ArgumentParser(description = 'Read, process, log errors, print, and plot information from USGS \
                                                    National Water Information System (NWIS) data files.') 
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--files', nargs = '+', help = 'Input NWIS file(s) to be processed')
    group.add_argument('-fd', '--filedialog', action = 'store_true', help = 'Open a file dialog menu to select datafiles.')
    parser.add_argument('-v', '--verbose', action = 'store_true',  help = 'Print general information about NWIS file(s)')
    parser.add_argument('-p', '--showplot', action = 'store_true',  help = 'Show plots of data contained in NWIS file(s)')
    parser.add_argument('-web', '--webservice', nargs = '+',  help = 'Get data file(s) from the web using a web service request file')
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
            
        # process file(s) from a webservice
        elif args.webservice:
            # get user supplied web request file and its location
            request_file = args.webservice[0]
            request_filedir, request_filename = nwispy_helpers.get_filedir_filename(path = request_file)            
            
            # make a directory to hold download files in the same directory as the request file
            web_filedir = nwispy_helpers.make_directory(path = request_filedir, directory_name = "-".join([request_filename.split(".txt")[0], "datafiles"]))
            
            # initialize error logging
            nwispy_logging.initialize_loggers(output_dir = web_filedir, logging_type = "exception")                        
            
            # read the request data file
            request_data = nwispy_webservice.read_webrequest(filepath = request_file)                         
                      
            for request in request_data["requests"]:    
                # encode a url based on request
                request_url = nwispy_webservice.encode_url(request) 
                
                # name each file by date tagging it to current date and time and its site number
                date_time_str = nwispy_helpers.now()
                web_filename = "_".join([request["site number"], request["data type"], date_time_str]) + ".txt"
                
                # download the files
                nwispy_webservice.download_file(user_parameters_url = request_url, 
                                                data_type = request["data type"], 
                                                filename = web_filename,
                                                file_destination = web_filedir)

            # close error logging
            nwispy_logging.remove_loggers()

            # process the downloaded file
            file_list = nwispy_helpers.get_filepaths(directory = web_filedir, file_ext = ".txt")

            process_files(file_list = file_list, arguments = args)            
            
        # process file(s) using standard input
        else:
            data = nwispy_filereader.read_file_in(sys.stdin) 
            outputdirpath = nwispy_helpers.make_directory(path = os.getcwd(), directory_name = args.outputdir)
            nwispy_viewer.plot_data(data, is_visible = args.showplot, save_path = outputdirpath) 
                    
            if args.verbose: 
                nwispy_viewer.print_info(data)
            
    except IOError as error:
        logging.exception("IO error: {0}".format(error.message))
        sys.exit(1)
        
    except ValueError as error:
        logging.exception("Value error: {0}".format(error.message))
        sys.exit(1)

    except IndexError as error:
        logging.exception("Index: {0}".format(error.message))
        sys.exit(1)

    except URLError as error:
        logging.exception("URLError error: {0}".format(error.code))
        sys.exit(1)

    except HTTPError as error:
        logging.exception("HTTP error: {0}".format(error.code))
        sys.exit(1)
        
if __name__ == "__main__":
    main()
    

  

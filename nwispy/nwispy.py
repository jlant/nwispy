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
import re
import numpy as np
import datetime
import Tkinter, tkFileDialog
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
from scipy.stats import nanmean 

# my modules
import helpers

def get_parameter_code(match):
    """   
    Get code and description from existing parameters.
    
    *Parameters*:
        match: regular expression match object
        
    *Return*:
        (code, description): tuple of code and description
    
    *Example*:
        string:  '#    06   00060     00003     Discharge, cubic feet per second (Mean)'
        
        match.groups(0):  ('#', '06', '00060', '00003', '     Discharge, cubic feet per second (Mean)')
        
        match.group(1) = '#'
        
        match.group(2) = '06'
        
        match.group(3) = '00060'
        
        match.group(4) = '00003'
        
        match.group(5) = 'Discharge, cubic feet per second (Mean)'
        
    """ 
    
    # get the proper information from each group
    dd = match.group(2)
    param = match.group(3)
    
    # concatenate dd and param using '_' as in the column names
    code = '_'.join((dd, param))            
    
    # get parameter description
    description = match.group(5).strip()    
    
    # if statistic exists, then add that to the string
    if match.group(4):
        statistic =  match.group(4).strip()
        code = '_'.join((code, statistic)) 
   
    return (code, description)


def get_date(daily, instantaneous):
    """   
    Parse the date strings from a data row.
    
    *Parameters*:
        daily: string of daily format; i.e. 2013-06-25
        
        intantaneous: string of intantaneous format; i.e. 00:15\tEDT
    
    *Return*:
        date: datetime object   
        
    """
    
    # get date from the data row
    year = daily.split('-')[0]
    month = daily.split('-')[1]
    day = daily.split('-')[2]
    hour = 0
    minute = 0
    
    # if data row has a date in instantaneous format, then get hour and minute after removing the 'EDT'
    if instantaneous:
        instantaneous = instantaneous.split('\t')[0]
        hour = instantaneous.split(':')[0]
        minute = instantaneous.split(':')[1]
                
    date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    
    return date

def print_info(nwis_data):
    """   
    Print relevant information and contained in the nwis data file. 
    
    *Parameters*:
        nwis_data: dictionary holding data from NWIS file
        
    *Return*:
        no return
        
    """   
    
    # print relevant information
    print('*** DATA FILE INFORMATION ***')
    print('Date retrieved: {0}'.format(nwis_data['date_retrieved']))
    print('Gage name: {0}'.format(nwis_data['gage_name']))
    print('Timestep: {0}'.format(nwis_data['timestep']))
    
    print('Parameters:')
    for parameter in nwis_data['parameters']:
        print('  {0}'.format(parameter['description']))

def plot_data(nwis_data, is_visible = True, save_path = None):
    """   
    Plot each parameter contained in the nwis data. Save plots to a particular
    path.
    
    *Parameters*:
        nwis_data: dictionary holding data from NWIS file
        
        save_path: string path to save plot(s) 
        
    *Return*:
        no return
        
    """
    
    for parameter in nwis_data['parameters']:
        
        fig = plt.figure(figsize=(12,10))
        ax = fig.add_subplot(111)
        ax.grid(True)
        ax.set_title(nwis_data['gage_name'] + ' (' + nwis_data['timestep'] + ')')
        ax.set_xlabel('Date')
        ax.set_ylabel(parameter['description'])
        plt.plot(nwis_data['dates'], parameter['data'], color = 'b', marker = 'o', label = parameter['description'])
    
        # rotate and align the tick labels so they look better
        fig.autofmt_xdate()
        
        # use a more precise date string for the x axis locations in the
        # toolbar
        ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
     
        # legend; make it transparent    
        handles, labels = ax.get_legend_handles_labels()
        legend = ax.legend(handles, labels, fancybox = True)
        legend.get_frame().set_alpha(0.5)
        legend.draggable(state=True)
        
        # show text of mean, max, min values on graph; use matplotlib.patch.Patch properies and bbox
        text = 'mean = %.2f\nmax = %.2f\nmin = %.2f' % (parameter['mean'], parameter['max'], parameter['min'])
        patch_properties = {'boxstyle': 'round',
                            'facecolor': 'wheat',
                            'alpha': 0.5
                            }
                       
        ax.text(0.05, 0.95, text, transform = ax.transAxes, fontsize = 14, 
                verticalalignment = 'top', horizontalalignment = 'left', bbox = patch_properties)
        
        # save plots
        if save_path:        
            # set the size of the figure to be saved
            curr_fig = plt.gcf()
            curr_fig.set_size_inches(12, 10)
            plt.savefig(save_path + '/' + nwis_data['gage_name'] + ' - ' + parameter['description']  + '.png', dpi = 100)
            
        # show plots
        if is_visible:
            plt.show()
        else:
            plt.close()
 
        
def read_file(filepath):
    """    
    Open NWIS file, create a file object for read_file_in(filestream) to process.
    This function is responsible to opening the file, removing the file opening  
    responsibility from read_file_in(filestream) so that read_file_in(filestream)  
    can be unit tested.
    
    *Parameters:*
		filepath : string path to NWIS file
    
    *Return:*
        data : dictionary holding data found in NWIS data file  
        
    """
    
    with open(filepath, 'r') as f:
        data = read_file_in(f)
    
    return data

def read_file_in(filestream):
    """    
    Read and process a USGS NWIS file. Finds any parameter and its respective data. 
    Relevant data is put into a dictionary (see Return section).  Missing data values
    are replaced with a NAN value.  
    
    *Parameters:*
        filestream: file object
    
    *Return:*
        data: dictionary holding data found in NWIS data file
        
        data = {
            'date_retrieved': None,
            
            'gage_name': None,
            
            'column_names': None,
            
            'parameters': [],
            
            'dates': [],
            
            'timestep': None   
        }      
                
        ** Note: The 'parameters' key contains a list of dictionaries containing
        the parameters found in the data file; i.e.
        
        parameters[0] = {
            'code': string of NWIS code,
            
            'description': string of NWIS description,
            
            'index': integer of column index data is located,
            
            'data': numpy array of data values,
            
            'mean': mean of data values,
            
            'max': max of data values,
            
            'min': min of data values
        }        
        
    """  

    data_file = filestream.readlines()
    
    # regular expression patterns in data file 
    # column_names and data_row patterns have 5 groups which is used to 
    # distinguish a daily file from an instanteous file; if 4th group is None, 
    # then data file is daily, otherwise it is an instanteous file.
    patterns = {
        'date_retrieved': '(.+): (.{4}-.{2}-.{2}) (.{2}:.{2}:.{2}) (.+)', 
        'gage_name': '(#.+)(USGS.+)',
        'parameters': '(#)\D+([0-9]{2})\D+([0-9]{5})(\D+[0-9]{5})?(.+)',
        'column_names': '(agency_cd)\t(site_no)\t(datetime)\t(tz_cd)?(.+)',
        'data_row': '(USGS)\t([0-9]{8})\t([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})\s?([0-9]{2}:[0-9]{2}\t[A-Z]{3})?(.+)'
    }    
    
    # initialize a dictionary to hold all the data of interest
    data = {
        'date_retrieved': None,
        'gage_name': None,
        'column_names': None,
        'parameters': [],
        'dates': [],
        'timestep': None
    }      
    
    # process file; find matches and add to data dictionary
    for line in data_file: 
        match_date_retrieved = re.search(pattern = patterns['date_retrieved'], string = line)
        match_gage_name = re.search(pattern = patterns['gage_name'], string = line)
        match_parameters = re.search(pattern = patterns['parameters'], string = line)
        match_column_names = re.search(pattern = patterns['column_names'], string = line)
        match_data_row = re.search(pattern = patterns['data_row'], string = line)
     
        # if match is found add it to data dictionary; date is in second group of the match
        if match_date_retrieved:
            data['date_retrieved'] = match_date_retrieved.group(2)
        
        # get the gage name which is the second group in the pattern
        if match_gage_name:
            data['gage_name'] = match_gage_name.group(2)
        
        # get the parameters available in the file and create a dictionary for each parameter
        if match_parameters:
            code, description = get_parameter_code(match = match_parameters)       
            
            data['parameters'].append({ 
                'code': code, 
                'description': description,
                'index': None,
                'data': [],
                'mean': None,
                'max': None,
                'min': None
            })
            
        # get the column names and indices of existing parameter(s) 
        if match_column_names:
            data['column_names'] = match_column_names.group(0).split('\t')
            
            for parameter in data['parameters']:
                parameter['index'] = data['column_names'].index(parameter['code'])           

         # get date; match_data_row.group(3) => daily match, match_data_row.group(4) => instantaneous match
        if match_data_row:
            date = get_date(daily = match_data_row.group(3), instantaneous = match_data_row.group(4))
            data['dates'].append(date)
            
            for parameter in data['parameters']:
                value = match_data_row.group(0).split('\t')[parameter['index']]
                
                if not helpers.is_float(value):
                    if value == "":
                        error_str = '**Missing value on ' + str(date) + ' *Filling with Not A Number (NAN)'
                        print(error_str)
                        logger.info(error_str)
                        value = np.nan
                    
                    elif '_' in value:
                        error_str = '**Bad value with float on ' + str(date) + ' *Splitting on _ character'
                        print(error_str)
                        logger.info(error_str)
                        value = value.split('_')[0]
                    
                    else:
                        error_str = '**ERROR on ' + str(date) +' Value can not be converted to a float: ' + value + '**Exiting. Bad data in file!'
                        raise ValueError(error_str)
                        sys.exit('**Exiting. Bad data in file!')
                        
                parameter['data'].append(float(value))    
    
    # convert the date list to a numpy array
    data['dates'] = np.array(data['dates'])    
    
    # find timestep of the data
    timestep = data['dates'][1] - data['dates'][0]
    if timestep.days == 1:
        data['timestep'] = 'daily'
    else:
        data['timestep'] = 'instantaneous'
    
    # convert each parameter data list in data['parameter'] convert to a numpy array and
    # compute mean, max, and min as well.
    
    for parameter in data['parameters']:
<<<<<<< HEAD
        parameter['data'] = np.array(parameter['data'])       
        parameter['mean'] = nanmean(parameter['data'])
        parameter['max'] = np.nanmax(parameter['data'])
        parameter['min'] = np.nanmin(parameter['data'])
        
=======
        parameter['data'] = np.array(parameter['data'])
        parameter['mean'] = np.mean(parameter['data'])
        parameter['max'] = np.max(parameter['data'])
        parameter['min'] = np.min(parameter['data'])
    
>>>>>>> have a working unix friendly program; still working on logging errors properly
    return data 

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
              
        
        filedir, filename = os.path.split(f)
        
        # filedir is an empty string when file f is in current directory 
        if not filedir: 
            filedir = os.getcwd()
            
        # create output directory     
        outputdirpath = helpers.make_directory(path = filedir, directory_name = '-'.join([arguments.outputdir, filename]))      
          
#        logger = logging.getLogger(__name__)
#        logger.setLevel(logging.INFO)
#        handler = logging.FileHandler('/'.join([outputdirpath, 'error.log']))
#        handler.setLevel(logging.INFO)
#        logger.addHandler(handler)
        
        logging.basicConfig(filename = '/'.join([outputdirpath, 'error.log']), filemode = 'w', level = logging.INFO)  
        
        # read and plot data
        data = read_file(f)                              
        plot_data(data, is_visible = arguments.showplot, save_path = outputdirpath)             
                
        # print file information if requested
        if arguments.verbose: 
            print_info(data)
    
    # shutdown the error logger
    logging.shutdown()    
    
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
    parser.add_argument('-o', '--outputdir', default = 'output', help = 'Output directory name to hold plots (and error log if errors are found)')
    parser.add_argument('-v', '--verbose', action = 'store_true',  help = 'Print general information about NWIS file(s)')
    parser.add_argument('-p', '--showplot', action = 'store_true',  help = 'Show plots of data contained in NWIS file(s)')
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
            data = read_file_in(sys.stdin) 
            outputdirpath = helpers.make_directory(path = os.getcwd(), directory_name = args.outputdir)
            plot_data(data, is_visible = args.showplot, save_path = outputdirpath) 
                    
            if args.verbose: 
                print_info(data)
            
    except IOError as error:
        sys.exit('Cannot open file: {0}'.format(error.filename))
        
    except ValueError as error:
        sys.exit('Value error. {0}'.format(error.message))


if __name__ == "__main__":
    
    # read file, print results, and plot 
    main()
  
    
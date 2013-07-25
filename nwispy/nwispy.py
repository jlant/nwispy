# -*- coding: utf-8 -*-
"""
:Module: nwispy.py

:Author: Jeremiah Lant
 
:Email: jlant@usgs.gov

:Purpose: Read, process, print, and plot information from NWIS data files.

"""

import os
import sys
import re
import numpy as np
import datetime
import Tkinter, tkFileDialog
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging

def read_nwis(filename):
    """    
    Open NWIS file, create a file object for read_nwis_in(filestream) to process.
    This function is responsible to opening the file, removing the file opening  
    responsibility from read_nwis_in(filestream) so that read_nwis_in(filestream)  
    can be unit tested.
    
    *Parameters:*
		filename : string path to nwis file
    
    *Return:*
        data : dictionary holding data found in NWIS data file  
        
    """
    
    filestream = open(filename, 'r')
    data = read_nwis_in(filestream)
    filestream.close()
    
    return data

def read_nwis_in(filestream):
    """    
    Read and process a USGS NWIS file. Finds any parameter and its respective data. 
    Relevant data is put into a dictionary (see Return section).  Missing data values
    are replaced with a NAN value.  If data values are not floats, then an 
    attempt is made to split by the '_' character and accept only the float.
    
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
    
    # read all the lines in the filestream
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
    
    # process file
    for line in data_file: 
        # find match
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
                
                if not is_float(value):
                    if value == "":
                        error_str = '**Missing value on ' + str(date) + ' *Filling with Not A Number (NAN)'
                        print error_str
                        logging.info(error_str)
                        value = np.nan
                    
                    elif '_' in value:
                        error_str = '**Bad value with float on ' + str(date) + ' *Splitting on _ character'
                        print error_str
                        logging.info(error_str)
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
        parameter['data'] = np.array(parameter['data'])
        parameter['mean'] = np.mean(parameter['data'])
        parameter['max'] = np.max(parameter['data'])
        parameter['min'] = np.min(parameter['data'])
        
    return data 

    
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

def is_float(value):
    """   
    Determine if string value can be converted to a float. Return True if
    value can be converted to a float and False otherwise.
    
    *Parameters*:
        value: string
        
    *Return*:
        boolean
        
    """
    
    try:
        float(value)
        return True
        
    except ValueError:
        return False


def print_nwis(nwis_data):
    """   
    Print relevant information and contained in the nwis data 
    
    *Parameters*:
        nwis_data: dictionary holding data from NWIS file
        
    *Return*:
        no return
        
    """   
    
    # print relevant information
    print 'Date retrieved: ', nwis_data['date_retrieved']
    print 'Gage name: ', nwis_data['gage_name']
    print 'Timestep: ', nwis_data['timestep']
    
    print 'The following are the parameters avaiable in the file:'
    for parameter in nwis_data['parameters']:
        print parameter['description']

def plot_nwis(nwis_data, is_visible = True, save_path = None):
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
            plt.savefig(save_path + '/' + parameter['description'] + '.png', dpi = 100)
            
        # show plots
        if is_visible:
            plt.show()
        else:
            plt.close()
    
    
def main():  
    """
    Run as a script. Prompt user for NWIS file, process the file, print information, 
    and plot data. Information is printed to the screen.  Plots are saved to a directory 
    called 'figs' which is created in the same directory as the data file. A
    log file called 'nwis_error.log' is created if any errors are found in the 
    data file.
    
    """ 
    
    # open a file dialog to get file     
    root = Tkinter.Tk() 
    file_format = [('Text file','*.txt')]  
    nwis_file = tkFileDialog.askopenfilename(title = 'Select USGS NWIS File', filetypes = file_format)
    root.destroy()
    
    if nwis_file:
        
        try:
            # get directory and filename from data file
            dirname, filename = os.path.split(os.path.abspath(nwis_file))
            
            # make a directory called figs to hold the plots            
            figs_path = dirname + '/figs'
            if not os.path.exists(figs_path):
                os.makedirs(figs_path)            
            
            # log any errors or warnings found in file; save to data file directory
            logging.basicConfig(filename = dirname + '/nwis_error.log', filemode = 'w', level=logging.DEBUG)
            
            # process file
            print ''
            print '** Processing **'
            print nwis_file
            nwis_data = read_nwis(nwis_file)
            
            
            # print nwis information
            print ''
            print '** USGS NWIS File Information **'
            print_nwis(nwis_data = nwis_data)
            
            # plot nwis parameters
            print ''
            print '** Plotting **'
            print 'Plots are being saved to same directory as NWIS data file.'
            plot_nwis(nwis_data, is_visible = True, save_path = figs_path)

            # shutdown the logging system
            logging.shutdown()

        except IOError as error:
            print 'Cannot read file!' + error.filename
            print error.message
            
        except IndexError as error:
            print 'Cannot read file! Bad file!'
            print error.message
            
        except ValueError as error:
            print error.message
            
    else:
        print '** Canceled **'
    

if __name__ == "__main__":
    
    # read file, print results, and plot 
    main()

    
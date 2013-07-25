# -*- coding: utf-8 -*-
"""
:Module: nwispygui.py

:Author: Jeremiah Lant
 
:Email: jlant@usgs.gov

:Purpose: 
Script that creates an interactive plot of an NWIS data file. User can 
interact with the plot via a SpanSelector mouse widget. A toggle key event handler 
exists for the matplotlib SpanSelector widget. A keypress of 'A' or 'a' actives the 
slider and a keypress of 'Q' or 'q' de-activates the slider.
         
"""

#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import Tkinter, tkFileDialog
import matplotlib.dates as mdates
import datetime

# my module
import nwispy

def onselect(xmin, xmax):
    """ 
    A select event handler for the matplotlib SpanSelector widget.
    Selects a min/max range of the x or y axes for a matplotlib Axes.
    """ 
    # convert matplotlib float dates to a datetime format
    date_min = mdates.num2date(xmin)
    date_max = mdates.num2date(xmax) 
    
    # put the xmin and xmax in datetime format to compare
    date_min = datetime.datetime(date_min.year, date_min.month, date_min.day, date_min.hour, date_min.minute)    
    date_max = datetime.datetime(date_max.year, date_max.month, date_max.day, date_max.hour, date_max.minute)
    
    # find the indices that were selected    
    indices = np.where((dates >= date_min) & (dates <= date_max))
    indices = indices[0]
    
    # set the data in second plot
    plot2.set_data(dates[indices], parameter['data'][indices])
    
    # calculate new mean, max, min
    param_mean = np.mean(parameter['data'][indices])    
    param_max = np.max(parameter['data'][indices])  
    param_min = np.min(parameter['data'][indices])  
    
    ax2.set_xlim(dates[indices][0], dates[indices][-1])
    ax2.set_ylim(param_min, param_max)
        
    # show text of mean, max, min values on graph; use matplotlib.patch.Patch properies and bbox
    text3 = 'mean = %.2f\nmax = %.2f\nmin = %.2f' % (param_mean, param_max, param_min)
                   
    ax2_text.set_text(text3)
    
    fig.canvas.draw()

def toggle_selector(event):
    """ 
    A toggle key event handler for the matplotlib SpanSelector widget. Keypress
    of 'A' or 'a' actives the slider; 'Q' or 'q' de-activates the slider
    """ 
    if event.key in ['Q', 'q'] and span.visible:
        print '**SpanSelector deactivated.**'
        span.visible = False
    if event.key in ['A', 'a'] and not span.visible:
        print '**SpanSelector activated.**'
        span.visible = True
    

 # create root window     
root = Tkinter.Tk() 
file_format = [('Text file','*.txt')]  
nwis_file = tkFileDialog.askopenfilename(title = 'Select USGS NWIS File', filetypes = file_format)
root.destroy()

if nwis_file:
    
    try:
        # process file    
        nwis_data = nwispy.read_nwis(nwis_file)
        
        # print relevant information
        print '** USGS NWIS File Information **'
        nwispy.print_nwis(nwis_data = nwis_data)
    
        dates = nwis_data['dates']
        parameter = nwis_data['parameters'][0]
        
         # plot parameter
        fig = plt.figure(figsize=(12,10))

        ax1 = fig.add_subplot(211)
        ax1.grid(True)
        ax1.set_title(nwis_data['gage_name'] + ' (' + nwis_data['timestep'] +')')
        ax1.set_xlabel('Date')
        ax1.set_ylabel(parameter['description'])

        plot1, = ax1.plot(dates, parameter['data'], color = 'b', marker = 'o', label = parameter['description'])
        
        # rotate and align the tick labels so they look better      
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation = 30)
        
        # use a more precise date string for the x axis locations in the
        # toolbar
        ax1.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
         
        # legend; make it transparent    
        handles, labels = ax1.get_legend_handles_labels()
        legend = ax1.legend(handles, labels, fancybox = True)
        legend.get_frame().set_alpha(0.5)
        legend.draggable(state=True)
        
        # show text of mean, max, min values on graph; use matplotlib.patch.Patch properies and bbox
        text1 = 'mean = %.2f\nmax = %.2f\nmin = %.2f' % (parameter['mean'], parameter['max'], parameter['min'])
        patch_properties = {'boxstyle': 'round',
                            'facecolor': 'wheat',
                            'alpha': 0.5
                            }
                       
        ax1.text(0.05, 0.95, text1, transform = ax1.transAxes, fontsize = 14, 
                verticalalignment = 'top', horizontalalignment = 'left', bbox = patch_properties)
        
        # add another plot
        ax2 = fig.add_subplot(212)
        ax2.grid(True)
        ax2.set_title('USGS NWIS: ' + nwis_data['gage_name'])
        ax2.set_xlabel('Date')
        ax2.set_ylabel(parameter['description'])
        plot2, = ax2.plot(dates, parameter['data'], color = 'b',  marker = 'o', label = parameter['description'])
        
        # rotate and align the tick labels so they look better  
        plt.xticks(rotation = 30)
        
        ax2.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
        
        # legend; make it transparent    
        handles2, labels2 = ax2.get_legend_handles_labels()
        legend2 = ax2.legend(handles2, labels2, fancybox = True)
        legend2.get_frame().set_alpha(0.5)
        legend2.draggable(state=True)
        
        # show text of mean, max, min values on graph; use matplotlib.patch.Patch properies and bbox
        text2 = 'mean = %.2f\nmax = %.2f\nmin = %.2f' % (parameter['mean'], parameter['max'], parameter['min'])
        patch_properties = {'boxstyle': 'round',
                            'facecolor': 'wheat',
                            'alpha': 0.5
                            }
                       
        ax2_text = ax2.text(0.05, 0.95, text2, transform = ax2.transAxes, fontsize = 14, 
                             verticalalignment = 'top', horizontalalignment = 'left', bbox = patch_properties)
                
        # make a splan selector and have it turned off initially until user 
        # presses 'q' or 'a' on the key board via toggle_selector
        span = SpanSelector(ax1, onselect, 'horizontal', useblit=True,
                            rectprops=dict(alpha=0.5, facecolor='red'))
        span.visible = False
                
        # connect span with the toggle selector in order to toggle span selector on and off
        span.connect_event('key_press_event', toggle_selector)        
        
        # make sure that the layout of the subplots do not overlap
        plt.tight_layout()
        plt.show()
                
    except IOError as error:
        print 'cannot read file' + error.filename
        print error.message
        
    except IndexError as error:
        print 'Cannot read file! Bad file!'
        print error.message
            
    except ValueError as error:
        print error.message
        
else:
    print '** Canceled **'


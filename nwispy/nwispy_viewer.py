"""
:Module: nwis_plotter.py

:Author: Jeremiah Lant
 
:Email: jlant@usgs.gov

:Purpose: 

Plot and print information about nwis data files.

"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from textwrap import wrap

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
        ylabel = '\n'.join(wrap(parameter['description'], 60))
        ax.set_ylabel(ylabel)
        plt.plot(nwis_data['dates'], parameter['data'], color = 'b', marker = 'o', markersize = 6, label = ylabel)
    
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
            if parameter['description'].split(',')[0] == "Turbidity":
                short_description = parameter['description'].split(',')[0] 
                plt.savefig(save_path + '/' + nwis_data['gage_name'] + ' - ' + short_description  + '.png', dpi = 100)
            else:
                plt.savefig(save_path + '/' + nwis_data['gage_name'] + ' - ' + parameter['description']  + '.png', dpi = 100)
            
        # show plots
        if is_visible:
            plt.show()
        else:
            plt.close()


def main():
    """ Test functionality of plotting and printing file information """


if __name__ == "__main__":
    main() 
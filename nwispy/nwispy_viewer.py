# -*- coding: utf-8 -*-
"""
:Module: nwis_viewer.py

:Author: Jeremiah Lant, jlant@usgs.gov, U.S. Geological Survey, Kentucky Water Science Center, http://www.usgs.gov/ 

:Synopsis: Handles views of the data, such as printing and plotting.
"""

__author__   = "Jeremiah Lant, jlant@usgs.gov, U.S. Geological Survey, Kentucky Water Science Center."
__copyright__ = "http://www.usgs.gov/visual-id/credit_usgs.html#copyright"
__license__   = __copyright__
__contact__   = __author__

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from textwrap import wrap

import datetime
import numpy as np
import os

def print_info(nwis_data):
    """   
    Print information contained in the data dictionary. 
    
    Parameters
    ----------
    nwis_data : dictionary 
        A dictionary containing data found in data file.
    
    Examples
    --------
    >>> import nwispy_viewer
    >>> import datetime
    >>> import numpy as np
    >>> start_date = datetime.datetime(2014, 03, 01, 8, 0)
    >>> dates = [start_date + datetime.timedelta(i) for i in range(10)]
    >>> temperature_data = np.array([0 + i for i in range(10)])
    >>> stage_data = np.array([100 + i for i in range(10)])      
    >>> parameters = [{"code": "00010", "description": "Temperature, water, degrees Celsius", "index": 0, 
                   ... "data": temperature_data, "mean": np.mean(temperature_data), "max": np.max(temperature_data), 
                   ... "min": np.min(temperature_data)}, 
                      {"code": "00065", "description": "Gage height, feet", "index": 1, "data": stage_data, 
                   ... "mean": np.mean(stage_data),"max": np.max(stage_data), "min": np.min(stage_data)}]
    >>> data = {"date_retrieved": "2014-03-20 22:28:47","gage_name": "USGS 03401385 DAVIS BRANCH AT HIGHWAY 988 NEAR MIDDLESBORO, KY", 
            ... "column_names": ["03_00010", "03_00010_cd", "02_00065", "02_00065_cd"], "parameters": parameters, 
            ... "dates": dates, "timestep": "instaneous"}
    >>> nwispy_viewer.print_info(nwis_data = data)
    --- DATA FILE INFORMATION ---
    Date retrieved: 2014-03-20 22:28:47
    Gage name: USGS 03401385 DAVIS BRANCH AT HIGHWAY 988 NEAR MIDDLESBORO, KY
    Timestep: instaneous
    Parameters:
      Temperature, water, degrees Celsius
      Gage height, feet
    """   
    
    # print relevant information
    print("--- DATA FILE INFORMATION ---")
    print("Date retrieved: {0}".format(nwis_data["date_retrieved"]))
    print("Gage name: {0}".format(nwis_data["gage_name"]))
    print("Timestep: {0}".format(nwis_data["timestep"]))
    
    print("Parameters:")
    for parameter in nwis_data["parameters"]:
        print("  {0}".format(parameter["description"]))
        print("      mean: {}".format(parameter["mean"]))
        print("      max: {}".format(parameter["max"]))
        print("      min: {}".format(parameter["min"]))

def plot_data(nwis_data, is_visible = True, save_path = None):
    """   
    Plot each parameter contained in the nwis data. Save plots to a particular
    path.
    
    Parameters
    ----------
    nwis_data : dictionary 
        A dictionary containing data found in data file.

    is_visible : bool
        Boolean value to show plots 
        
    save_path : string 
        String path to save plot(s) 
    """
    
    for parameter in nwis_data["parameters"]:
        
        fig = plt.figure(figsize=(12,10))
        ax = fig.add_subplot(111)
        ax.grid(True)
        ax.set_title(nwis_data["gage_name"] + " (" + nwis_data["timestep"] + ")")
        ax.set_xlabel("Date")
        ylabel = "\n".join(wrap(parameter["description"], 60))
        ax.set_ylabel(ylabel)

        if "Discharge" in parameter["description"]:
            color_str = "b"
        elif "Gage height" in parameter["description"]:
            color_str = "g"
        elif "Precipitation" in parameter["description"]:
            color_str = "DarkBlue"
        elif "Temperature" in parameter["description"]:
            color_str = "orange"
        else:
            color_str = "k"

        plt.plot(nwis_data["dates"], parameter["data"], color = color_str, label = ylabel) 
        plt.fill_between(nwis_data["dates"], parameter["min"], parameter["data"], facecolor = color_str, alpha = 0.5)
            
        # rotate and align the tick labels so they look better
        fig.autofmt_xdate()
        
        # use a more precise date string for the x axis locations in the
        # toolbar
        ax.fmt_xdata = mdates.DateFormatter("%Y-%m-%d")
     
        # legend; make it transparent    
        handles, labels = ax.get_legend_handles_labels()
        legend = ax.legend(handles, labels, fancybox = True)
        legend.get_frame().set_alpha(0.5)
        legend.draggable(state=True)
        
        # show text of mean, max, min values on graph; use matplotlib.patch.Patch properies and bbox
        text = "mean = %.2f\nmax = %.2f\nmin = %.2f" % (parameter["mean"], parameter["max"], parameter["min"])
        patch_properties = {"boxstyle": "round",
                            "facecolor": "wheat",
                            "alpha": 0.5
                            }
                       
        ax.text(0.05, 0.95, text, transform = ax.transAxes, fontsize = 14, 
                verticalalignment = "top", horizontalalignment = "left", bbox = patch_properties)
        
        # save plots
        if save_path:        
            # set the size of the figure to be saved
            curr_fig = plt.gcf()
            curr_fig.set_size_inches(12, 10)
            
            # keep filename string short enough to be saved properly; keep only usgs gage number, description shortened if it exceeds 50 characters 
            short_gage_name = " ".join(nwis_data["gage_name"].split()[0:2])            
            if len(parameter["description"]) > 50:
                short_description = parameter["description"].split(",")[0] 
                filename = " - ".join([short_gage_name, short_description])  + ".png"           
                filepath = os.path.join(save_path, filename)
                plt.savefig(filepath, dpi = 100)
            else:
                filename = " - ".join([short_gage_name, parameter["description"]])  + ".png"           
                filepath = os.path.join(save_path, filename)
                plt.savefig(filepath, dpi = 100)
            
        # show plots
        if is_visible:
            plt.show()
        else:
            plt.close()


def _create_testdata():
    """ Create test data for tests """
    
    start_date = datetime.datetime(2014, 03, 01, 8, 0)
    dates = [start_date + datetime.timedelta(i) for i in range(10)]
    
    temperature_data = np.array([0 + i for i in range(10)])
    stage_data = np.array([100 + i for i in range(10)])
       
    parameters = [
        {"code": "00010",
        "description": "Temperature, water, degrees Celsius",
        "index": 0,
        "data": temperature_data,
        "mean": np.mean(temperature_data),
        "max": np.max(temperature_data),
        "min": np.min(temperature_data)},

        {"code": "00065",
        "description": "Gage height, feet",
        "index": 1,
        "data": stage_data,
        "mean": np.mean(stage_data),
        "max": np.max(stage_data),
        "min": np.min(stage_data)}        
    ]
    
    data = {
        "date_retrieved": "2014-03-20 22:28:47",
        "gage_name": "USGS 03401385 DAVIS BRANCH AT HIGHWAY 988 NEAR MIDDLESBORO, KY",
        "column_names": ["03_00010", "03_00010_cd", "02_00065", "02_00065_cd"],
        "parameters": parameters,
        "dates": dates,
        "timestep": "instaneous"   
    } 
    
    return data
    
def test_print():
    """ Test print output functionality """
    
    print("---Testing print ---")
    
    data = _create_testdata()
    print_info(nwis_data = data)
    
    print("")

def test_plot():
    """ Test plotting functionality """
    
    print("--- Testing plot ---")    
    
    data = _create_testdata()
    plot_data(nwis_data = data, is_visible = True, save_path = None)
    
    print("Plotting completed")
    print("")
    
def main():
    """ Test functionality of plotting and printing file information """
    
    test_print()
    
    test_plot()

if __name__ == "__main__":
    main() 
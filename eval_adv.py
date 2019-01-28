"""Description:

Evaluate the effectiveness of advertising from sales records
(a time series of sales with dates and sales amounts for each
transaction with optional sales type such as 'Sales Receipt'
to handle double entry bookkeeping)

Usage:  eval_adv.py -h for command line options and examples

Requirements: This program requires Python 3 and several Python
packages (see import lines below).  It was developed and tested with
the Ananconda Python 3.7 distribution which includes all required
Python packages.

Ananconda URL: https://www.anaconda.com/download/

Anaconda Version Info:

$ conda list anaconda
# packages in environment at C:\\Anaconda5p2:
#
# Name                    Version                   Build  Channel
anaconda                  5.2.0                    py36_3
anaconda-client           1.6.14                   py36_0
anaconda-navigator        1.8.7                    py36_0
anaconda-project          0.8.2            py36hfad2e28_0


Copyright (C) 2018 by John F. McGowan, Ph.D. (ceo@mathematical-software.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

# standard Python libraries
import os
import sys
import time
import datetime
import inspect
import subprocess  # getoutput(cmd_string)
import locale      # localization
import platform    # get Python version etc.
import shelve      # saving AdEvaluatorSettings
# use greatest common denominator (GCD) function
from math import gcd
# use named tuples
from collections import namedtuple

ANACONDA_DOWNLOAD_URL = 'http://www.anaconda.com/download/'

# get Python version
try:
    version_str = platform.python_version()
    version_list = version_str.split('.')
    major_version = int(version_list[0])
    if major_version < 3:
        raise ValueError(debug_prefix()
                         + 'ERROR: this program requires Python 3!  '
                         + 'Python Version: '
                         + version_str
                         + '  Try downloading and installing '
                         + 'the Anaconda Python 3 Distribution from'
                         + ANACONDA_DOWNLOAD_URL)

except Exception as my_X:
    print("Unable to get Python version string with EXCEPTION:")
    print(my_X)
    print("END EXCEPTION")

# TkInter GUI library
from tkinter import Tk
from tkinter import PhotoImage
from tkinter import Canvas
from tkinter import Toplevel
from tkinter import Menu
from tkinter import Text
# special Tk variables associated with widgets
from tkinter import IntVar
from tkinter import DoubleVar
from tkinter import StringVar
from tkinter import mainloop
# tkinter constants
from tkinter import END
from tkinter import RIGHT
from tkinter import LEFT
from tkinter import X
from tkinter import Y
from tkinter import HORIZONTAL
from tkinter import VERTICAL

from tkinter import filedialog
from tkinter import messagebox

# tkinter.ttk widgets
from tkinter.ttk import Button
from tkinter.ttk import Entry
from tkinter.ttk import Label
from tkinter.ttk import Checkbutton
from tkinter.ttk import Scrollbar
# GUI progress bar widget
from tkinter.ttk import Progressbar

# more Python standard libraries
import unittest
import io
from dateutil.parser import parse

# Scientific/Numerical Python libraries
import numpy as np
import pandas as pd
# SciPy
import scipy.stats as st
from scipy.optimize import curve_fit
from scipy.special import factorial  # elementwise factorial function
# graphics libraries

# differences between operating systems
if sys.platform == "win32":
    # Microsoft Windows
    pass
elif sys.platform == "darwin":
    # Apple Mac OS X
    import matplotlib
    matplotlib.use("TkAgg")
elif sys.platform == "linux":
    # Linux Unix variants
    pass
else:
    pass

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import FuncFormatter
from matplotlib.font_manager import FontProperties
# date formatting
import matplotlib.dates as mdates
import matplotlib.cbook as cbook

# choose matplotlib graphics style
plt.style.use('ggplot')
#pd.options.display.mpl_style = 'default'

mpl.rcParams['font.size'] = 14
mpl.rcParams['font.weight'] = 'bold'
mpl.rcParams['axes.labelweight'] = 'bold'
mpl.rcParams['axes.titleweight'] = 'bold'

# constants

# use *.py ident line in .gitattributes to turn on Dollar Sign Id tag
# erase eval_adv.py and checkout again to get the updated Dollar Sign Id tag
#
# the SHA is the BLOB sha, not the commit SHA :-(
PROJECT_GIT_SHA = "$Id: 047127d4302b3030132beba0e99dd9a44e7e1a6f $ \n\n"

# use git rev-list --count HEAD > eval_adv_version.txt
# to get commit count for the version number
PROJECT_VERSION = "1.X"
VERSION_FILE = "eval_adv_version.txt"
with open(VERSION_FILE) as version_file:
    PROJECT_VERSION = "1." + version_file.read()

NO_ADV_MARKER = 'bo' # blue filled circle
ADV_MARKER = 'gP'  # green filled plus sign

# line color
NO_ADV_LINE = 'b--'   # blue dashed line
ADV_LINE = 'g--'      # green dashed line

PROFIT_LINEWIDTH = 10
PROFIT_CHANGE_COLOR = 'r'  # k for black

LINEWIDTH = 3
MARKERSIZE = 10

AD_PRO_TEASER = """
COMING SOON

We are developing a professional version
of AdEvaluator\u2122 for multidimensional cases.
The pro version uses our Math Recognition
technology to automatically identify
good multidimensional mathematical models.

The Math Recognition technology is applicable
to all types of data.  It can for example be applied to
complex biological systems such as the
blood coagulation system which causes heart attacks
and strokes when it fails.  According the US
Centers for Disease Control (CDC) about
633,000 people died from heart attacks
and 140,000 from strokes in 2016.

"""

ALPHA_FISHER = 0.05  # Fisher's p-value cutoff
DAYS_PER_YEAR = 365.25
NSIMS_DEFAULT = 1000 # default to one thousand simulations
ADV_START_DATE = '03/31/2018'
MONTHS_PER_YEAR = 12
ANNUAL_ADV_EXPENSE = 500.0 * MONTHS_PER_YEAR  # annual advertising cost
BLOCK_DEFAULT = False
BINS_DEFAULT = 20  # was 50

SEED_VAL = 113  # default random number seed
INPUT_FILE = 'sales.csv'  # sales report from QuickBooks
OUTPUT_FOLDER = '.' # current folder

# maximum title string length in chars
MAX_TITLE_LENGTH_CHARS = 40
INFER_PRICE_TAG = "<INFER PRICE FROM DATA>"
ADRATER_URL = "http://wordpress.jmcgowan.com/wp/downloads/"
GEOMETRY_STRING = "750x422"

# duration to display the figures
PLOT_DURATION_SECS = 2.0

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
mondays = mdates.WeekdayLocator()
yearsFmt = mdates.DateFormatter('%b %Y')

def debug_prefix():
    """
    return <file_name>:<line_number> (<function_name>)
    """
    the_stack = inspect.stack()
    lineno = the_stack[1].lineno
    filename = the_stack[1].filename
    function = the_stack[1].function
    return (str(filename) + ":"
            + str(lineno)
            + " (" + str(function) + ") ")

# test classes

# unit test overkill
class TestClass(unittest.TestCase):
    """
    test class for module

    To run this test:

    $ python -m unittest eval_adv.TestClass
    """

    def test_get_date_refs(self):
        """test get_date_refs(...)"""
        data_frame = pd.DataFrame({'DATE' : ['12/1/2018',
                                             '12/2/2017'],
                                   'Type' : ['Sales Receipt',
                                             'Sales Receipt'],
                                   'CUSTOMER' : ['Bob', 'Sam'],
                                   'AMOUNT' : [90.0, 90.0]})
        self.assertEqual(get_date_refs(data_frame), ('DATE', 0))

    def test_get_amount_refs(self):
        """test get_amount_refs(...)"""
        data_frame = pd.DataFrame({'DATE' : ['12/1/2018',
                                             '12/2/2017'],
                                   'Type' : ['Sales Receipt',
                                             'Sales Receipt'],
                                   'CUSTOMER' : ['Bob', 'Sam'],
                                   'AMOUNT' : [90.0, 90.0]})
        self.assertEqual(get_amount_refs(data_frame), ('AMOUNT', 3))

    def test_get_type_refs(self):
        """test get_type_refs(...)"""
        data_frame = pd.DataFrame({'DATE' : ['12/1/2018',
                                             '12/2/2017'],
                                   'Type' : ['Sales Receipt',
                                             'Sales Receipt'],
                                   'CUSTOMER' : ['Bob', 'Sam'],
                                   'AMOUNT' : [90.0, 90.0]})
        self.assertEqual(get_type_refs(data_frame), ('Type', 1))

    def test_get_unit_prices(self):
        """
        test get_unit_prices(sales_data)
        """
        self.assertEqual(get_unit_prices([0.0, 50.0, 100.0, 150.0]), [50.0])
        self.assertEqual(get_unit_prices([-50.0, 50.0, 60.0, 100.0, 150.0]), \
                         [10.0])
        self.assertEqual(get_unit_prices([50.0, 100.0, 150.0]), [50.0])
        self.assertEqual(get_unit_prices([50.0, 60.0, 100.0, 150.0]), \
                         [10.0])
        self.assertEqual(get_unit_prices(np.array([50.0, 100.0, 150.0])), \
                                         [50.0])
        self.assertEqual(get_unit_prices(np.array([50.0, 60.0, 100.0, 150.0])), \
                                         [10.0])

    def test_get_units(self):
        """
        test get_units(sales_data)
        """
        sales_data = np.array([90.0, 180.0, 270.0])

        self.assertEqual(get_units(sales_data)[0], 1)
        self.assertEqual(get_units(sales_data)[1], 2)
        self.assertEqual(get_units(sales_data)[2], 3)

# module classes
class SalesStats:
    """
    sales statistics for sales report
    """

    def summary(self):
        """
            print summary report on sales statistics
        """
        print(str(self))

    def test(self):
        """
        TBD: simple self test
        """
        pass

    def __init__(self,
                 daily_sales_np,
                 mask_no_adv,
                 welch_t_edges=None,
                 welch_t_bins=None,
                 coeff_of_determination=None,
                 input_file=None,
                 empirical_p_value=None,
                 expected_profit_increase=None):
        self.mask_no_adv = mask_no_adv
        self.mask_adv = ~mask_no_adv
        # compute average daily sales for two periods
        self.ave_daily_sales_no_adv = daily_sales_np[mask_no_adv, 1].mean()
        self.ave_daily_sales_adv \
            = daily_sales_np[self.mask_adv, 1].mean()

        self.std_daily_sales_no_adv \
            = daily_sales_np[mask_no_adv, 1].std() \
            /np.sqrt(mask_no_adv.sum())
        self.std_daily_sales_adv \
            = daily_sales_np[self.mask_adv, 1].std()\
            /np.sqrt(self.mask_adv.sum())
        self.welch_t_edges = welch_t_edges
        self.welch_t_bins = welch_t_bins
        self.coeff_of_determination = coeff_of_determination
        self.input_file = input_file
        self.empirical_p_value = empirical_p_value

        # Welch's t-test
        # https://en.wikipedia.org/wiki/Welch's_t-test

        # In statistics, Welch's t-test, or unequal variances t-test, is a
        # two-sample location test which is used to test the hypothesis that
        # two populations have equal means. Welch's t-test is an adaptation
        # of Student's t-test.

        # Original reference:
        #
        # Welch, B. L. (1947).  "The generalization of "Student's" problem
        # when several different population variances are involved".
        # Biometrika. 34 (1-2): 28-35

        self.tstat, self.pvalue \
            = st.ttest_ind(daily_sales_np[self.mask_no_adv, 1], \
                           daily_sales_np[self.mask_adv, 1], \
                           None, equal_var=False)

        # compute pvalue based on empirical distribution
        # (not Bell Curve/Gaussian/Normal)
        tstat_bin_index \
            = np.argmax(self.welch_t_edges[:-1] > self.tstat)
        welch_t_hist_norm = self.welch_t_bins.sum()
        p_low \
            = self.welch_t_bins[:tstat_bin_index].sum() \
            /welch_t_hist_norm

        p_hi \
            = self.welch_t_bins[tstat_bin_index:].sum() \
            /welch_t_hist_norm

        self.empirical_pvalue = np.min([p_low, p_hi])
        self.expected_profit_increase = expected_profit_increase
        # end SalesStats.__init__(...)
    def __str__(self):
        text_str = "Average Daily Sales with Advertising: " \
                    + str(self.ave_daily_sales_adv) + "\n"
        text_str += "STD Daily Sales with Advertising: " \
                    + str(self.std_daily_sales_adv) + "\n"
        text_str += "Average Daily Sales without Advertising: " \
                    + str(self.ave_daily_sales_no_adv) + "\n"
        text_str += "STD Daily Sales without Advertising: " \
                    + str(self.std_daily_sales_no_adv) + "\n"
        return text_str
# end class SalesStats

# GUI classes and related functions

root = None

DETAIL_LEVEL_DEFAULT = 0
DATE_HEADER_DEFAULT = '<INFER DATE HEADER>'
AMOUNT_HEADER_DEFAULT = '<INFER AMOUNT HEADER>'
SALES_TYPE_HEADER_DEFAULT = '<INFER SALES TYPE HEADER>'
SALES_TYPE_VALUE_DEFAULT = ''
UNIT_COST_DEFAULT = 0.0
LAYERS_DEFAULT = False  # no layers by default

# named tuple for the GUI Configuration parameters
# set in Settings Dialog
AdEvaluatorSettings = namedtuple('AdEvaluatorSettings',
                                 # single string with spaces between names
                                 'annual_adv_expense '
                                 'unit_price '
                                 'number_sims '
                                 'detail_level '
                                 'adv_date '
                                 'date_tag '
                                 'amount_tag '
                                 'sales_type_tag '
                                 'sales_type_value '
                                 'unit_cost '
                                 'block '
                                 'layers '
                                 'bins')

def save_settings():
    """
    save settings to shelf file
    """
    global _settings

    try:
        if not _settings is None:
            shelf_h = shelve.open(AD_SETTINGS_FILE)
            # store values to shelf
            shelf_h['settings'] = _settings
            shelf_h.close()
    except Exception as my_X:
        cwd = os.getcwd()
        print(debug_prefix()
              + "Unable to update "
              + AD_SETTINGS_FILE
              + "in folder: " + cwd)
        print("EXCEPTION:")
        print(my_X)
        print("END EXCEPTION")
    # end save_settings()

def reset():
    """
    reset settings to default values
    """
    global _settings
    _settings = AdEvaluatorSettings(ANNUAL_ADV_EXPENSE,
                                    INFER_PRICE_TAG,
                                    NSIMS_DEFAULT,
                                    DETAIL_LEVEL_DEFAULT,
                                    ADV_START_DATE,
                                    DATE_HEADER_DEFAULT,
                                    AMOUNT_HEADER_DEFAULT,
                                    SALES_TYPE_HEADER_DEFAULT,
                                    SALES_TYPE_VALUE_DEFAULT,
                                    UNIT_COST_DEFAULT,
                                    BLOCK_DEFAULT,
                                    LAYERS_DEFAULT,
                                    BINS_DEFAULT)

    # end reset()

reset()

# shelf tag for GUI config info
AD_SETTINGS_FILE = "eval_adv_settings"
_b_load_settings = True

def load_settings():
    """
    load settings from shelf files if they exist
    """

    # need global to update _settings
    # NOT to read values
    global _settings

    if os.path.isfile(AD_SETTINGS_FILE + ".dat"):
        cwd = os.getcwd()
        try:
            shelf_h = shelve.open(AD_SETTINGS_FILE)
            # update _settings with saved values
            try:
                _settings = shelf_h['settings']
            finally:
                shelf_h.close()

            print('_settings', _settings)
        except FileNotFoundError as not_found_X:
            print(debug_prefix()
                  + "Unable to open "
                  + AD_SETTINGS_FILE
                  + " in folder: " + cwd)
        except Exception as my_X:
            # unable to open shelf
            print(debug_prefix()
                  + "Unable to update "
                  + AD_SETTINGS_FILE
                  + " in folder: " + cwd)
            print("EXCEPTION")
            print(my_X)
            print("END EXCEPTION")
    else:
        return -1

    return 0  # end load_settings()

class SettingsDialog:
    """
    class for program settings and configuration
    """
    def __init__(self, parent):
        global _settings
        global _b_load_settings

        if _b_load_settings:
            load_settings()

        top = self.top = Toplevel(parent)
        top.title("Settings Dialog")

        # annual advertising expense
        self.adv_expense_label = Label(top, text='Annual advertising expense:')
        self.adv_expense_label.grid(row=0, column=0)

        self.adv_expense_entry_box = Entry(top, width=30)
        # insert default value as text
        self.adv_expense_entry_box.insert(END, str(_settings.annual_adv_expense))
        self.adv_expense_entry_box.grid(row=0, column=1)

        # advertising start date
        self.adv_date_label = Label(top, text='Advertising Start Date')
        self.adv_date_label.grid(row=1, column=0)
        self.adv_date_entry_box = Entry(top, width=30)
        self.adv_date_entry_box.insert(END, str(_settings.adv_date))
        self.adv_date_entry_box.grid(row=1, column=1)

        # unit price charged to customers
        self.unit_price_label = Label(top, text='Unit Price')
        self.unit_price_label.grid(row=2, column=0)

        self.unit_price_entry_box = Entry(top, width=30)
        self.unit_price_entry_box.insert(END, INFER_PRICE_TAG)
        self.unit_price_entry_box.grid(row=2, column=1)

        # marginal cost of producing an additional unit
        self.unit_cost_label = Label(top, text='Unit Cost')
        self.unit_cost_label.grid(row=3, column=0)
        self.unit_cost_entry_box = Entry(top, width=30)
        if not _settings.unit_cost is None:
            self.unit_cost_entry_box.insert(END, str(_settings.unit_cost))
        self.unit_cost_entry_box.grid(row=3, column=1)

        # date column name (e.g. 'DATE')
        self.date_tag_label = Label(top, text='Date Column Name')
        self.date_tag_label.grid(row=4, column=0)

        self.date_tag_entry_box = Entry(top, width=30)
        if not _settings.date_tag is None:
            self.date_tag_entry_box.insert(END, str(_settings.date_tag))
        self.date_tag_entry_box.grid(row=4, column=1)

        # sales amount column name (e.g. 'Amount')
        self.amount_tag_label = Label(top, text='Sales Amount Column Name')
        self.amount_tag_label.grid(row=5, column=0)

        self.amount_tag_entry_box = Entry(top, width=30)
        if not _settings.amount_tag is None:
            self.amount_tag_entry_box.insert(END, str(_settings.amount_tag))
        self.amount_tag_entry_box.grid(row=5, column=1)

        # sales type column name (e.g. 'Type')
        self.sales_type_tag_label = Label(top, text='Sales Type Column Name')
        self.sales_type_tag_label.grid(row=6, column=0)

        self.sales_type_tag_entry_box = Entry(top, width=30)
        if not _settings.sales_type_tag is None:
            self.sales_type_tag_entry_box.insert(END, str(_settings.sales_type_tag))
        self.sales_type_tag_entry_box.grid(row=6, column=1)

        # sales type value (e.g. 'Sales Receipt')
        self.sales_type_value_label = Label(top, text='Sales Type Value')
        self.sales_type_value_label.grid(row=7, column=0)

        self.sales_type_value_entry_box = Entry(top, width=30)
        if not _settings.sales_type_value is None:
            self.sales_type_value_entry_box.insert(END, str(_settings.sales_type_value))
        self.sales_type_value_entry_box.grid(row=7, column=1)

        # debug trace level
        self.detail_level_label = Label(top, text="Detail Level")
        self.detail_level_label.grid(row=8, column=0)
        # enter the detail level through GUI
        self.detail_level_box = Entry(top, width=30)
        if not _settings.detail_level is None:
            self.detail_level_box.insert(END, str(_settings.detail_level))
        self.detail_level_box.grid(row=8, column=1)

        # number of simulations for sales/profit projections
        self.nsims_label = Label(top, text="Number of Simulations")
        self.nsims_label.grid(row=9, column=0)
        # enter number of simulations through GUI
        self.nsims_box = Entry(top, width=30)
        if not _settings.number_sims is None:
            self.nsims_box.insert(END, str(_settings.number_sims))
        self.nsims_box.grid(row=9, column=1)

        self.layers = IntVar()
        self.layers.set(_settings.layers)

        self.layers_box = Checkbutton(top,
                                      text="Plot Layers",
                                      variable=self.layers).grid(row=10, column=0)

        self.block = IntVar()
        self.block.set(_settings.block)

        self.block_box = Checkbutton(top,
                                     text="Block on Figures",
                                     variable=self.block).grid(row=10, column=1)

        self.submit_button = Button(top, text='OK', command=self.send)
        self.submit_button.grid(row=11, column=0)

        self.cancel_button = Button(top, text='Cancel', command=self.do_nothing)
        self.cancel_button.grid(row=11, column=1)

        self.reset_button = Button(top, text='Reset', command=self.reset)
        self.reset_button.grid(row=12, column=1)

        top.focus_force()
        # end SettingsDialog.__init___()

    def reset(self):
        """
        reset the settings to the default values
        """
        reset() # reset to defaults
        self.update() # update the dialog values
        self.save_settings()  # save to shelf files
        # end SettingsDialog.reset()

    def update(self):
        """
        update the dialog
        """
        # annual advertising expense
        # insert default value as text
        self.adv_expense_entry_box.delete(0, "end")
        self.adv_expense_entry_box.insert(END, str(_settings.annual_adv_expense))

        # advertising start date
        self.adv_date_entry_box.delete(0, "end")
        self.adv_date_entry_box.insert(END, str(_settings.adv_date))

        # unit price charged to customers
        self.unit_price_entry_box.delete(0, "end")
        self.unit_price_entry_box.insert(END, INFER_PRICE_TAG)

        # marginal cost of producing an additional unit
        if not _settings.unit_cost is None:
            self.unit_cost_entry_box.delete(0, "end")
            self.unit_cost_entry_box.insert(END, str(_settings.unit_cost))

        # date column name (e.g. 'DATE')
        if not _settings.date_tag is None:
            self.date_tag_entry_box.delete(0, "end")
            self.date_tag_entry_box.insert(END, str(_settings.date_tag))

        # sales amount column name (e.g. 'Amount')
        if not _settings.amount_tag is None:
            self.amount_tag_entry_box.delete(0, "end")
            self.amount_tag_entry_box.insert(END, str(_settings.amount_tag))

        # sales type column name (e.g. 'Type')
        if not _settings.sales_type_tag is None:
            self.sales_type_tag_entry_box.delete(0, "end")
            self.sales_type_tag_entry_box.insert(END, str(_settings.sales_type_tag))

        if not _settings.sales_type_value is None:
            self.sales_type_value_entry_box.delete(0, "end")
            self.sales_type_value_entry_box.insert(END, str(_settings.sales_type_value))

        if not _settings.detail_level is None:
            self.detail_level_box.delete(0, "end")
            self.detail_level_box.insert(END, str(_settings.detail_level))

        # number of simulations for sales/profit projections
        if not _settings.number_sims is None:
            self.nsims_box.delete(0, "end")
            self.nsims_box.insert(END, str(_settings.number_sims))

        self.block.set(_settings.block)
        self.layers.set(_settings.layers)

        # end SettingsDialog.update()

    def do_nothing(self):
        """
        do nothing -- to cancel
        """
        self.top.destroy()
        # end SettingsDialog.do_nothing()

    def send(self):
        """
        send command for submit button
        """
        global _settings

        # get values
        new_value = self.adv_expense_entry_box.get()
        if new_value:
            try:
                _settings \
                    = _settings._replace(annual_adv_expense=float(new_value))
            except Exception as general_exception:
                print(debug_prefix()
                      + "Unable to process entry with EXCEPTION:")
                print(general_exception)
                print("END EXCEPTION")
                print("new_value:", new_value)

        new_value = self.adv_date_entry_box.get()
        _settings = _settings._replace(adv_date=new_value)

        new_value = self.unit_cost_entry_box.get()
        if new_value:
            try:
                _settings = _settings._replace(unit_cost=float(new_value))
            except Exception as general_exception:
                print(debug_prefix()
                      + "Unable to process entry with EXCEPTION:")
                print(general_exception)
                print("END EXCEPTION")

        new_value = self.date_tag_entry_box.get()
        _settings = _settings._replace(date_tag=new_value)

        new_value = self.amount_tag_entry_box.get()
        _settings = _settings._replace(amount_tag=new_value)

        new_value = self.sales_type_tag_entry_box.get()
        _settings = _settings._replace(sales_type_tag=new_value)

        new_value = self.sales_type_value_entry_box.get()
        _settings = _settings._replace(sales_type_value=new_value)

        new_value = self.detail_level_box.get()
        if new_value:
            try:
                _settings = _settings._replace(
                    detail_level=int(new_value))
            except Exception as general_exception:
                print(debug_prefix()
                      + "Unable to process detail_level_box entry with EXCEPTION:")
                print(general_exception)
                print("END EXCEPTION")
                print("new_value:", new_value)

        new_value = self.nsims_box.get()
        if new_value:
            try:
                _settings = _settings._replace(
                    number_sims=float(new_value))
            except Exception as general_exception:
                print(debug_prefix()
                      + "Unable to process nsims_box entry with EXCEPTION:")
                print(general_exception)
                print("END EXCEPTION")
                print("new_value:", new_value)

        try:
            _settings = _settings._replace(block=self.block.get())
        except Exception as general_exception:
            print(debug_prefix()
                  + "Unable to process block figure "
                  "checkbox with EXCEPTION:")
            print(general_exception)
            print("END EXCEPTION")

        # save Settings values to the shelf files
        self.save_settings()

        self.top.destroy()  # SettingsDialog.send() method

    def save_settings(self):
        """
        save settings to the shelf file
        """
        save_settings()
        # end SettingsDialog.save_settings()

def launch_settings(event=None):
    """
    click function for dialog box
    """
    global root
    settings_dialog = SettingsDialog(root)
    root.wait_window(settings_dialog.top)

# module functions

file_name = None

def plot_sales_data(input_file,
                    first_date,
                    day_np,
                    mask_adv,
                    mask_no_adv,
                    ma_period_days,
                    daily_sales_np,
                    sales_stats,
                    plot_duration_secs,
                    output_folder,
                    show_ma=True,
                    show_period_average=True):
    """
    plot daily sales data with optional moving average and period averages
    """

    if not isinstance(input_file, str):
        raise TypeError(debug_prefix()
                        + " input_file is type "
                        + str(type(input_file)))

    if not isinstance(day_np, np.ndarray):
        raise TypeError(debug_prefix()
                        + " day_np is type "
                        + str(type(day_np)))

    if not isinstance(daily_sales_np, np.ndarray):
        raise TypeError(debug_prefix()
                        + " daily_sales_np is type "
                        + str(type(daily_sales_np)))


    # extract the file stem (e.g. blatz from blatz.txt)
    base_file_name = os.path.basename(input_file)
    parts = base_file_name.split('.')
    file_stem = parts[0]

    # compute moving average of daily sales
    tmp1 = daily_sales_np[:, 1].ravel()
    #print("tmp1.shape", tmp1.shape)
    tmp2 = np.ones((ma_period_days, 1)).ravel()/float(ma_period_days)
    #print("tmp2.shape", tmp2.shape)

    # compute moving (aka running) average of daily
    # sales of 30 day period
    daily_sales_ma = np.convolve(tmp1, tmp2, 'same')
    #print("daily_sales_ma.shape", daily_sales_ma.shape)

    # period average daily sales
    ave_daily_sales = np.zeros(daily_sales_ma.shape)

    ave_daily_sales[mask_no_adv] \
        = sales_stats.ave_daily_sales_no_adv
    ave_daily_sales[mask_adv] \
        = sales_stats.ave_daily_sales_adv



    # make plot of sales data
    figure_sales = plt.figure(figsize=(12, 9))

    dates = [first_date + datetime.timedelta(float(day), 0, 0)
             for day in day_np]

    adv_dates = [first_date + datetime.timedelta(float(day), 0, 0)
                 for day in day_np[mask_adv]]

    no_adv_dates = [first_date + datetime.timedelta(float(day), 0, 0)
                    for day in day_np[mask_no_adv]]

    ma_dates = [first_date + datetime.timedelta(float(day), 0, 0)
                for day in day_np[ma_period_days:-ma_period_days]]

    plt.plot(no_adv_dates, daily_sales_np[mask_no_adv, 1], \
             NO_ADV_MARKER, label="NO ADVERTISING", markersize=MARKERSIZE)
    plt.plot(adv_dates, daily_sales_np[mask_adv, 1],
             ADV_MARKER,
             label="WITH ADVERTISING", markersize=MARKERSIZE)

    if show_period_average:
        plt.plot(dates, ave_daily_sales, 'r-', label='PERIOD AVERAGE', \
                 linewidth=LINEWIDTH, markersize=MARKERSIZE)

    if show_ma:
        # plot the moving average of the daily sales
        plt.plot(ma_dates, \
                 daily_sales_ma[ma_period_days:-ma_period_days], 'k-', \
                 label=str(ma_period_days) + ' DAY AVERAGE', linewidth=LINEWIDTH)

    plt.title('DAILY SALES (from ' + os.path.basename(input_file) + ')')
    plt.xlabel('DATE')
    plt.ylabel('DOLLARS')
    plt.grid()
    plt.legend(loc='upper right')
    #
    # only show Welch's T test in
    # debug mode
    #
    if _settings.detail_level > 0:
        xlow, xhi = plt.xlim()
        delta_x = xhi - xlow
        ylow, yhi = plt.ylim()
        delta_y = yhi - ylow
        plt.text(xlow + 0.05*delta_x, yhi - 0.05*delta_y, \
                 "Welch's T Statistic: %4.2f" \
                 % sales_stats.tstat, \
                 bbox=dict(facecolor='white', alpha=0.5))
        plt.text(xlow + 0.05*delta_x, yhi - 0.1*delta_y, \
                 "Probability Difference Due to Chance (p-value): %4.3f" \
                 % sales_stats.pvalue, \
                 bbox=dict(facecolor='white', alpha=0.5))

    ax_list = figure_sales.axes
    ax = ax_list[0]

    # format the ticks
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(mondays)
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

    ax.grid(True)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    figure_sales.autofmt_xdate()

    if _settings.block:
        plt.show()
    else:
        plt.ion()
        plt.show()
        # wait to display the figure
        plt.pause(plot_duration_secs)

    # save figure

    if show_ma:
        ma_suffix = '_ma'
    else:
        ma_suffix = ''

    if show_period_average:
        ave_suffix = '_period_ave'
    else:
        ave_suffix = ''

    image_file = file_stem + ma_suffix + ave_suffix + ".jpg"
    print("saving figure to", image_file)
    figure_sales.savefig(output_folder + os.sep + image_file)

    return daily_sales_ma  # return the moving average
    # end plot_sales_data(...)


def plot_ave_hist(ave_sales_increase_diff,
                  input_file,
                  output_folder,
                  title_str='AVERAGE DAILY SALES',
                  plot_duration_secs=2.0):
    """
    plot histogram of the average sales from the simulations
    """

    if not isinstance(input_file, str):
        raise TypeError(debug_prefix()
                        + " input_file is type "
                        + str(type(input_file)))

    if not isinstance(title_str, str):
        raise TypeError(debug_prefix()
                        + " title_str is type "
                        + str(type(title_str)))

    if not isinstance(output_folder, str):
        raise TypeError(debug_prefix()
                        + " output_folder is type "
                        + str(type(output_folder)))

    # extract the file stem
    base_file_name = os.path.basename(input_file)
    parts = base_file_name.split('.')
    file_stem = parts[0]

    fig_ave_hist = plt.figure(figsize=(12, 9))
    bin_values, \
        bin_edges, \
        patches = plt.hist(ave_sales_increase_diff,
                           bins=_settings.bins)
    plt.title(title_str)
    plt.xlabel('DOLLARS')
    plt.ylabel('NUMBER OF SIMULATIONS')
    plt.grid()

    ax_list = fig_ave_hist.axes
    ax = ax_list[0]
    formatter = FuncFormatter(currency)
    ax.xaxis.set_major_formatter(formatter)

    if _settings.block:
        plt.show()
    else:
        plt.ion()
        plt.show()  # sales projection histogram
        # wait to display the figure
        plt.pause(plot_duration_secs)

    suffix = title_str.replace(" ", "_")
    image_file = file_stem \
                 + "_sales_projection_" \
                 + suffix + ".jpg"
    print("saving sales projection figure to", image_file)
    fig_ave_hist.savefig(output_folder
                            + os.sep
                            + image_file)
    return bin_values, bin_edges
    # end plot_ave_hist(...)

def plot_diff_risk(profit_edges_no_adv,
                   profit_bins_no_adv,
                   profit_edges_adv,
                   profit_bins_adv,
                   number_sims,
                   input_file,
                   expected_profit_increase,
                   annual_adv_expense,
                   n_loss_sales,
                   n_loss_profits,
                   seed_val,
                   plot_duration_secs,
                   output_folder,
                   suffix='',
                   show_no_adv=True,
                   show_with_adv=True,
                   show_ave_with_adv=True):
    """
    plot overlay of profit projections with
    and without advertising
    """
    if not isinstance(input_file, str):
        raise TypeError(debug_prefix()
                        + " input_file is type "
                        + str(type(input_file)))

    # extract the file stem
    base_file_name = os.path.basename(input_file)
    parts = base_file_name.split('.')
    file_stem = parts[0]

    if show_no_adv and show_with_adv and show_ave_with_adv:
        suffix = ''
    else:
        # build suffix for each layer image
        # layers for animations
        if show_no_adv:
            suffix += "_no_adv"
        if show_with_adv:
            suffix += "_with_adv"
        if show_ave_with_adv:
            suffix += +"_ave"

    # main sales and profit projections plot/figure
    fig_projections = plt.figure(figsize=(12, 9))

    if False:
        plt.plot((profit_edges_no_adv[1:]+profit_edges_no_adv[:-1])/2.0, \
                 100.0*profit_bins_no_adv/number_sims, \
                 NO_ADV_MARKER,
                 label='PROFIT CHANGE NO ADVERTISING',
                 linewidth=LINEWIDTH, markersize=MARKERSIZE)

        plt.plot((profit_edges_adv[1:]+profit_edges_adv[:-1])/2.0, \
                 100.0*profit_bins_adv/number_sims, \
                 ADV_MARKER,
                 label='PROFIT CHANGE WITH ADVERTISING',
                 linewidth=LINEWIDTH, markersize=MARKERSIZE)
    else:
        bar_width = (profit_edges_no_adv[1]
                     - profit_edges_no_adv[0])/2.0
        opacity = 0.8

        if show_no_adv:
            plt.bar((profit_edges_no_adv[1:]
                     +profit_edges_no_adv[:-1])/2.0,
                    100.0*profit_bins_no_adv/number_sims,
                    bar_width,
                    alpha=opacity,
                    color='b',
                    label='PROFIT CHANGE NO ADVERTISING')
        
            
        if show_with_adv:
            plt.bar(bar_width + (profit_edges_adv[1:]
                                 + profit_edges_adv[:-1])/2.0,
                    100.0*profit_bins_adv/number_sims,
                    bar_width,
                    alpha=opacity,
                    color='g',
                    label='PROFIT CHANGE WITH ADVERTISING')
        else:
            # suppress the with advertising bars
            # but keep same horizontal axis
            dummy_bins = np.zeros(profit_bins_adv.shape)
            plt.bar(bar_width + (profit_edges_adv[1:]
                                 + profit_edges_adv[:-1])/2.0,
                    100.0*dummy_bins/number_sims,
                    bar_width,
                    alpha=opacity,
                    color='g',
                    label='PROFIT CHANGE WITH ADVERTISING')
            

    xlow, xhi = plt.xlim()
    delta_x = (xhi - xlow)
    ylow, yhi = plt.ylim()
    delta_y = (yhi - ylow)
    offset = 0.045
    if show_ave_with_adv:
        # add vertical line
        plt.axvline(expected_profit_increase,
                    ymin=ylow, ymax=yhi,
                    linewidth=PROFIT_LINEWIDTH,
                    color=PROFIT_CHANGE_COLOR,
                    label='EXPECTED PROFIT FROM ADVERTISING')

    plt.grid()
    plt.title('FULL YEAR PROJECTIONS ('
              + format(number_sims, ',d')
              + ' SIMULATIONS)  FROM: '
              + os.path.basename(input_file))
    plt.xlabel('ANNUAL PROFIT CHANGE (DOLLARS)')
    plt.ylabel('PERCENT OF SIMULATIONS')
    plt.legend(loc='upper right')

    #
    # reported expected profit or loss from simulations
    #
    profit_loss_str = locale.currency(expected_profit_increase,
                                      grouping=True)
    plt.text(xlow + 0.025*delta_x,
             yhi - offset*delta_y,
             "Expected Profit Change: "
             + profit_loss_str,
             bbox=dict(facecolor='white', alpha=0.5))

    # format the currency values
    ax_list = fig_projections.axes
    ax = ax_list[0]
    formatter = FuncFormatter(currency)
    ax.xaxis.set_major_formatter(formatter)

    if _settings.block:
        plt.show()
    else:
        plt.ion()
        plt.show()
        # wait to display the figure
        plt.pause(plot_duration_secs)  # sales and profits projections histograms

    image_file = file_stem \
                 + "_sales_projection" \
                 + suffix + ".jpg"
    print("saving sales projection figure to", image_file)
    fig_projections.savefig(output_folder + os.sep + image_file)
    # END plot_diff_risk(...)  MAIN PLOT


def plot_projections(sales_edges,
                     sales_bins,
                     profit_edges,
                     profit_bins,
                     number_sims,
                     input_file,
                     expected_profit_increase,
                     annual_adv_expense,
                     n_loss_sales,
                     n_loss_profits,
                     seed_val,
                     plot_duration_secs,
                     output_folder,
                     suffix=''):
    """
    plot the sales/profit projections
    """

    if not isinstance(input_file, str):
        raise TypeError(debug_prefix()
                        + " input_file is type "
                        + str(type(input_file)))

    # extract the file stem
    base_file_name = os.path.basename(input_file)
    parts = base_file_name.split('.')
    file_stem = parts[0]

    # main sales and profit projections plot/figure
    fig_projections = plt.figure(figsize=(12, 9))
    plt.plot((profit_edges[1:]+profit_edges[:-1])/2.0, \
             100.0*profit_bins/number_sims, \
             'bo', label='PROFIT INCREASE/DECREASE', linewidth=LINEWIDTH, markersize=MARKERSIZE)
    plt.plot((sales_edges[1:]+sales_edges[:-1])/2.0, \
             100.0*sales_bins/number_sims, \
             'gP', label='SALES INCREASE/DECREASE', linewidth=LINEWIDTH, markersize=MARKERSIZE)
    plt.grid()
    plt.title('FULL YEAR PROJECTIONS (' + str(number_sims)
              + ' SIMULATIONS)  FROM: ' + os.path.basename(input_file))
    plt.xlabel('DOLLARS')
    plt.ylabel('PERCENT OF SIMULATIONS')
    plt.legend(loc='upper right')
    xlow, xhi = plt.xlim()
    delta_x = (xhi - xlow)
    ylow, yhi = plt.ylim()
    delta_y = (yhi - ylow)
    offset = 0.045

    #
    # reported expected profit or loss from simulations
    #
    profit_loss_str = locale.currency(expected_profit_increase,
                                      grouping=True)
    plt.text(xlow + 0.025*delta_x,
             yhi - offset*delta_y,
             "Expected Profit Change: "
             + profit_loss_str,
             bbox=dict(facecolor='white', alpha=0.5))

    adv_expense_str = locale.currency(-1.0*annual_adv_expense,
                                      grouping=True)
    plt.text(xlow + 0.025*delta_x,
             yhi - 2*offset*delta_y,
             "ANNUAL ADVERTISING EXPENSES: " + adv_expense_str,
             bbox=dict(facecolor='white', alpha=0.5))

    plt.text(xlow + 0.025*delta_x,
             yhi - 3*offset*delta_y,
             "Simulations with "
             + "a Sales Decline: %5.1f / %5.1f"
             % (n_loss_sales, number_sims),
             bbox=dict(facecolor='white', alpha=0.5))

    plt.text(xlow + 0.025*delta_x,
             yhi - 4*offset*delta_y,
             "Simulations with " +
             "Losses: %5.1f / %5.1f"
             % (n_loss_profits, number_sims),
             bbox=dict(facecolor='white', alpha=0.5))

    plt.text(xlow + 0.025*delta_x,
             yhi - 5*offset*delta_y,
             "Random Number Seed: %d" % seed_val,
             bbox=dict(facecolor='white', alpha=0.5))

    ax_list = fig_projections.axes
    ax = ax_list[0]
    formatter = FuncFormatter(currency)
    ax.xaxis.set_major_formatter(formatter)

    if _settings.block:
        plt.show()
    else:
        plt.ion()
        plt.show()
        # wait to display the figure
        plt.pause(plot_duration_secs)  # sales and profits projections histograms

    image_file = file_stem + "_sales_projection" + suffix + ".jpg"
    print("saving sales projection figure to", image_file)
    fig_projections.savefig(output_folder + os.sep + image_file)
    # end plot_projections(....)


# menu item functions
def new_file():
    """dummy create new file"""
    print("New File!")

def open_file(event=None):
    """ open a sales report file """
    global file_name
    global root

    # filetypes=(...) works on both Windows and Mac OS X
    # filetype=(...) worked on Windows but not Mac OS X
    file_name = filedialog.askopenfilename(initialdir=".",
                                           title="Open Sales Report file",
                                           filetypes=(("CSV Files", "*.csv"),
                                                      ("All Files", "*.*")))
    if len(file_name) > MAX_TITLE_LENGTH_CHARS:
        file_name_display = "..." + file_name[-(MAX_TITLE_LENGTH_CHARS-3):]
    else:
        file_name_display = file_name

    # update GUI title with abbreviated file name
    if file_name_display:
        root.title("AdEvaluator\u2122 (" + file_name_display + ")")
    print(file_name)  # open_file()

def view_file(event=None):
    """
    show contents of sales report file selected
    """
    global file_name
    global root

    if file_name is None:
        contents = "No sales report file selected!"
    elif not file_name:
        contents = "No sales report file selected! <file_name is empty string>"
    elif os.path.exists(file_name):
        # read file
        with open(file_name) as sales_report:
            contents = sales_report.read()
    else:
        contents = "FILE " + str(file_name) + " NOT FOUND\n"

    popup_win = Toplevel()
    scroll_bar = Scrollbar(popup_win)
    text_widget = Text(popup_win, height=24, width=80)
    scroll_bar.pack(side=RIGHT, fill=Y)
    text_widget.pack(side=LEFT, fill=Y)
    scroll_bar.config(command=text_widget.yview)
    text_widget.config(yscrollcommand=scroll_bar.set)
    text_widget.insert(END, contents)
    # view_file

def show_help(event=None):
    """ show help message in GUI"""
    popup_win = Toplevel()
    popup_win.title("Help -- AdEvaluator\u2122")
    scroll_bar = Scrollbar(popup_win)
    text_widget = Text(popup_win, height=24, width=80)
    scroll_bar.pack(side=RIGHT, fill=Y)
    text_widget.pack(side=LEFT, fill=Y)
    scroll_bar.config(command=text_widget.yview)
    text_widget.config(yscrollcommand=scroll_bar.set)
    help_text = ad_help()
    assert isinstance(help_text, str)
    text_widget.insert(END, help_text)


def ad_help(event=None):
    """
    Help message for app
    """

    help_text = """

    AdEvaluator\u2122 processes a sales report in comma separated values
(CSV) format with a DATE column, a sales AMOUNT column, and an
optional SALES TYPE column.  It computes the daily total sales for
each day during the period of the sales report.  It divides the sales
report period into two parts, a "no advertising" period followed by an
"advertising" or "new advertising" period.

    The unit price of the product or service sold should be the same
during the entire sales report period, both the "advertising" and the
"no advertising" sub-periods.  There should be no other changes
between the two periods other than the new advertising, sales,
marketing, or public relations campaign or program.

    AdEvaluator\u2122 returns an estimated of the projected profit/loss for
a year with the advertising continued as well as a histogram (bar
chart) showing the frequency of different outcomes based on a larg
number of simulations of the future.  The default number of
simulations is one-thousand (1000).

    AdEvaluator\u2122 also reports other details from the simulations and
several standard "classical" statistical tests such as Welch's T Test
-- a more advanced, robust derivative of Student's T test for
evaluating whether two disributions are the same (in our case, any
change in average daily sales between the "no advertising" and
"advertising" sub-periods is due to chance).

"""

    help_text += AD_PRO_TEASER
    help_text += startup_notice("AdEvaluator\u2122")

    return help_text  # ad_help()

def show_glossary(event=None):
    """
    show glossary of technical terms
    """
    popup_win = Toplevel()
    popup_win.title("Glossary -- AdEvaluator\u2122")
    scroll_bar = Scrollbar(popup_win)
    text_widget = Text(popup_win, height=24, width=80)
    scroll_bar.pack(side=RIGHT, fill=Y)
    text_widget.pack(side=LEFT, fill=Y)
    scroll_bar.config(command=text_widget.yview)
    text_widget.config(yscrollcommand=scroll_bar.set)
    glossary_text = glossary()
    assert isinstance(glossary_text, str)
    text_widget.insert(END, glossary_text)

def show_disclaimer(event=None):
    """
    show the disclaimer message
    """
    popup_win = Toplevel()
    popup_win.title("Disclaimer -- AdEvaluator\u2122")
    scroll_bar = Scrollbar(popup_win)
    text_widget = Text(popup_win, height=24, width=80)
    scroll_bar.pack(side=RIGHT, fill=Y)
    text_widget.pack(side=LEFT, fill=Y)
    scroll_bar.config(command=text_widget.yview)
    text_widget.config(yscrollcommand=scroll_bar.set)
    disclaimer_text = disclaimer()
    assert isinstance(disclaimer_text, str)
    disclaimer_text += startup_notice(os.path.basename(sys.argv[0]))
    text_widget.insert(END, disclaimer_text)

def show_usage(event=None):
    """ show usage message in GUI"""
    popup_win = Toplevel()
    popup_win.title("Usage -- AdEvaluator\u2122")
    scroll_bar = Scrollbar(popup_win)
    text_widget = Text(popup_win, height=24, width=80)
    scroll_bar.pack(side=RIGHT, fill=Y)
    text_widget.pack(side=LEFT, fill=Y)
    scroll_bar.config(command=text_widget.yview)
    text_widget.config(yscrollcommand=scroll_bar.set)
    usage_text = usage(sys.argv[0])
    assert isinstance(usage_text, str)
    text_widget.insert(END, usage_text)

def show_license(event=None):
    """ show license in GUI """
    popup_win = Toplevel()
    popup_win.title("License -- AdEvaluator\u2122")
    scroll_bar = Scrollbar(popup_win)
    text_widget = Text(popup_win, height=24, width=80)
    scroll_bar.pack(side=RIGHT, fill=Y)
    text_widget.pack(side=LEFT, fill=Y)
    scroll_bar.config(command=text_widget.yview)
    text_widget.config(yscrollcommand=scroll_bar.set)
    license_text = gpl_v3_license()
    assert isinstance(license_text, str)
    text_widget.insert(END, license_text)

def open_website(event=None):
    """ launch AdEvaluator website """
    if sys.platform == "win32":
        os.system("rundll32 url.dll,FileProtocolHandler "
                  + ADRATER_URL)
    elif sys.platform == "darwin":
        # OS X
        os.system("open " + ADRATER_URL)
    elif sys.platform == "linux" or sys.platform == "linux2":
        # Linux
        #
        # not all Linux have xdg-open
        #
        os.system("xdg-open " + ADRATER_URL)
    else:
        messagebox.showerror("AdEvaluator\u2122",
                             "ERROR: Cannot determine the operating system "
                             "to launch the web browswer")

def about_program(event=None):
    """ about program message """
    messagebox.showinfo("About AdEvaluator\u2122",
                        "AdEvaluator\u2122 \n"
                        + "Project Version: " + PROJECT_VERSION +
                        "evaluates the effectiveness of a "
                        "new advertising, sales, or marketing method or "
                        "campaign.\n\n" + AD_PRO_TEASER +
                        "Copyright (C) 2018 by John F. "
                        "McGowan, Ph.D. (ceo@mathematical-software.com)\n")

def eval_file(event=None):
    """
    evaluate advertising performance
    """
    global file_name
    global root
    global _settings

    if file_name is None:
        messagebox.showerror("AdEvaluator\u2122",
                             "ERROR: No sales report file selected.  "
                             "Try File | Open Sales Report...")
        return

    if not file_name:
        messagebox.showerror("AdEvaluator\u2122",
                             "ERROR: No sales report file selected.  "
                             "Try File | Open Sales Report...")
        return

    if os.path.exists(file_name):
        #cmd_str = "python eval_adv.py \"" + file_name + "\""
        #print("Executing:", cmd_str)
        #output = subprocess.getoutput(cmd_str)
        #print(output)

        args = ['-i', file_name,
                '-e', _settings.annual_adv_expense,
                '-n', _settings.number_sims,
                '-d', str(_settings.detail_level)]

        if bool(_settings.block):
            args.append('-b')

        if bool(_settings.layers):
            args.append("-l")  # layered plots for animation

        # fix unit price if set in GUI
        if _settings.unit_price != INFER_PRICE_TAG:
            args.append("-price")
            args.append(str(_settings.unit_price))

        if not _settings.adv_date is None:
            if isinstance(_settings.adv_date, str):
                args.append("-adv_date")
                args.append(str(_settings.adv_date))

        if not _settings.unit_cost is None:
            if _settings.unit_cost:
                if _settings.unit_cost != UNIT_COST_DEFAULT:
                    args.append("-unit_cost")
                    args.append(str(_settings.unit_cost))

        if not _settings.date_tag is None:
            if _settings.date_tag:
                if _settings.date_tag != DATE_HEADER_DEFAULT:
                    args.append("-date_tag")
                    args.append(str(_settings.date_tag))

        if not _settings.amount_tag is None:
            if _settings.amount_tag:
                if _settings.amount_tag != AMOUNT_HEADER_DEFAULT:
                    args.append("-amount_tag")
                    args.append(str(_settings.amount_tag))

        if not _settings.sales_type_tag is None:
            if _settings.sales_type_tag:
                if _settings.sales_type_tag != SALES_TYPE_HEADER_DEFAULT:
                    args.append("-sales_type_tag")
                    args.append(str(_settings.sales_type_tag))

        if not _settings.sales_type_value is None:
            if _settings.sales_type_value:
                args.append("-sales_type_value")
                args.append(str(_settings.sales_type_value))

        print(args)
        try:
            evaluate_advertising(*args)
        except Exception as general_exception:
            messagebox.showerror("AdEvaluator\u2122", debug_prefix()
                                 + "EXCEPTION: "
                                 + print_to_string(general_exception))
        root.lift()
        #root.force_focus()  # failed
        root.after(1, lambda: root.focus_force())
        root.geometry(GEOMETRY_STRING)
    else:
        msg = print_to_string(debug_prefix()
                              + "ERROR: Unable to find "
                              "input file (sales report): <"
                              , file_name, ">")
        messagebox.showerror("AdEvaluator\u2122", msg)

def glossary(event=None):
    """
    glossary of technical terms
    """
    glossary_text = """GLOSSARY

NULL HYPOTHESIS The statistics literature loves the cryptic term "null
hypothesis".  In our case this refers to the hypothesis that the no
advertising period and the with advertising period are the same.  The
advertising has no effect.  The chance (probability) of a sale is the
same in both periods.

CLASSICAL STATISTICS Classical statistics primarily refers to the
statistical methods and theories developed by Ronald Fisher, William
Sealy Gossett (better known by the pseudonym Student), and their
colleagues and rivals in the 1920's and 1930's.  These powerful,
widely used methods predate computers and were invented using calculus
and pen and paper.  These methods have the advantage that they require
little computing power and they are understandable, as compared to
machine learning and deep learning methods which require enormous
computing power and are currently difficult to understand.  A good
statistician can explain in English what the formulas are doing and
justify the decisions they recommend.  In our case we can compute the
sales and profit/loss projections using a laptop computer -- a
warehouse full of GPUs is not required -- and we can explain the basis
for the projections in English.

P-VALUE  The probability that the null hypothesis will by chance produce
the data.  In our case, we are interested in the probability that the
business with no advertising will produce the sales recorded during the
advertising period *by chance*.  In our case, if the P VALUE is large, such
as 0.5, then the advertising has a good chance of having no effect.

The P VALUE is widely used in classical statistics.  It is a measure of
statistical significance, NOT practical significance such as profit and
loss for a business.  At best, a tiny P VALUE only tells us that the
advertising had some effect, not the size of the effect. This is why the
program computes and displays the projected sales increase or decrease
and the projected profit or loss due to the advertising.

For example, consider a candy store that sells one hundred candy bars for
one dollar on average each day.  The candy store pays five hundred dollars
per month for a billboard a few blocks away.  The billboard increases the
sales by an average of one candy bar per day.  This small increase in sales
is large enough that the P VALUE will be tiny, clearly showing the billboard
causes a change in sales.  However, the billboard costs $500.00 per month
but the extra sales bring in at most $30.00 more per month.  Consequently, the
billboard is a money-losing method even though the P VALUE is tiny.

Modern statistics is moving away from the P VALUE and using confidence levels
because of this and other weaknesses with the P VALUE.  Most statistical
functions and packages in Python, MATLAB, SAS, and other tools continue to
report the P VALUE.  This program reports both P VALUES and confidence levels
in the form of sales and profit and loss projections.

Copyright (C) 2018 by John F. McGowan, Ph.D.
E-Mail: ceo@mathematical-software.com

"""
    return glossary_text

def disclaimer():
    """
    disclaimer text
    """

    disclaimer_text = """Disclaimer

AdEvaluator\u2122 is designed for cases with a single product or
service with a constant unit price during both
periods. AdEvaluator\u2122 needs a reference period without the new
advertising and a test period with the new advertising campaign. The
new advertising campaign should be the *only significant change* between
the two periods.  AdEvaluator\u2122 also assumes that the probability
of the daily sales is independent and identically distributed during
each period.  This is not true in all cases.  Exercise your
professional business judgement whether the results of the simulations
are applicable to your business.

"""
    return disclaimer_text


def usage(cmd_str):
    """
    print usage message for program
    """
    if not isinstance(cmd_str, str):
        raise TypeError(debug_prefix() + 'cmd_str is type ' + str(type(cmd_str)))

    usage_text \
    = print_to_string("Usage:", cmd_str,
                      "    [input_file='" + str(INPUT_FILE) + "'] \n"
                      "    [-i input_file='" + str(INPUT_FILE) + "'] \n"
                      "    [-gui] run Graphical User Interface (GUI)\n"
                      "    [-no_settings] DO NOT load settings -- clean start\n"
                      "    [-reset | -reset_settings] reset settings and save\n"
                      "    [-block] block at each figure\n"
                      "    [-layers | -l] make layered plots for slide animation\n"
                      "    [-d detail_level='"
                      + str(_settings.detail_level) + "']\n"
                      "    [-o output_folder='" + str(OUTPUT_FOLDER) + "']\n"
                      "    [-adv_date advertising_start_date="
                      + ADV_START_DATE + "]\n"
                      "    [-e annual_advertising_expense="
                      + str(ANNUAL_ADV_EXPENSE) + "] \n    [-s random_number_seed="
                      + str(SEED_VAL) + "] \n    [-n number_of_simulations="
                      + str(NSIMS_DEFAULT) + "] \n"
                      "    [-pause <plot_duration_seconds>]\n"
                      "    [-price <unit_price>]\n"
                      "    [-cost <unit_cost>]\n"
                      "    [-date_tag <date_column_name>]\n"
                      "    [-amount_tag <amount_column_name>]\n"
                      "    [-sales_type_tag <sales_type_column_name>]\n"
                      "    [-sales_type_value <sales_sales_type_value_for_evaluation>]\n"
                      "    [-license] print full GPL version 3 license\n"
                      "    [-short_notice] print short startup notice\n"
                      "    [-disclaimer] print legal disclaimer\n"
                      "    [-glossary]  print glossary of technical terms\n"
                      "    [-h | -help | --help]  print this help message\n"
                      "    [-v | -version | --version] project version number\n")
    usage_text += print_to_string("   --- Evaluate the effectiveness "
                                  "of advertising " \
                                  + "from a sales report")
    usage_text += print_to_string("   --- assumes sales report divided "
                                  "into two periods with ")
    usage_text += print_to_string("   --- either no or current advertising "
                                  "in the first period")
    usage_text += print_to_string("   --- and new advertising at a "
                                  "constant rate during " \
                                  + "the second period")
    usage_text += print_to_string("   --- assumes a SINGLE product or "
                                  "service (a 'widget') " \
                                  + "with a CONSTANT")
    usage_text += print_to_string("   --- UNIT PRICE during both periods "
                                  "-- NO PRICE CHANGE")
    usage_text += print_to_string("   ---")
    usage_text += print_to_string("   --- use -adv_date <date> to set the "
                                  "date when the new " \
                                  + "advertising starts")
    usage_text += print_to_string("\n")
    usage_text += print_to_string("Examples: " + cmd_str + " -i sales.csv \n")
    usage_text += print_to_string("          "
                                  + cmd_str
                                  + " -i sales_renamed.csv "
                                  + "-date_tag mydate -sales_type_tag sales_type "
                                  + "-sales_type_value Invoice\n")
    usage_text += print_to_string("\n")

    usage_text \
        += print_to_string("""Copyright (C) 2018 by John F. McGowan, Ph.D. """ +
                           """(ceo@mathematical-software.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
""")
    usage_text += "\nProgram Version: " + PROJECT_VERSION
    usage_text += print_to_string("\n")
    return usage_text
    # end usage(cmd_str)

def startup_notice(program_name):
    """
    Brief copyright startup notice
    """
    if not isinstance(program_name, str):
        raise TypeError(debug_prefix() + "program_name is type " + str(type(program_name)))

    if not program_name:
        raise ValueError(debug_prefix() + "program_name is empty string")

    msg = print_to_string(program_name + \
          """ Copyright (C) 2018  John F. McGowan, Ph.D.
E-Mail: ceo@mathematical-software.com

This program comes with ABSOLUTELY NO WARRANTY; for details use -license option
This is free software, and you are welcome to redistribute it
under certain conditions; use -license option for details.""")
    return msg

def gpl_v3_license():
    """
    display the full GNU General Public License Version 3
    """
    license_text = '''
AdEvaluator\u2122 advertising evaluation software is made available subject to
the terms of the GNU General Public License Version 3.0 (full text below).

AdEvaluator\u2122 Copyright (C) 2018 by John F. McGowan, Ph.D.
E-Mail: ceo@mathematical-software.com

                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.

                       TERMS AND CONDITIONS

  0. Definitions.

  "This License" refers to version 3 of the GNU General Public License.

  "Copyright" also means copyright-like laws that apply to other kinds of
works, such as semiconductor masks.

  "The Program" refers to any copyrightable work licensed under this
License.  Each licensee is addressed as "you".  "Licensees" and
"recipients" may be individuals or organizations.

  To "modify" a work means to copy from or adapt all or part of the work
in a fashion requiring copyright permission, other than the making of an
exact copy.  The resulting work is called a "modified version" of the
earlier work or a work "based on" the earlier work.

  A "covered work" means either the unmodified Program or a work based
on the Program.

  To "propagate" a work means to do anything with it that, without
permission, would make you directly or secondarily liable for
infringement under applicable copyright law, except executing it on a
computer or modifying a private copy.  Propagation includes copying,
distribution (with or without modification), making available to the
public, and in some countries other activities as well.

  To "convey" a work means any kind of propagation that enables other
parties to make or receive copies.  Mere interaction with a user through
a computer network, with no transfer of a copy, is not conveying.

  An interactive user interface displays "Appropriate Legal Notices"
to the extent that it includes a convenient and prominently visible
feature that (1) displays an appropriate copyright notice, and (2)
tells the user that there is no warranty for the work (except to the
extent that warranties are provided), that licensees may convey the
work under this License, and how to view a copy of this License.  If
the interface presents a list of user commands or options, such as a
menu, a prominent item in the list meets this criterion.

  1. Source Code.

  The "source code" for a work means the preferred form of the work
for making modifications to it.  "Object code" means any non-source
form of a work.

  A "Standard Interface" means an interface that either is an official
standard defined by a recognized standards body, or, in the case of
interfaces specified for a particular programming language, one that
is widely used among developers working in that language.

  The "System Libraries" of an executable work include anything, other
than the work as a whole, that (a) is included in the normal form of
packaging a Major Component, but which is not part of that Major
Component, and (b) serves only to enable use of the work with that
Major Component, or to implement a Standard Interface for which an
implementation is available to the public in source code form.  A
"Major Component", in this context, means a major essential component
(kernel, window system, and so on) of the specific operating system
(if any) on which the executable work runs, or a compiler used to
produce the work, or an object code interpreter used to run it.

  The "Corresponding Source" for a work in object code form means all
the source code needed to generate, install, and (for an executable
work) run the object code and to modify the work, including scripts to
control those activities.  However, it does not include the work's
System Libraries, or general-purpose tools or generally available free
programs which are used unmodified in performing those activities but
which are not part of the work.  For example, Corresponding Source
includes interface definition files associated with source files for
the work, and the source code for shared libraries and dynamically
linked subprograms that the work is specifically designed to require,
such as by intimate data communication or control flow between those
subprograms and other parts of the work.

  The Corresponding Source need not include anything that users
can regenerate automatically from other parts of the Corresponding
Source.

  The Corresponding Source for a work in source code form is that
same work.

  2. Basic Permissions.

  All rights granted under this License are granted for the term of
copyright on the Program, and are irrevocable provided the stated
conditions are met.  This License explicitly affirms your unlimited
permission to run the unmodified Program.  The output from running a
covered work is covered by this License only if the output, given its
content, constitutes a covered work.  This License acknowledges your
rights of fair use or other equivalent, as provided by copyright law.

  You may make, run and propagate covered works that you do not
convey, without conditions so long as your license otherwise remains
in force.  You may convey covered works to others for the sole purpose
of having them make modifications exclusively for you, or provide you
with facilities for running those works, provided that you comply with
the terms of this License in conveying all material for which you do
not control copyright.  Those thus making or running the covered works
for you must do so exclusively on your behalf, under your direction
and control, on terms that prohibit them from making any copies of
your copyrighted material outside their relationship with you.

  Conveying under any other circumstances is permitted solely under
the conditions stated below.  Sublicensing is not allowed; section 10
makes it unnecessary.

  3. Protecting Users' Legal Rights From Anti-Circumvention Law.

  No covered work shall be deemed part of an effective technological
measure under any applicable law fulfilling obligations under article
11 of the WIPO copyright treaty adopted on 20 December 1996, or
similar laws prohibiting or restricting circumvention of such
measures.

  When you convey a covered work, you waive any legal power to forbid
circumvention of technological measures to the extent such circumvention
is effected by exercising rights under this License with respect to
the covered work, and you disclaim any intention to limit operation or
modification of the work as a means of enforcing, against the work's
users, your or third parties' legal rights to forbid circumvention of
technological measures.

  4. Conveying Verbatim Copies.

  You may convey verbatim copies of the Program's source code as you
receive it, in any medium, provided that you conspicuously and
appropriately publish on each copy an appropriate copyright notice;
keep intact all notices stating that this License and any
non-permissive terms added in accord with section 7 apply to the code;
keep intact all notices of the absence of any warranty; and give all
recipients a copy of this License along with the Program.

  You may charge any price or no price for each copy that you convey,
and you may offer support or warranty protection for a fee.

  5. Conveying Modified Source Versions.

  You may convey a work based on the Program, or the modifications to
produce it from the Program, in the form of source code under the
terms of section 4, provided that you also meet all of these conditions:

    a) The work must carry prominent notices stating that you modified
    it, and giving a relevant date.

    b) The work must carry prominent notices stating that it is
    released under this License and any conditions added under section
    7.  This requirement modifies the requirement in section 4 to
    "keep intact all notices".

    c) You must license the entire work, as a whole, under this
    License to anyone who comes into possession of a copy.  This
    License will therefore apply, along with any applicable section 7
    additional terms, to the whole of the work, and all its parts,
    regardless of how they are packaged.  This License gives no
    permission to license the work in any other way, but it does not
    invalidate such permission if you have separately received it.

    d) If the work has interactive user interfaces, each must display
    Appropriate Legal Notices; however, if the Program has interactive
    interfaces that do not display Appropriate Legal Notices, your
    work need not make them do so.

  A compilation of a covered work with other separate and independent
works, which are not by their nature extensions of the covered work,
and which are not combined with it such as to form a larger program,
in or on a volume of a storage or distribution medium, is called an
"aggregate" if the compilation and its resulting copyright are not
used to limit the access or legal rights of the compilation's users
beyond what the individual works permit.  Inclusion of a covered work
in an aggregate does not cause this License to apply to the other
parts of the aggregate.

  6. Conveying Non-Source Forms.

  You may convey a covered work in object code form under the terms
of sections 4 and 5, provided that you also convey the
machine-readable Corresponding Source under the terms of this License,
in one of these ways:

    a) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by the
    Corresponding Source fixed on a durable physical medium
    customarily used for software interchange.

    b) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by a
    written offer, valid for at least three years and valid for as
    long as you offer spare parts or customer support for that product
    model, to give anyone who possesses the object code either (1) a
    copy of the Corresponding Source for all the software in the
    product that is covered by this License, on a durable physical
    medium customarily used for software interchange, for a price no
    more than your reasonable cost of physically performing this
    conveying of source, or (2) access to copy the
    Corresponding Source from a network server at no charge.

    c) Convey individual copies of the object code with a copy of the
    written offer to provide the Corresponding Source.  This
    alternative is allowed only occasionally and noncommercially, and
    only if you received the object code with such an offer, in accord
    with subsection 6b.

    d) Convey the object code by offering access from a designated
    place (gratis or for a charge), and offer equivalent access to the
    Corresponding Source in the same way through the same place at no
    further charge.  You need not require recipients to copy the
    Corresponding Source along with the object code.  If the place to
    copy the object code is a network server, the Corresponding Source
    may be on a different server (operated by you or a third party)
    that supports equivalent copying facilities, provided you maintain
    clear directions next to the object code saying where to find the
    Corresponding Source.  Regardless of what server hosts the
    Corresponding Source, you remain obligated to ensure that it is
    available for as long as needed to satisfy these requirements.

    e) Convey the object code using peer-to-peer transmission, provided
    you inform other peers where the object code and Corresponding
    Source of the work are being offered to the general public at no
    charge under subsection 6d.

  A separable portion of the object code, whose source code is excluded
from the Corresponding Source as a System Library, need not be
included in conveying the object code work.

  A "User Product" is either (1) a "consumer product", which means any
tangible personal property which is normally used for personal, family,
or household purposes, or (2) anything designed or sold for incorporation
into a dwelling.  In determining whether a product is a consumer product,
doubtful cases shall be resolved in favor of coverage.  For a particular
product received by a particular user, "normally used" refers to a
typical or common use of that class of product, regardless of the status
of the particular user or of the way in which the particular user
actually uses, or expects or is expected to use, the product.  A product
is a consumer product regardless of whether the product has substantial
commercial, industrial or non-consumer uses, unless such uses represent
the only significant mode of use of the product.

  "Installation Information" for a User Product means any methods,
procedures, authorization keys, or other information required to install
and execute modified versions of a covered work in that User Product from
a modified version of its Corresponding Source.  The information must
suffice to ensure that the continued functioning of the modified object
code is in no case prevented or interfered with solely because
modification has been made.

  If you convey an object code work under this section in, or with, or
specifically for use in, a User Product, and the conveying occurs as
part of a transaction in which the right of possession and use of the
User Product is transferred to the recipient in perpetuity or for a
fixed term (regardless of how the transaction is characterized), the
Corresponding Source conveyed under this section must be accompanied
by the Installation Information.  But this requirement does not apply
if neither you nor any third party retains the ability to install
modified object code on the User Product (for example, the work has
been installed in ROM).

  The requirement to provide Installation Information does not include a
requirement to continue to provide support service, warranty, or updates
for a work that has been modified or installed by the recipient, or for
the User Product in which it has been modified or installed.  Access to a
network may be denied when the modification itself materially and
adversely affects the operation of the network or violates the rules and
protocols for communication across the network.

  Corresponding Source conveyed, and Installation Information provided,
in accord with this section must be in a format that is publicly
documented (and with an implementation available to the public in
source code form), and must require no special password or key for
unpacking, reading or copying.

  7. Additional Terms.

  "Additional permissions" are terms that supplement the terms of this
License by making exceptions from one or more of its conditions.
Additional permissions that are applicable to the entire Program shall
be treated as though they were included in this License, to the extent
that they are valid under applicable law.  If additional permissions
apply only to part of the Program, that part may be used separately
under those permissions, but the entire Program remains governed by
this License without regard to the additional permissions.

  When you convey a copy of a covered work, you may at your option
remove any additional permissions from that copy, or from any part of
it.  (Additional permissions may be written to require their own
removal in certain cases when you modify the work.)  You may place
additional permissions on material, added by you to a covered work,
for which you have or can give appropriate copyright permission.

  Notwithstanding any other provision of this License, for material you
add to a covered work, you may (if authorized by the copyright holders of
that material) supplement the terms of this License with terms:

    a) Disclaiming warranty or limiting liability differently from the
    terms of sections 15 and 16 of this License; or

    b) Requiring preservation of specified reasonable legal notices or
    author attributions in that material or in the Appropriate Legal
    Notices displayed by works containing it; or

    c) Prohibiting misrepresentation of the origin of that material, or
    requiring that modified versions of such material be marked in
    reasonable ways as different from the original version; or

    d) Limiting the use for publicity purposes of names of licensors or
    authors of the material; or

    e) Declining to grant rights under trademark law for use of some
    trade names, trademarks, or service marks; or

    f) Requiring indemnification of licensors and authors of that
    material by anyone who conveys the material (or modified versions of
    it) with contractual assumptions of liability to the recipient, for
    any liability that these contractual assumptions directly impose on
    those licensors and authors.

  All other non-permissive additional terms are considered "further
restrictions" within the meaning of section 10.  If the Program as you
received it, or any part of it, contains a notice stating that it is
governed by this License along with a term that is a further
restriction, you may remove that term.  If a license document contains
a further restriction but permits relicensing or conveying under this
License, you may add to a covered work material governed by the terms
of that license document, provided that the further restriction does
not survive such relicensing or conveying.

  If you add terms to a covered work in accord with this section, you
must place, in the relevant source files, a statement of the
additional terms that apply to those files, or a notice indicating
where to find the applicable terms.

  Additional terms, permissive or non-permissive, may be stated in the
form of a separately written license, or stated as exceptions;
the above requirements apply either way.

  8. Termination.

  You may not propagate or modify a covered work except as expressly
provided under this License.  Any attempt otherwise to propagate or
modify it is void, and will automatically terminate your rights under
this License (including any patent licenses granted under the third
paragraph of section 11).

  However, if you cease all violation of this License, then your
license from a particular copyright holder is reinstated (a)
provisionally, unless and until the copyright holder explicitly and
finally terminates your license, and (b) permanently, if the copyright
holder fails to notify you of the violation by some reasonable means
prior to 60 days after the cessation.

  Moreover, your license from a particular copyright holder is
reinstated permanently if the copyright holder notifies you of the
violation by some reasonable means, this is the first time you have
received notice of violation of this License (for any work) from that
copyright holder, and you cure the violation prior to 30 days after
your receipt of the notice.

  Termination of your rights under this section does not terminate the
licenses of parties who have received copies or rights from you under
this License.  If your rights have been terminated and not permanently
reinstated, you do not qualify to receive new licenses for the same
material under section 10.

  9. Acceptance Not Required for Having Copies.

  You are not required to accept this License in order to receive or
run a copy of the Program.  Ancillary propagation of a covered work
occurring solely as a consequence of using peer-to-peer transmission
to receive a copy likewise does not require acceptance.  However,
nothing other than this License grants you permission to propagate or
modify any covered work.  These actions infringe copyright if you do
not accept this License.  Therefore, by modifying or propagating a
covered work, you indicate your acceptance of this License to do so.

  10. Automatic Licensing of Downstream Recipients.

  Each time you convey a covered work, the recipient automatically
receives a license from the original licensors, to run, modify and
propagate that work, subject to this License.  You are not responsible
for enforcing compliance by third parties with this License.

  An "entity transaction" is a transaction transferring control of an
organization, or substantially all assets of one, or subdividing an
organization, or merging organizations.  If propagation of a covered
work results from an entity transaction, each party to that
transaction who receives a copy of the work also receives whatever
licenses to the work the party's predecessor in interest had or could
give under the previous paragraph, plus a right to possession of the
Corresponding Source of the work from the predecessor in interest, if
the predecessor has it or can get it with reasonable efforts.

  You may not impose any further restrictions on the exercise of the
rights granted or affirmed under this License.  For example, you may
not impose a license fee, royalty, or other charge for exercise of
rights granted under this License, and you may not initiate litigation
(including a cross-claim or counterclaim in a lawsuit) alleging that
any patent claim is infringed by making, using, selling, offering for
sale, or importing the Program or any portion of it.

  11. Patents.

  A "contributor" is a copyright holder who authorizes use under this
License of the Program or a work on which the Program is based.  The
work thus licensed is called the contributor's "contributor version".

  A contributor's "essential patent claims" are all patent claims
owned or controlled by the contributor, whether already acquired or
hereafter acquired, that would be infringed by some manner, permitted
by this License, of making, using, or selling its contributor version,
but do not include claims that would be infringed only as a
consequence of further modification of the contributor version.  For
purposes of this definition, "control" includes the right to grant
patent sublicenses in a manner consistent with the requirements of
this License.

  Each contributor grants you a non-exclusive, worldwide, royalty-free
patent license under the contributor's essential patent claims, to
make, use, sell, offer for sale, import and otherwise run, modify and
propagate the contents of its contributor version.

  In the following three paragraphs, a "patent license" is any express
agreement or commitment, however denominated, not to enforce a patent
(such as an express permission to practice a patent or covenant not to
sue for patent infringement).  To "grant" such a patent license to a
party means to make such an agreement or commitment not to enforce a
patent against the party.

  If you convey a covered work, knowingly relying on a patent license,
and the Corresponding Source of the work is not available for anyone
to copy, free of charge and under the terms of this License, through a
publicly available network server or other readily accessible means,
then you must either (1) cause the Corresponding Source to be so
available, or (2) arrange to deprive yourself of the benefit of the
patent license for this particular work, or (3) arrange, in a manner
consistent with the requirements of this License, to extend the patent
license to downstream recipients.  "Knowingly relying" means you have
actual knowledge that, but for the patent license, your conveying the
covered work in a country, or your recipient's use of the covered work
in a country, would infringe one or more identifiable patents in that
country that you have reason to believe are valid.

  If, pursuant to or in connection with a single transaction or
arrangement, you convey, or propagate by procuring conveyance of, a
covered work, and grant a patent license to some of the parties
receiving the covered work authorizing them to use, propagate, modify
or convey a specific copy of the covered work, then the patent license
you grant is automatically extended to all recipients of the covered
work and works based on it.

  A patent license is "discriminatory" if it does not include within
the scope of its coverage, prohibits the exercise of, or is
conditioned on the non-exercise of one or more of the rights that are
specifically granted under this License.  You may not convey a covered
work if you are a party to an arrangement with a third party that is
in the business of distributing software, under which you make payment
to the third party based on the extent of your activity of conveying
the work, and under which the third party grants, to any of the
parties who would receive the covered work from you, a discriminatory
patent license (a) in connection with copies of the covered work
conveyed by you (or copies made from those copies), or (b) primarily
for and in connection with specific products or compilations that
contain the covered work, unless you entered into that arrangement,
or that patent license was granted, prior to 28 March 2007.

  Nothing in this License shall be construed as excluding or limiting
any implied license or other defenses to infringement that may
otherwise be available to you under applicable patent law.

  12. No Surrender of Others' Freedom.

  If conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot convey a
covered work so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you may
not convey it at all.  For example, if you agree to terms that obligate you
to collect a royalty for further conveying from those to whom you convey
the Program, the only way you could satisfy both those terms and this
License would be to refrain entirely from conveying the Program.

  13. Use with the GNU Affero General Public License.

  Notwithstanding any other provision of this License, you have
permission to link or combine any covered work with a work licensed
under version 3 of the GNU Affero General Public License into a single
combined work, and to convey the resulting work.  The terms of this
License will continue to apply to the part which is the covered work,
but the special requirements of the GNU Affero General Public License,
section 13, concerning interaction through a network will apply to the
combination as such.

  14. Revised Versions of this License.

  The Free Software Foundation may publish revised and/or new versions of
the GNU General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

  Each version is given a distinguishing version number.  If the
Program specifies that a certain numbered version of the GNU General
Public License "or any later version" applies to it, you have the
option of following the terms and conditions either of that numbered
version or of any later version published by the Free Software
Foundation.  If the Program does not specify a version number of the
GNU General Public License, you may choose any version ever published
by the Free Software Foundation.

  If the Program specifies that a proxy can decide which future
versions of the GNU General Public License can be used, that proxy's
public statement of acceptance of a version permanently authorizes you
to choose that version for the Program.

  Later license versions may give you additional or different
permissions.  However, no additional obligations are imposed on any
author or copyright holder as a result of your choosing to follow a
later version.

  15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  16. Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES.

  17. Interpretation of Sections 15 and 16.

  If the disclaimer of warranty and limitation of liability provided
above cannot be given local legal effect according to their terms,
reviewing courts shall apply local law that most closely approximates
an absolute waiver of all civil liability in connection with the
Program, unless a warranty or assumption of liability accompanies a
copy of the Program in return for a fee.

                     END OF TERMS AND CONDITIONS
'''
    return license_text


def compute_loss(sales_bins, sales_edges, loss_level=0.0):
    """
    compute number of losses
    """

    if not isinstance(sales_bins, (list, tuple, np.ndarray)):
        raise TypeError(debug_prefix() + "sales_bins is type " + str(type(sales_bins)))

    if not isinstance(sales_edges, (list, tuple, np.ndarray)):
        raise TypeError(debug_prefix() + "sales_edges is type " + str(type(sales_edges)))

    if not isinstance(loss_level, (float, np.float)):
        raise TypeError(debug_prefix() + "loss_level is type " + str(type(loss_level)))

    n_loss_sales = 0.0
    for index, value in enumerate(sales_bins):
        if sales_edges[index+1] <= loss_level:
            n_loss_sales += value
        elif sales_edges[index] <= loss_level:
            fraction = (-sales_edges[index]) / \
                       (sales_edges[index+1] - sales_edges[index])
            n_loss_sales += fraction*value
    return n_loss_sales  # compute_loss(...)

def currency(x, pos):
    'Function for formatting currency values on axis of plots'
    if abs(x) >= 1000000:
        return '${:1.1f}M'.format(x*1e-6)
    elif abs(x) < 1000:
        return '${:,.0f}'.format(x)

    return '${:1.0f}K'.format(x*1e-3)

def poisson_curve(input_data, *p):
    """
    Poisson statistics

    ARGUMENTS: input_data -- number of events
               *p -- parameters (poisson lambda)

    RETURNS: probability density function value

    """
    if not isinstance(input_data, np.ndarray):
        raise TypeError(debug_prefix() + "input_data is type " + str(type(input_data)))

    if not isinstance(p, (list, tuple, np.ndarray)):
        raise TypeError(debug_prefix() + "p is type " + str(type(p)))

    if len(p) != 1:
        raise ValueError(debug_prefix() + "p has " + str(len(p)) + " elements")

    # lambda is reserved keyword in Python
    poisson_parameter = p[0]

    return np.exp(-1.0*poisson_parameter) \
        * (poisson_parameter)**input_data \
        / factorial(input_data)

def bell_curve(input_data, *p):
    """
    Bell Curve/Normal/Gaussian model

    ARGUMENTS: input_data -- location data
               *p -- parameters

    RETURNS: probability density function value

    signature compatible with scipy.stats.curve_fit(...)
    """

    if not isinstance(input_data, np.ndarray):
        raise TypeError(debug_prefix() + "input_data is type " + str(type(input_data)))

    if not isinstance(p, (list, tuple, np.ndarray)):
        raise TypeError(debug_prefix() + "p is type " + str(type(p)))

    if not len(p) == 3:
        raise ValueError(debug_prefix() + "p has " + str(len(p)) + " elements (not three)")

    magnitude = p[0]
    location = p[1]  # mu
    scale = p[2]  # sigma/dispersion
    return magnitude \
        *(1.0/np.sqrt(2.0*np.pi))\
        *np.exp(-0.5* (input_data - location)**2/scale**2)

def print_to_string(*args, **kwargs):
    """
    emulate output of Python print
    into a Python string
    """
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents  # print_to_string(*args,...)

def gcd_array(array_1d):
    """
    compute greatest common denominator of a list
    """
    if not isinstance(array_1d, (tuple, list, np.ndarray)):
        raise TypeError(debug_prefix() + 'array_1d is type ' + str(type(array_1d)))

    if isinstance(array_1d, np.ndarray):
        array_iter = array_1d.ravel()
    else:
        array_iter = array_1d

    index = 1
    accum = array_iter[0]
    while index < len(array_iter):
        accum = gcd(accum, array_iter[index])
        index += 1
    return accum

def check_unit_price(unit_price):
    """
    check for probable problem with the inferred
    unit price -- for validating the
    price inference
    """

    if not isinstance(unit_price, (float, np.float)):
        raise TypeError(debug_prefix() + 'unit_price is type ' + str(type(unit_price)))

    if unit_price == 0.01:
        raise ValueError(debug_prefix() + "Inferred price is one cent ($0.01)!  \n"
                         "This usually means the sales amounts \nare not "
                         "multiples of a single price.  \nCheck if there "
                         "has been a price change, multiple product or "
                         "service types with \ndifferent prices in the "
                         "sames sales report, data entry errors, \n"
                         "or some other problem with the sales report data."
                         "  Use -price <price> option at the command line \n"
                         "or set the price in Run | Settings in the GUI to"
                         "manually set the unit price.")
    elif unit_price <= 0.0:
        raise ValueError(debug_prefix() + "ERROR: unit_price is "
                         + "{:,.2f}".format(unit_price) +
                         " (ZERO OR LESS THAN ZERO)")


def get_unit_prices(sales_data):
    """
    infer the unit prices from sales data

    ARGUMENT: sales_data -- sales date and amount

    RETURNS: list of probable prices

    sales amounts are integer multiples of the
    possible prices

    useful if sales report lacks prices
    """
    if isinstance(sales_data, (list, tuple)):
        amounts = np.array(sales_data)
    elif isinstance(sales_data, np.ndarray):
        if sales_data.ndim == 1:
            amounts = sales_data
        else:
            amounts = sales_data[:, 1]
    else:
        raise TypeError(debug_prefix() + 'sales_data type is ' \
                        + str(type(sales_data)))

    unique_amounts = np.unique(amounts[amounts > 0.0])
    unique_amounts_cents = (100.0*unique_amounts).astype(np.int)
    unit_prices = [float(gcd_array(unique_amounts_cents)/100)]
    return unit_prices


def get_units(sales_data, unit_price=None):
    """
    convert to sales amounts to number of units

    ARGUMENT: sales_data -- sales dates and amounts
    """

    if not isinstance(sales_data, np.ndarray):
        raise TypeError(debug_prefix() + "sales_data is type " + str(type(sales_data)))

    if unit_price is None:
        unit_prices = get_unit_prices(sales_data)
        price = unit_prices[0]
        check_unit_price(price)
    else:
        if isinstance(unit_price, (float, np.float)):
            price = unit_price
        else:
            raise TypeError(debug_prefix() + "unit_price is type " + str(type(unit_price)))

    return (sales_data/price).astype(int)

def get_dist(sales_data, unit_price=None):
    """
    get empirical distribution for daily sales

    ARGUMENT: sales_data -- sales dates and amounts

    """

    if unit_price is None:
        unit_prices = get_unit_prices(sales_data)
        unit_price = unit_prices[0]
        check_unit_price(unit_price)
    elif not isinstance(unit_price, (float, np.float)):
        raise TypeError(debug_prefix() + 'unit_price is type ' + str(type(unit_price)))
    else:
        pass

    unit_sales = get_units(sales_data, unit_price)
    number_of_days = unit_sales.size
    histogram = np.zeros(np.max(unit_sales)+1)
    #
    # counting number of days with so many units
    # sold
    #
    for units_sold in unit_sales:
        histogram[int(units_sold)] += 1.0
    # unit_sales.size should be number of days in period
    # not total number of units sold
    # return empirical distribution and errors on the same
    return histogram/number_of_days, np.sqrt(histogram)/number_of_days

def vary_distribution(dist_cumsum, dist_error):
    """
    vary the distribution estimate for simulations

    ARGUMENTS: dist_cumsum -- empirical cumulative
                              distribution function (cdf)
               dist_error -- error on empirical probability
                             distribution function (pdf)
    """

    if isinstance(dist_cumsum, (list, tuple)):
        dist_cumsum = np.array(dist_cumsum)

    if isinstance(dist_error, (list, tuple)):
        dist_error = np.array(dist_error)

    if not isinstance(dist_cumsum, np.ndarray):
        raise TypeError(debug_prefix() + 'dist_cumsum is type ' + str(type(dist_cumsum)))

    if not isinstance(dist_error, np.ndarray):
        raise TypeError(debug_prefix() + 'dist_error is type ' + str(type(dist_error)))

    # infer pdf values
    prefix = np.array((0.0,))
    dist_pdf = (dist_cumsum[1:] - dist_cumsum[:-1])
    dist_pdf = np.concatenate((prefix, dist_pdf))
    new_dist_pdf = dist_pdf \
                   + dist_error \
                   * np.random.standard_normal(dist_pdf.size)

    # normalize the new empirical distribution
    new_dist_pdf = new_dist_pdf / new_dist_pdf.sum()
    return new_dist_pdf.cumsum()


def sim_unit_sales(dist_cumsum, size=None):
    """
    simulate unit sales based on empirical distribution

    ARGUMENTS: dist_cumsum -- cumulative sum of empirical distribution
               size -- shape of output number of units sold array

    RETURNS: number of units sold
             OR array of number of units sold
    """

    if not isinstance(dist_cumsum, (list, tuple, np.ndarray)):
        raise TypeError(debug_prefix() + "dist_cumsum is type " + str(type(dist_cumsum)))

    if size is None:
        rval = np.random.uniform()  # number from 0.0 to 1.0
        nsold = np.argmax(dist_cumsum > rval)
        return nsold
    elif isinstance(size, (tuple, list, np.ndarray)):
        result = np.zeros(size)
        rval = np.random.uniform(size=size)
        for index, value in enumerate(rval.ravel()):
            result.ravel()[index] = np.argmax(dist_cumsum > value)
        return result  # array of simulated sales
    else:
        raise TypeError(debug_prefix() + "size is type " + str(type(size)))


def compute_daily_sales(sorted_data_frame,
                        date_tag=None,
                        amount_tag=None,
                        sales_type_tag=None,
                        sales_type_value=None):
    """
    compute the daily sales, sub total of sales amounts
    for each day

    ARGUMENT: sorted_data_frame -- sales report data frame
              sort by date in ascending order

    RETURNS: array of daily sales with 0.0 entries for zero
             sales days ("zero days")
    """

    if not isinstance(sorted_data_frame, pd.DataFrame):
        raise TypeError(debug_prefix()
                        + "sorted_data_frame is type "
                        + str(type(sorted_data_frame)))

    if not isinstance(date_tag, (type(None), str)):
        raise TypeError(debug_prefix()
                        + "date_tag is type "
                        + str(type(date_tag)))

    if not isinstance(amount_tag, (type(None), str)):
        raise TypeError(debug_prefix()
                        + "amount_tag is type "
                        + str(type(amount_tag)))

    if not isinstance(sales_type_tag, (type(None), str)):
        raise TypeError(debug_prefix()
                        + "sales_type_tag is type "
                        + str(type(sales_type_tag)))

    if not isinstance(sales_type_value, (type(None), str)):
        raise TypeError(debug_prefix()
                        + "sales_type_value is type "
                        + str(type(sales_type_value)))

    date_tag, date_index = get_date_refs(sorted_data_frame, date_tag)
    sales_type_tag, type_index = get_type_refs(sorted_data_frame, sales_type_tag)
    amount_tag, amount_index = get_amount_refs(sorted_data_frame, amount_tag)

    if isinstance(sales_type_value, str) \
       and not sales_type_value == '':
        # use type value from Settings
        # (override automatic type value inference)
        sales_type_value_str = sales_type_value
    else:
        # automatic sales type value inference
        new_sales_type_value = get_sales_type_value(sorted_data_frame,
                                                    sales_type_tag)
        if not new_sales_type_value is None:
            sales_type_value_str = new_sales_type_value
        else:
            sales_type_value_str = 'Sales Receipt' # default guess

    # compute the daily sales with zero days
    # interpolated
    daily_sales = []
    day = []
    day_count = 0
    for index, record in enumerate(sorted_data_frame.values):
        if index == 0:
            old_date = record[date_index]
            daily_sum = 0.0

        if isinstance(sales_type_tag, str):
            # type if from QuickBooks
            # which has Invoice, Sales Receipt, and Payment types
            if record[type_index] != sales_type_value_str:
                continue  # skip this record

        current_date = record[date_index]
        # make sures sales amount is float (dollars)
        sales_amount = float(record[amount_index])

        if current_date != old_date:
            daily_sales.append([old_date, daily_sum])
            day.append(day_count)
            day_count += 1
            daily_sum = 0.0
            diff_date = current_date - old_date
            #        print("diff_date")
            #        print(diff_date)
            if diff_date.days > 1:
                # add zero sales days
                for day_index in range(diff_date.days-1):
                    zero_date = old_date + datetime.timedelta(days=1)
                    daily_sales.append([zero_date, 0.0])
                    day_count += 1
                    day.append(day_count)
                    old_date = zero_date
            old_date = current_date
        else:
            daily_sum += sales_amount

    if len(daily_sales) == 0:
        # skipped all records in the sales record file
        raise ValueError(debug_prefix()
                         + "computed daily sales is empty.  "
                         "\nSales Column Header is " + sales_type_tag
                         + "\nSales Type Value is " + sales_type_value +
                         "\n\nCheck if the sales data file is empty or "
                         "the Sales Type column values "
                         "are not 'Sales Receipt' "
                         "\nand set the Sales Type Value in the Settings Dialog "
                         "to the appropriate value from the sales data file.")

    daily_sales_np = np.array(daily_sales)
    day_np = np.array(day)

    return day_np, daily_sales_np

def get_date_refs(data_frame, date_tag=None):
    """
    get date tag and index

    figures out date column name/index from
    data frame

    ARGUMENT: Pandas DataFrame with sales report

    RETURNS: date_tag, date_index
    """

    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError(debug_prefix() + 'data_frame is type ' \
                        + str(type(data_frame)))
    if date_tag is None \
       or date_tag == DATE_HEADER_DEFAULT:
        if 'DATE' in data_frame.columns:
            data_frame['DATE'] = pd.to_datetime(data_frame.DATE)
            date_tag = 'DATE'
        elif 'Date' in data_frame.columns:
            data_frame['Date'] = pd.to_datetime(data_frame.Date)
            date_tag = 'Date'
        else:
            raise ValueError(debug_prefix() + "Unable to find dates in sales data.  "
                             "Try option -date_tag <date column name>"
                             " or set date column name in GUI Settings Dialog")
    else:
        if date_tag in data_frame.columns:
            data_frame[date_tag] = pd.to_datetime(data_frame[date_tag])
        else:
            raise ValueError(debug_prefix() + "Unable to find date column "
                             + str(date_tag)
                             + "in sales data."
                             "Try option -date_tag <date column name>"
                             " or set date column name in GUI Settings Dialog")

    # get column index of date
    date_index = data_frame.columns.get_loc(date_tag)

    return date_tag, date_index  # get_date_refs(data_frame)

def get_type_refs(data_frame, sales_type_tag=None):
    """
    get Type column references

    figures out sale type column name and index
    from data frame

    ARGUMENT: data_frame -- Pandas data frame with sales report

    RETURNS: sales_type_tag, type_index -- name and column index
    for sales type
    """
    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError(debug_prefix() + 'data_frame is type ' \
                        + str(type(data_frame)))

    if sales_type_tag is None \
       or sales_type_tag == SALES_TYPE_HEADER_DEFAULT:
        # locate type of sale/transaction
        # QuickBooks uses "Sales Receipt", "Invoice", "Payment"
        if 'Type' in data_frame.columns:
            sales_type_tag = 'Type'
            type_index = data_frame.columns.get_loc(sales_type_tag)
        else:
            sales_type_tag = None
            type_index = None
    else:
        if sales_type_tag in data_frame.columns:
            type_index = data_frame.columns.get_loc(sales_type_tag)
        else:
            print("Unable to find type column ",
                  sales_type_tag, " in sales report")
            sales_type_tag = None
            type_index = None

    return sales_type_tag, type_index  # get_type_refs(data_frame)

def get_sales_type_value(data_frame, sales_type_tag=None):
    """
    get the best candidate for the sales type value
    e.g. Payment, Invoice, Sales Receipt etc.
    """

    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError(debug_prefix()
                        + "data_frame is type "
                        + str(type(data_frame)))

    if not isinstance(sales_type_tag, (str, type(None))):
        raise TypeError(debug_prefix()
                        + "sales_type_tag is type "
                        + str(type(sales_type_tag)))

    sales_type_value = None

    if sales_type_tag in data_frame.columns:
        sales_type_index = data_frame.columns.get_loc(sales_type_tag)
        sales_type_values = data_frame.values[:, sales_type_index]
        sales_type_unique_values = np.unique(sales_type_values)
        for vindex, value in enumerate(sales_type_unique_values):
            value_upper = value.upper()
            if value_upper == "SALES RECEIPT":
                sales_type_value = value
                break
            elif value_upper == "PAYMENT":
                sales_type_value = value
                break
            elif value_upper == "INVOICE":
                sales_type_value = value
                break
            else:
                pass

    return sales_type_value  # get_sales_type_value(...)

def get_amount_refs(data_frame, amount_tag=None):
    """
    get references to amount column

    figures out sales amount column name and index
    from data frame

    ARGUMENT: data_frame -- Pandas data frame with sales report

    RETURNS: amount_tag, amount_index -- name and column index
    for sales amount column in data_frame

    """
    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError(debug_prefix() + 'data_frame is type ' \
                        + str(type(data_frame)))

    if amount_tag is None \
       or amount_tag == AMOUNT_HEADER_DEFAULT:
        # locate amount of the sale
        if 'AMOUNT' in data_frame.columns:
            amount_tag = 'AMOUNT'
        elif 'Amount' in data_frame.columns:
            amount_tag = 'Amount'
        elif 'Total' in data_frame.columns:
            amount_tag = 'Total'
        elif 'TOTAL' in data_frame.columns:
            amount_tag = 'TOTAL'
        else:
            raise ValueError(debug_prefix()
                             + "Unable to find amount "
                             + str(amount_tag) + " in sales data.  "
                             + "Try option -amount_tag <amount column name>"
                             " or set amount column name in GUI Settings Dialog.")
    else:
        if amount_tag in data_frame.columns:
            pass
        else:
            raise ValueError(debug_prefix()
                             + "Unable to find the amount column header "
                             + str(amount_tag)
                             + " in sales report.  "
                             "Try option -amount_tag <amount column name>"
                             " or set amount column name in GUI Settings Dialog.")

    amount_index = data_frame.columns.get_loc(amount_tag)

    return amount_tag, amount_index  # get_amount_refs(data_frame)

def sim_adv_period(daily_sales_np,
                   dist_cumsum_no_adv,
                   mask_adv,
                   file_stem="sales_data",
                   unit_price=None,
                   number_sims=NSIMS_DEFAULT,
                   output_folder=OUTPUT_FOLDER,
                   plot_duration_secs=PLOT_DURATION_SECS):
    """

    simulate the advertising period, computes the welch's T
    statistic for comparing averages of each period, and plots
    a histogram of the welch's T statistics.  The histogram is
    an empirical probability distribution for the T statistic.

    ARGUMENTS: daily_sales_np -- daily sales in NumPy array
               dist_cumsum_no_adv -- empirical probability distribution
                                     of daily sales with no advertising
                                     fraction of days with n unit sales
               mask_adv -- true if advertising active on day
               file_stem -- from <file_stem>.csv with sales report
               number_sims -- number of simulations

    RETURNS: welch_t_edges, welch_t_bins -- histogram of
             Welch's t statistic from simulations

    WHY: simulating the Welch's T statistic using the empirical
    distribution of sales enables us to evaluate how accurate Welch's T
    test is.  Welch's T test assumes a Bell Curve distribution for both
    data sets being compared.  This is generally only approximately true
    for sales data.

    """

    # check arguments
    if not isinstance(daily_sales_np, np.ndarray):
        raise TypeError(debug_prefix() + 'daily_sales_np is type ' \
                        + str(type(daily_sales_np)))
    if not isinstance(dist_cumsum_no_adv, (list, tuple, np.ndarray)):
        raise TypeError(debug_prefix() + 'dist_cumsum_no_adv is type ' \
                        + str(type(dist_cumsum_no_adv)))
    if not isinstance(mask_adv, np.ndarray):
        raise TypeError(debug_prefix() + 'mask_adv is type ' \
                        + str(type(mask_adv)))
    if not isinstance(number_sims, (int, np.int)):
        raise TypeError(debug_prefix() + 'number_sims is type ' \
                        + str(type(number_sims)))

    # invert advertising mask
    mask_no_adv = ~mask_adv
    # simulate the advertising period

    print("simulating advertising period sales data using " \
          + "the empirical probability distribution with no adv...")
    thist = []
    pval_hist = []
    t_start = time.time()
    t_mark = t_start
    # infer the unit price
    if unit_price is None:
        unit_prices = get_unit_prices(daily_sales_np)
        print("inferred unit prices are:", unit_prices)
        unit_price = unit_prices[0]

    for sim_index in range(number_sims):
        sim_sales_adv = sim_unit_sales(dist_cumsum_no_adv, \
                                       daily_sales_np[mask_adv, 1].shape)
        sim_sales_adv *= unit_price

    # debug trace messages
    #    print("average daily sales (NO ADV):", sim_sales_adv.mean())
    #    print("std daily sales (NO ADV):", \
        #          sim_sales_adv.std()/np.sqrt(sim_sales_adv.size))

        diff = sim_sales_adv.mean() - daily_sales_np[mask_no_adv, 1].mean()

        scale = np.sqrt(sim_sales_adv.var()/sim_sales_adv.size \
                         + daily_sales_np[mask_no_adv, 1].var() \
                         /daily_sales_np[mask_no_adv, 1].size)

        my_zscore = diff

        # degrees of freedom for computing T statistic
        dof_1 = daily_sales_np[mask_no_adv, 1].size-1
        dof_2 = sim_sales_adv.size-1

        nu_denom = (sim_sales_adv.var()**2/(sim_sales_adv.size**2*dof_1) \
                    + daily_sales_np[mask_no_adv, 1].var()**2 \
                    /((daily_sales_np[mask_no_adv, 1].size)**2*dof_2))

        welch_nu = (sim_sales_adv.var()/sim_sales_adv.size \
                    + daily_sales_np[mask_no_adv, 1].var() \
                    /daily_sales_np[mask_no_adv, 1].size)**2 / nu_denom

        #welch_t = st.t.ppf(my_zscore, welch_nu)

        # compute Welch's t-statistic
        tstat, pvalue = st.ttest_ind(daily_sales_np[mask_no_adv, 1], \
                                     sim_sales_adv, \
                                     None, equal_var=False)
        # histogram Welch's t statistic and p-value
        # to get an empirical distribution for these values
        # for comparison to computed value for real data
        #
        thist.append(tstat)  # was tstat
        pval_hist.append(pvalue)
        now = time.time()
        # progress message
        if (now - t_mark) > 1:
            print(".", sep='', end='', flush=True)
            t_mark = now

    if _settings.detail_level > 1:
        # display histogram of Welch t-statistics
        # from simulations
        f_tstat = plt.figure(figsize=(12, 9))
        welch_t_bins, welch_t_edges, patches \
            = plt.hist(thist, bins=_settings.bins)
        plt.title("Welch's t statistic is a measure of the difference between the two periods")
        plt.xlabel("WELCH'S T STATISTIC (0.0 MEANS THE TWO PERIODS ARE VERY SIMILAR)")
        plt.ylabel('NUMBER OF SIMULATIONS')
#        x_low, x_hi = plt.xlim()
#        delta_x = x_hi - x_low
#        y_low, y_hi = plt.ylim()
#        delta_y = y_hi - y_low
#        plt.text(x_low + 0.025*delta_x,
#                 y_hi - 0.09*delta_y,
#                 "Welch's t statistic is a measure "
#                 "  of how similar the two periods are",
#                 bbox=dict(facecolor='white', alpha=0.5))
        if bool(_settings.block):
            plt.show()
        else:
            plt.ion()
            plt.show()
            # wait to display the figure
            plt.pause(plot_duration_secs)

        f_tstat.savefig(output_folder + os.sep
                        + file_stem + '_welch_t_stat_hist.jpg')

    else:
        welch_t_bins, welch_t_edges = np.histogram(thist,
                                                   bins=_settings.bins)

    if _settings.detail_level > 1:
        # display histogram of p-values from Welch t statistic
        # from simulations
        f_pval = plt.figure(figsize=(12, 9))
        welch_pval_bins, welch_pval_edges, patches \
            = plt.hist(pval_hist, bins=_settings.bins)
        plt.title("HISTOGRAM OF THE P-VALUE DERIVED FROM WELCH'S T STAT")
        plt.xlabel('P VALUE IS AN *ESTIMATE* OF THE PROBABILITY TWO PERIODS SAME')
        plt.ylabel('NUMBER OF SIMULATIONS')
        if bool(_settings.block):
            plt.show()
        else:
            plt.ion()
            plt.show()
            # wait to display the figure
            plt.pause(plot_duration_secs)

        f_pval.savefig(output_folder + os.sep
                       + file_stem + '_welch_p_value_hist.jpg')

    else:
        welch_pval_bins, \
        welch_pval_edges = np.histogram(pval_hist,
                                        bins=_settings.bins)

    return welch_t_bins, welch_t_edges  # sim_adv_period(...)

def fit_plot_bell_curve(welch_t_edges,
                        welch_t_bins,
                        file_stem='sales_data',
                        output_folder=OUTPUT_FOLDER,
                        plot_duration_secs=PLOT_DURATION_SECS):
    """
    fit a Bell Curve to the simulated Welch's T stastistic data
    and plot the simulated data vs the Bell Curve fit

    ARGUMENTS: welch_t_edges -- edges of bins of histogram
               welch_t_bins -- counts in each bin

    RETURNS: coeff_of_determination -- the coefficient of determination
                                       for the Bell Curve fit

    WHY: Welch's T test assumes a Bell Curve distribution for the
    two data sets compared, in our case the no advertising period and the
    advertising period.  The histogram and  Bell Curve fit shows how accurate
    this assumption is.  The assumption is only approximately true for most
    sales data.
    """

    if not isinstance(welch_t_edges, (list, tuple, np.ndarray)):
        raise TypeError(debug_prefix() + "welch_t_edges is type " + str(type(welch_t_edges)))

    if not isinstance(welch_t_bins, (list, tuple, np.ndarray)):
        raise TypeError(debug_prefix() + "welch_t_bins is type " + str(type(welch_t_bins)))

    if not isinstance(file_stem, str):
        raise TypeError(debug_prefix() + "file_stem is type " + str(type(file_stem)))

    if not isinstance(output_folder, str):
        raise TypeError(debug_prefix() + "output_folder is type " + str(type(output_folder)))

    if not isinstance(plot_duration_secs, (float, np.float)):
        raise TypeError(debug_prefix() + "plot_duration_secs is type "
                        + str(type(plot_duration_secs)))

    # fit Bell Curve to Welch t stat simulated data
    input_data = (welch_t_edges[:-1] + welch_t_edges[1:])/2.0

    y_data = welch_t_bins/welch_t_bins.sum()

    mag_start = np.sqrt(2.0*np.pi)*np.max(y_data)
    mu_start = input_data.dot(y_data)/y_data.sum()
    sigma_start = np.sqrt(((input_data - mu_start)**2).dot(y_data)/y_data.sum())
    p_start = [mag_start,
               mu_start,
               sigma_start]

    print("fitting Bell Curve to Welch's t statistic empirical distribution")
    popt, pcov = curve_fit(bell_curve, input_data, y_data, p_start)

    xline = np.linspace(np.min(input_data), np.max(input_data), 100)
    y_fit = bell_curve(input_data, *popt)
    residuals = y_data - y_fit

    # coefficient of determination is roughly the fraction
    # of the variance in the data explained by the model
    # 1.0 is a perfect model, 0.0 is a very bad model
    coeff_of_determination = 1.0 - residuals.var()/y_data.var()

    if _settings.detail_level > 1:
        f_fit = plt.figure(figsize=(12, 9))
        y_line = bell_curve(xline, *popt)
        plt.plot(input_data, y_data, 'gP', label='TSTAT DATA', \
                 linewidth=LINEWIDTH, markersize=MARKERSIZE)
        plt.plot(input_data, y_fit, 'ko', label='PREDICTED VALUES', \
                 linewidth=LINEWIDTH, markersize=MARKERSIZE)
        plt.plot(xline, y_line, 'b-', label='BELL CURVE FIT', \
                 linewidth=LINEWIDTH, markersize=MARKERSIZE)
        plt.xlabel("WELCH'S T STATISTIC VALUE "
                   "(A MEASURE OF THE DIFFERENCE BETWEEN THE TWO PERIODS)")
        plt.ylabel('FRACTION OF SIMULATIONS WITH THE T STAT VALUE')
        plt.title("FIT BELL CURVE TO THE WELCH'S T STATISTIC DISTRIBUTION (R**2=%3.2f)" \
                  % coeff_of_determination)
        plt.grid()
        plt.legend(loc='upper right')
        if bool(_settings.block):
            plt.show()
        else:
            plt.ion()
            plt.show()
            # wait to display the figure
            plt.pause(plot_duration_secs)

        f_fit.savefig(output_folder + os.sep
                      + file_stem + "_bell_curve_fit.jpg")

    return coeff_of_determination  # fit_plot_bell_curve(x,n)

def make_report(daily_sales_np, \
                daily_sales_ma, \
                sales_stats):
    """
    compute statistics and generate text report on
    the effectiveness of the advertising

    ARGUMENTS: daily_sales_np -- date/time and sales amount
               daily_sales_ma -- moving average of daily sales
               sales_stats -- object includes:
                   mask_no_adv -- True if no advertising
                   welch_t_edges -- bin edges from t stat simulation
                   welch_t_bins -- bin values from t stat simulation
                   coeff_of determination -- for Bell Curve
                      fit to Welch's t stat empirical distribution
                   input_file -- input data file
                   empirical_p_value -- from simulations
                   expected_profit_increase -- from simulations
    RETURNS: report -- text block
    """

    # check arguments
    if not isinstance(daily_sales_np, np.ndarray):
        raise TypeError(debug_prefix() + 'daily_sales_np is type ' \
                        + str(type(daily_sales_np)))

    if daily_sales_np.ndim != 2:
        raise ValueError(debug_prefix() + 'daily_sales_np has ' \
                         + str(daily_sales_np.ndim) \
                         + ' dimensions')

    if not isinstance(daily_sales_ma, np.ndarray):
        raise TypeError(debug_prefix() + 'daily_sales_ma is type ' \
                        + str(type(daily_sales_ma)))

    if daily_sales_ma.ndim != 1:
        raise ValueError(debug_prefix() + 'daily_sales_ma has ' \
                         + str(daily_sales_ma.ndim) \
                         + ' dimensions')
    if not isinstance(sales_stats, SalesStats):
        raise TypeError(debug_prefix() + 'sales_stats is type ' \
                        + str(type(sales_stats)))

    # test normality of daily sales data
    zscore_no_adv, pval_norm_no_adv \
        = st.normaltest(daily_sales_np[sales_stats.mask_no_adv, 1])
    zscore_adv, pval_norm_adv \
        = st.normaltest(daily_sales_np[sales_stats.mask_adv, 1])

    zscore_ma_no_adv, pval_ma_norm_no_adv \
        = st.normaltest(daily_sales_ma[sales_stats.mask_no_adv])
    zscore_ma_adv, pval_ma_norm_adv \
        = st.normaltest(daily_sales_ma[sales_stats.mask_adv])

    report = ""

    report += "Advertising Effectiveness Evaluation for " \
              + str(sales_stats.input_file) + "\n"
    report += "Executed " + __file__ \
              + " on Date and Time: " + time.ctime() \
              + "  PROJECT VERSION: " \
              + PROJECT_VERSION \
              + "\n"
    report += "Average Daily Sales with No Advertising: " \
              + str(sales_stats.ave_daily_sales_no_adv) + "\n"
    report += "Standard Deviation in Average Daily Sales: " \
              + str(sales_stats.std_daily_sales_no_adv) + "\n"
    report += "Normality Test ZScore of Daily Sales (NO ADV): " \
              + str(zscore_no_adv) + "\n"
    report += "Normality P-Value of Daily Sales (NO ADV): " \
              + str(pval_norm_no_adv) + "\n"
    report += "Normality Test ZScore of Daily Sales MA (NO ADV): " \
              + str(zscore_ma_no_adv) + "\n"
    report += "Normality P-Value of Daily Sales MA (NO ADV): " \
              + str(pval_ma_norm_no_adv) + "\n"

    report += "Average Daily Sales with Advertising: " \
              + str(sales_stats.ave_daily_sales_adv) + "\n"
    report += "Standard Deviation in Average Daily Sales: " \
              + str(sales_stats.std_daily_sales_adv) + "\n"
    report += "Normality Test ZScore of Daily Sales (NO ADV): " \
              + str(zscore_adv) + "\n"
    report += "Normality P-Value of Daily Sales (NO ADV): " \
              + str(pval_norm_adv) + "\n"
    report += "Normality Test ZScore of Daily Sales MA (NO ADV): " \
              + str(zscore_ma_adv) + "\n"
    report += "Normality P-Value of Daily Sales MA (NO ADV): " \
              + str(pval_ma_norm_adv) + "\n"

    report += "Welch's T Test"+ "\n"
    report += "Welch's T Statistic: " \
              + str(sales_stats.tstat) + "\n"
    report += "Welch's P Value: " \
              + str(sales_stats.pvalue) + "\n"
    report += "Coefficient of Determination Bell Curve " + \
              "Model of T STAT: %4.3f\n" \
              % sales_stats.coeff_of_determination
    report += "Empirical Distribution P-Value: %f\n" \
              % sales_stats.empirical_pvalue

    # report results from Welch's t statistic which assumes
    # the Bell Curve (Normal/Gaussian) distribution
    pct_str = "%5.2f" % float(100.0 * sales_stats.pvalue)
    report += "According to the T statistic, the probability " \
              + "that the difference in average " \
              + "daily sales between two periods\n" \
              + "is due to chance is: " + pct_str + " PERCENT \n"

    # report results from the empirical distributions
    empirical_pct_str = "%5.2f" % float(100.0 * sales_stats.empirical_pvalue)
    report += "According to the empirical distributions, the probability " \
              + "that the difference in average " \
              + "daily sales between the two periods\n" \
              + "is due to chance is: " + empirical_pct_str + " PERCENT\n"
    if sales_stats.empirical_pvalue < ALPHA_FISHER:
        report += "Null hypothesis (same average values in both periods) rejected\n"
    else:
        report += "Null hypothesis (same average values in both periods) NOT REJECTED\n"

    if not sales_stats.expected_profit_increase is None:
        profit_loss_str = locale.currency(sales_stats.expected_profit_increase,
                                          grouping=True)
        report += "Expected Profit Change: " \
                  + profit_loss_str
                  # + "{:,.2f}".format(sales_stats.expected_profit_increase)
    return report  # make_report(...)

def evaluate_advertising(*args):
    """
    wrapper for main functionality of script, evaluation of the
    effectiveness of the advertising -- which can include PR activities,
    sales and marketing consultants, social media services, etc.
    """
    global _settings
    global _b_load_settings

    # default parameters
    adv_date_str = ADV_START_DATE
    ma_period_days = 30  # moving average period (default 30 day)
    number_sims = NSIMS_DEFAULT  # 1000 thousand simulations
    annual_adv_expense = ANNUAL_ADV_EXPENSE

    # process the command line arguments
    input_file = INPUT_FILE  # default name of quickbooks sales report
    seed_val = SEED_VAL  # default random number seed for simulations
    output_folder = OUTPUT_FOLDER

    unit_price = None  # price charged to customer
    unit_cost = 0.0 # marginal cost of additional unit

    plot_duration_secs = PLOT_DURATION_SECS  # default plot duration

    if not ("-no_settings" in args
            or "-clean_start" in args):
        # load settings from shelf files
        load_settings()
    else:
        reset()  # default settings for clean start

    # initialize argument index
    arg_index = 0
    while arg_index < len(args):
        print("processing", arg_index, '/', len(args), args[arg_index])
        if args[arg_index] in ('-adv_date', '-adv_start_date', \
                               '-adv_date_start'):
            if (arg_index+1) < len(args):
                adv_date_str = args[arg_index+1]
                arg_index += 1
            else:
                raise ValueError(debug_prefix()
                                 + 'missing argument for the advertising start date ('
                                 + args[arg_index] + ')')
        elif args[arg_index] in ('-i', '-input', '-sales', \
                                 '-sales_report', \
                                 '-input_file'):
            if (arg_index+1) < len(args):
                input_file = args[arg_index+1]
                print("input_file->", input_file)
                arg_index += 1
            else:
                raise ValueError(debug_prefix() + 'missing argument for the input file ('
                                 + args[arg_index] + ')')
        elif args[arg_index] in ("-no_settings", "-clean_start"):
            pass  # do nothing
        elif args[arg_index] in ("-block", "-b"):
            # show figure and wait for user input
            if not _settings.block:
                _settings = _settings._replace(block=True)
        elif args[arg_index] in ("-layers", "-l"):
            # layered plots for presentation software slide animation
            if not _settings.layers:
                _settings = _settings._replace(layers=True)
        elif args[arg_index] in ('-d', '-debug',
                                 '-debug_level',  # backward compatible for tests
                                 '-detail_level'):
            if (arg_index + 1) < len(args):
                detail_level = int(args[arg_index+1])
                if detail_level < 0:
                    raise ValueError(debug_prefix() + "detail_level is "
                                     + str(detail_level)
                                     + " (LESS THAN ZERO)")
                _settings = _settings._replace(detail_level=detail_level)
                arg_index += 1
            else:
                raise ValueError(debug_prefix() + 'missing argument for the detail level ('
                                 + args[arg_index] + ')')

        elif args[arg_index] in ('-o',
                                 '-output',
                                 '-folder',
                                 '-output_folder'):
            if (arg_index+1) < len(args):
                output_folder = args[arg_index+1]
                arg_index += 1
            else:
                raise ValueError(debug_prefix() + 'missing argument for the output folder ('
                                 + args[arg_index] + ')')
        elif args[arg_index] in ('-price', '-p', '-unit_price'):
            if (arg_index+1) < len(args):
                unit_price = float(args[arg_index+1])
                check_unit_price(unit_price)
                arg_index += 1
            else:
                raise ValueError(debug_prefix() + 'missing argument for the unit price ('
                                 + args[arg_index] + ')')

        elif args[arg_index] in ('-cost', '-unit_cost', '-c'):
            if (arg_index+1) < len(args):
                unit_cost = float(args[arg_index+1])
                if unit_cost < 0.0:
                    raise ValueError(debug_prefix() + "ERROR: unit_cost is "
                                     + "{:,.2f}".format(unit_cost)
                                     + " (LESS THAN ZERO)")
                arg_index += 1
            else:
                raise ValueError(debug_prefix() + 'missing argument for the unit cost ('
                                 + args[arg_index] + ')')

        elif args[arg_index] in ('-plot_duration', '-pause'):
            # duration in seconds that a figure is displayed
            if (arg_index+1) < len(args):
                plot_duration_secs = float(args[arg_index+1])
                if plot_duration_secs < 0.0:
                    raise ValueError(debug_prefix() + "ERROR: plot_duration is "
                                     + "{:,.2f}".format(plot_duration_secs)
                                     + " seconds (LESS THAN ZERO)")
                arg_index += 1
            else:
                raise ValueError(debug_prefix() + 'missing argument for the plot display duration {'
                                 + args[arg_index] + ')')

        elif args[arg_index] in '-date_tag':
            if (arg_index+1) < len(args):
                date_tag_str = args[arg_index+1]
                _settings = _settings._replace(date_tag=date_tag_str)
                arg_index += 1
            else:
                ValueError(debug_prefix()
                           + 'missing argument for the date column name in the sales report ('
                           + args[arg_index] + ')')

        elif args[arg_index] in '-amount_tag':
            # the sales amount column name in the sales report
            if (arg_index+1) < len(args):
                amount_tag_str = args[arg_index+1]
                _settings = _settings._replace(amount_tag=amount_tag_str)
                arg_index += 1
            else:
                ValueError(debug_prefix() + "missing argument for the "
                           + "sales amount column name in the sales report ("
                           + args[arg_index] + ")")

        elif args[arg_index] in '-sales_type_tag':
            # the sales type column name in the sales report
            if (arg_index+1) < len(args):
                sales_type_tag_str = args[arg_index+1]
                _settings = _settings._replace(sales_type_tag
                                               =sales_type_tag_str)
                arg_index += 1
            else:
                ValueError(debug_prefix() + "missing argument for the "
                           + "optional sales type column name "
                           + "in the sales report {"
                           + args[arg_index] + ")")

        elif args[arg_index] in '-sales_type_value':
            # the value such as "Sales Receipt" for the entries of
            # interest in the optional sales type column in the
            # sales report
            if (arg_index+1) < len(args):
                sales_type_value_str = args[arg_index+1]
                _settings = _settings._replace(sales_type_value=
                                               sales_type_value_str)
                arg_index += 1
            else:
                ValueError(debug_prefix() + "missing argument for the optional sales "
                           + "type value in the sales report ("
                           + args[arg_index] + ")")

        elif args[arg_index] in ('-e', '-expenses', \
                                 '-adv_expenses', '-advertising'):
            # annual advertising expense
            if (arg_index+1) < len(args):
                # make sure convert to float (dollars)
                annual_adv_expense = float(args[arg_index+1])
                if annual_adv_expense < 0.0:
                    raise ValueError(debug_prefix() + "ERROR: annual advertising expense is "
                                     + "{:,.2f}".format(annual_adv_expense)
                                     + " (LESS THAN ZERO)")
                arg_index += 1
            else:
                raise ValueError(debug_prefix()
                                 + 'missing argument for the annual advertising expense {'
                                 + args[arg_index] + ')')
        elif args[arg_index] in ('-n', '-nsims', \
                                 '-nsimulations', '-n_simulations'):
            # number of simulations for sales and profit/loss
            # projections
            if (arg_index+1) < len(args):
                # make sure convert to float (dollars)
                number_sims = int(args[arg_index+1])
                if number_sims < 1:
                    raise ValueError(debug_prefix()
                                     + "ERROR: number of simulations is "
                                     + str(number_sims)
                                     + " (LESS THAN ONE SIMULATION)")
                arg_index += 1
            else:
                raise ValueError(debug_prefix()
                                 + 'missing argument for the number of simulations ('
                                 + args[arg_index] + ')')
        elif args[arg_index] in ('-s', '-seed', '--seed'):
            # the random number seed for the simulations
            if (arg_index+1) < len(args):
                # convert to integer
                seed_val = int(args[arg_index+1])
                if seed_val < 1:
                    raise ValueError(debug_prefix()
                                     + "ERROR: random number seed is "
                                     + str(seed_val)
                                     + " (LESS THAN ONE)")
                arg_index += 1
            else:
                raise ValueError(debug_prefix()
                                 + 'missing argument for the random number seed ('
                                 + args[arg_index] + ')')
        elif args[arg_index] in ('-reset', '-reset_settings'):
            reset()  # reset settings
            save_settings() # save settings to shelf files

        elif args[arg_index] in ('-glossary', '-gloss', '-g'):
            # print glossary of technical terms
            glossary_text = glossary()
            glossary_text += startup_notice(os.path.basename(args[0]))
            print(glossary_text)
            sys.exit(0)

        elif args[arg_index] in ('-license', '-copyright'):
            # print license
            license_text = gpl_v3_license()
            print(license_text)
            sys.exit(0)

        elif args[arg_index] in ('-startup_notice',
                                 '-short_notice',
                                 '_notice',
                                 '-short',
                                 '-notice'):
            # print short startup notice
            print(startup_notice(os.path.basename(args[0])))
            sys.exit(0)

        elif args[arg_index] in ('-disclaimer', '--disclaimer'):
            # the legal disclaimer
            disclaimer_text = disclaimer()
            disclaimer_text += startup_notice(os.path.basename(args[0]))
            print(disclaimer_text)
            sys.exit(0)

        elif args[arg_index] in ('-v', '-version', '--version'):
            print("Version:", PROJECT_VERSION)
            sys.exit(0)
        elif args[arg_index] in ('-h', '-help', '--help', '-?'):
            # the usage/help message
            usage_text = usage(os.path.basename(args[0]))
            help_text = usage_text + ad_help()
            print(help_text)
            sys.exit(0)
        else:
            if arg_index == 1 and not args[arg_index][0] == "-":
                # handle eval_adv.py sales.csv
                if os.path.exists(args[arg_index]):
                    input_file = args[arg_index]
                    print("input_file->", input_file)
                else:
                    raise ValueError(debug_prefix()
                                     + "input file "
                                     + args[arg_index]
                                     + " does not exist.  \nThis programs "
                                     "requires a comma separated values (CSV) "
                                     "format file \nwith sales data with "
                                     "the date and amount of each sales "
                                     "transaction.  \nMost spreadsheets, "
                                     "databases, and accounting programs can "
                                     "export data \nin the CSV format.\n")
            else:
                # raise Exception for unknown command line argument
                if arg_index > 0:
                    raise ValueError(debug_prefix()
                                     + "unknown command line option ", args[arg_index])

        arg_index += 1  # loop over command line arguments

    # interactive copyright/license startup notice
    print(startup_notice(os.path.basename(sys.argv[0])))

    # create the output folder if it does not exist already
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # set the random number seed
    np.random.seed(seed_val)

    base_file_name = os.path.basename(input_file)
    parts = base_file_name.split('.')
    file_stem = parts[0]

    # get the date the (new) advertising starts
    start_date = parse(adv_date_str)
    print("advertising start date:", start_date)

    # read the input file (the sales report)
    if not os.path.exists(input_file):
        # double check file exists just in case
        cwd = os.getcwd()
        raise FileNotFoundError(input_file
                                + ' does not exist in folder: '
                                + cwd)

    print("reading the sales report from", input_file)
    try:
        data_frame = pd.read_csv(input_file)
    except Exception as general_exception:
        msg = print_to_string(os.path.basename(sys.argv[0]),
                              debug_prefix()
                              + "unable to read ", input_file)
        msg += print_to_string("EXCEPTION:")
        msg += print_to_string(general_exception)
        msg += print_to_string("END EXCEPTION")
        msg += print_to_string("Try checking the file name and contents.  \n"
                               "This program requires a comma separated values "
                               "(CSV) input file.  \nMost spreadsheets, "
                               "databases, and accounting programs "
                               "can export data in the CSV format.")
        raise ValueError(debug_prefix() + msg)

    first_row = ",".join(data_frame.columns)
    for column_index, column_name in enumerate(data_frame.columns):
        try:
            value = float(column_name)
        except ValueError as value_error:
            # should fail on column names
            continue
        # if get here a column header was a number
        if not (value == float(column_index)
                or value == float(column_index+1)):
            raise ValueError(debug_prefix()
                             + "Missing column header row in sales report file "
                             + input_file + "\n\n  First row is: "
                             + first_row
                             + " \n\nTry checking the file contents and adding "
                             "a first row with column names.\n"
                             "Use DATE for dates column name, "
                             "AMOUNT for the sales amount column name, \n"
                             "and 'Type' for sales type column name.")

    date_tag, date_index = get_date_refs(data_frame,
                                         _settings.date_tag)

    sorted_data_frame = data_frame.sort_values(by=date_tag)
    first_date_ts = sorted_data_frame[date_tag][0]
    first_date = first_date_ts.date()
    try:
        day_np, daily_sales_np = compute_daily_sales(sorted_data_frame,
                                                     _settings.date_tag,
                                                     _settings.amount_tag,
                                                     _settings.sales_type_tag,
                                                     _settings.sales_type_value)
    except Exception as general_X:
        msg = debug_prefix() \
              + "compute_daily_sales(...) failed with EXCEPTION\n" \
              + str(general_X) \
              + "\nEND EXCEPTION"
        raise ValueError(msg)

    # sanity check
    if not daily_sales_np.ndim == 2:
        raise ValueError(debug_prefix()
                         + " computed daily_sales_np has "
                         + str(daily_sales_np.ndim)
                         + " dimensions (should be 2)")

    if daily_sales_np.size <= 0:
        raise ValueError(debug_prefix()
                         + " computed daily sales has "
                         + str(daily_sales_np.size)
                         + " elements (should be greater than 0)")

    mask_no_adv = daily_sales_np[:, 0] < start_date
    mask_adv = daily_sales_np[:, 0] >= start_date

    # compute and plot empirical probability distributions
    #
    dist_h_no_adv, y_err_no_adv \
        = get_dist(daily_sales_np[mask_no_adv, 1], unit_price)

    dist_h_adv, y_err_adv \
        = get_dist(daily_sales_np[mask_adv, 1], unit_price)

    dist_cumsum_no_adv = dist_h_no_adv.cumsum()
    dist_cumsum_adv = dist_h_adv.cumsum()

    x_no_adv = np.array(range(dist_h_no_adv.size))
    x_adv = np.array(range(dist_h_adv.size))

    x_no_adv_line = np.linspace(0.0, np.max(x_no_adv), 100)
    x_adv_line = np.linspace(0.0, np.max(x_adv), 100)

    # avoid divide by zero error
    zero_mask = y_err_no_adv == 0.0
    y_err_no_adv[zero_mask] = 0.01

    zero_mask = y_err_adv == 0.0
    y_err_adv[zero_mask] = 0.01

    #
    # fit Poisson model to the empirical distributions
    #


    p_start = [np.round(x_no_adv.dot(dist_h_no_adv)/dist_h_no_adv.sum())]

    popt_no_adv, pcov_no_adv = curve_fit(poisson_curve,
                                         x_no_adv,
                                         dist_h_no_adv,
                                         p_start,
                                         y_err_no_adv)

    y_fit_no_adv = poisson_curve(x_no_adv, *popt_no_adv)

    y_fit_no_adv_line = poisson_curve(x_no_adv_line, *popt_no_adv)

    res_no_adv = y_fit_no_adv - dist_h_no_adv
    r2_no_adv = 1.0 - res_no_adv.var()/dist_h_no_adv.var()

    p_start = [np.round(x_adv.dot(dist_h_adv)/dist_h_adv.sum())]

    popt_adv, pcov_adv = curve_fit(poisson_curve,
                                   x_adv,
                                   dist_h_adv,
                                   p_start,
                                   y_err_adv)

    y_fit_adv = poisson_curve(x_adv, *popt_adv)
    y_fit_adv_line = poisson_curve(x_adv_line, *popt_adv)

    res_adv = y_fit_adv - dist_h_adv
    r2_adv = 1.0 - res_adv.var()/dist_h_adv.var()

    welch_t_bins, welch_t_edges = sim_adv_period(daily_sales_np,
                                                 dist_cumsum_no_adv,
                                                 mask_adv,
                                                 file_stem,
                                                 unit_price=unit_price,
                                                 output_folder=output_folder,
                                                 plot_duration_secs=plot_duration_secs)

    coeff_of_determination \
        = fit_plot_bell_curve(welch_t_edges,
                              welch_t_bins,
                              file_stem,
                              output_folder=output_folder,
                              plot_duration_secs=plot_duration_secs)


    # create a SalesStats object
    sales_stats = SalesStats(daily_sales_np,
                             mask_no_adv,
                             welch_t_edges,
                             welch_t_bins,
                             coeff_of_determination,
                             input_file)

    if _settings.layers:
        # generate layers for animation of plot
        # in PowerPoint/Impress/presentation software

        # only daily sales
        daily_sales_ma = plot_sales_data(input_file,
                                         first_date,
                                         day_np,
                                         mask_adv,
                                         mask_no_adv,
                                         ma_period_days,
                                         daily_sales_np,
                                         sales_stats,
                                         plot_duration_secs,
                                         output_folder,
                                         show_ma=False,
                                         show_period_average=False)

        # daily sales and moving average
        daily_sales_ma = plot_sales_data(input_file,
                                         first_date,
                                         day_np,
                                         mask_adv,
                                         mask_no_adv,
                                         ma_period_days,
                                         daily_sales_np,
                                         sales_stats,
                                         plot_duration_secs,
                                         output_folder,
                                         show_ma=True,
                                         show_period_average=False)

    # show all three plot elements together (default)
    daily_sales_ma = plot_sales_data(input_file,
                                     first_date,
                                     day_np,
                                     mask_adv,
                                     mask_no_adv,
                                     ma_period_days,
                                     daily_sales_np,
                                     sales_stats,
                                     plot_duration_secs,
                                     output_folder,
                                     show_ma=True,
                                     show_period_average=True)


    # side by side pie charts of frequency of daily sales
    fig_pie = plt.figure(figsize=(12,9))
    # no advertising pie chart
    plt.subplot(1,2,1)
    labels_no_adv = [str(item) for item in x_no_adv]
    plt.pie(dist_h_no_adv.ravel(), labels=labels_no_adv, autopct='%1.1f%%')
    plt.title('NO ADVERTISING')

    # advertising pie chart
    plt.subplot(1,2,2)
    labels_adv = [str(item) for item in x_adv]
    plt.pie(dist_h_adv.ravel(), labels=labels_adv, autopct='%1.1f%%')
    plt.title('ADVERTISING')

    fp = FontProperties(family="sans-serif", size=20, weight="bold")
    plt.suptitle('UNIT SALES PER DAY', fontproperties=fp)

    if _settings.block:
        plt.show()
    else:
        plt.ion()
        plt.show()
        plt.pause(plot_duration_secs)

    fig_pie.savefig(output_folder
                     + os.sep
                     + file_stem
                     + "_pie_charts.jpg")

    fig_bar, ax_bar  = plt.subplots(figsize=(12,9))
    n_groups = max(len(x_adv), len(x_no_adv))

    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    try:
        index_no_adv = np.arange(len(x_no_adv))
        rects1 = plt.bar(index_no_adv,
                         dist_h_no_adv.ravel(),
                         bar_width,
                         alpha=opacity,
                         color='b',
                         label='NO ADVERTISING')
    except Exception as bar_X:
        print(debug_prefix(), "caught exception", bar_X)
        raise()

    try:
        index_adv = np.arange(len(x_adv))
        rects2 = plt.bar(index_adv + bar_width,
                         dist_h_adv.ravel(),
                         bar_width,
                         alpha=opacity,
                         color='g',
                         label='ADVERTISING')
    except Exception as bar_X:
        print(debug_prefix(), "caught exception", bar_X)
        raise()

    plt.xlabel('UNIT SALES PER DAY')
    plt.ylabel('FRACTION OF DAYS')
    plt.title('UNIT SALES PER DAY BAR CHART')
    bar_labels = [str(item) for item in range(n_groups+1)]
    plt.xticks(index + bar_width, bar_labels)
    plt.legend()

    plt.tight_layout()
    if _settings.block:
        plt.show()
    else:
        plt.ion()
        plt.show()
        plt.pause(plot_duration_secs)

    # save bar charts to jpeg image
    fig_bar.savefig(output_folder
                     + os.sep
                     + file_stem
                     + "_bar_charts.jpg")

    if _settings.detail_level > 0:
        # show empirical sales distributions
        fig_dist = plt.figure(figsize=(12, 9))
        plt.errorbar(x_no_adv, dist_h_no_adv.ravel(),
                     yerr=y_err_no_adv.ravel(),
                     fmt=NO_ADV_MARKER,
                     label='NO ADVERTISING',
                     linewidth=LINEWIDTH, markersize=MARKERSIZE)
        plt.errorbar(x_adv, dist_h_adv.ravel(),
                     yerr=y_err_adv.ravel(),
                     fmt=ADV_MARKER,
                     label='ADVERTISING',
                     linewidth=LINEWIDTH, markersize=MARKERSIZE)

        if _settings.detail_level > 1:
            plt.plot(x_no_adv_line, y_fit_no_adv_line,
                     NO_ADV_LINE,
                     label='NO ADV FIT', linewidth=LINEWIDTH)

            plt.plot(x_adv_line, y_fit_adv_line,
                     ADV_LINE,
                     label='ADV FIT', linewidth=LINEWIDTH)

        plt.title('ESTIMATED PROBABILITY OF A NUMBER OF SALES PER DAY')
        plt.xlabel('NUMBER OF UNIT SALES PER DAY')
        plt.ylabel('FRACTION OF DAYS WITH THE NUMBER OF DAILY SALES')
        plt.legend(loc='upper right')
        if _settings.detail_level > 1:
            xlo, xhi = plt.xlim()
            delta_x = xhi - xlo
            ylo, yhi = plt.ylim()
            delta_y = yhi - ylo
            # add coefficients of determination from fits
            plt.text(xlo + delta_x*0.025,
                     yhi - 0.05*delta_y,
                     'NO ADV R**2: %3.2f' % r2_no_adv)
            plt.text(xlo + 0.025*delta_x,
                     yhi - 0.09*delta_y,
                     'ADV R**2: %3.2f' % r2_adv)

        plt.grid()
        if _settings.block:
            plt.show()
        else:
            plt.ion()
            plt.show()
            plt.pause(plot_duration_secs)

        fig_dist.savefig(output_folder
                         + os.sep
                         + file_stem
                         + "_empirical_distributions.jpg")

    # simulate future year sales with and without adv

    # TO DO: simulate future year sales with and without adv
    # using the empirical daily sales distributions
    #
    year_shape = (365,)
    if unit_price is None:
        # infer the unit price from the sales data
        unit_prices = get_unit_prices(daily_sales_np[mask_no_adv, 1])
        unit_price = unit_prices[0]
        check_unit_price(unit_price)

    else:
        # use unit_price from command line arguments
        pass

    # initialize accumulators for simulated average sales
    ave_sales_no_adv = np.zeros((number_sims,))
    ave_sales_no_adv_test = np.zeros((number_sims,))
    ave_sales_adv = np.zeros((number_sims,))

    if not root is None:
        print("creating the ttk progres bar...")
        progress_var = IntVar()
        pbar = Progressbar(root,
                           variable=progress_var,
                           maximum=number_sims,
                           orient=HORIZONTAL,
                           mode='determinate')
        pbar.pack(fill=X, expand=1)
        root.update_idletasks()

    print("simulating annual sales using empirical distributions")
    t_mark = time.time()
    for trial_index in range(number_sims):
        # one full year with advertising
        dist_cumsum_adv_varied = vary_distribution(dist_cumsum_adv,
                                                   y_err_adv)

        unit_sales_adv = sim_unit_sales(dist_cumsum_adv_varied,
                                        year_shape)

        # one full year without advertising
        dist_cumsum_no_adv_varied = vary_distribution(dist_cumsum_no_adv,
                                                      y_err_no_adv)

        unit_sales_no_adv = sim_unit_sales(dist_cumsum_no_adv_varied,
                                           year_shape)

        # simulate no advertising values for the differential risk
        # assessment
        dist_cumsum_no_adv_test_varied = vary_distribution(dist_cumsum_no_adv,
                                                      y_err_no_adv)

        unit_sales_no_adv_test = sim_unit_sales(dist_cumsum_no_adv_varied,
                                           year_shape)

        # compute average daily sales for each simulated period
        ave_sales_no_adv[trial_index] \
            = (unit_price * unit_sales_no_adv).sum() \
            / unit_sales_no_adv.size

        # test simulation for differential risk assessment
        ave_sales_no_adv_test[trial_index] \
            = (unit_price * unit_sales_no_adv_test).sum() \
            / unit_sales_no_adv_test.size

        ave_sales_adv[trial_index] \
            = (unit_price * unit_sales_adv).sum() / unit_sales_adv.size

        # progress message every second
        t_now = time.time()
        if (t_now - t_mark) > 1.0:
            print(trial_index, "/", number_sims, flush=True)
            t_mark = t_now
        if not root is None:
            progress_var.set(trial_index)
            root.update_idletasks()
        # end simulation loop

    if not root is None:
        print("destroying ttk progress bar")
        pbar.destroy()

# compute empirical p-value
    low_sales = 0.0
    hi_sales = np.max((np.max(ave_sales_no_adv),
                       np.max(ave_sales_adv)))

    # use histogram to get estimate of the probability density
    # function for sales for two periods

    bins_no_adv, edges_no_adv = np.histogram(ave_sales_no_adv,
                                             bins=_settings.bins,
                                             range=(low_sales, hi_sales),
                                             density=True)
    bins_adv, edges_adv = np.histogram(ave_sales_adv,
                                       bins=_settings.bins,
                                       range=(low_sales, hi_sales),
                                       density=True)

    if _settings.detail_level > 1:
        xval = (edges_no_adv[:-1] + edges_no_adv[1:])/2.0

        f_pdf = plt.figure(figsize=(12, 9))
        plt.plot(xval, bins_no_adv,
                 NO_ADV_MARKER,
                 label='NO ADV', markersize=MARKERSIZE, linewidth=LINEWIDTH)
        plt.plot(xval, bins_adv,
                 ADV_MARKER,
                 label='ADV', markersize=MARKERSIZE, linewidth=LINEWIDTH)
        plt.grid()
        plt.legend(loc='upper right')
        plt.xlabel('DOLLARS')
        plt.ylabel('Probability Density')
        plt.title('Empirical Sales Probability Density '
                  'from the Sales Projection')

        ax_list = f_pdf.axes
        ax = ax_list[0]
        formatter = FuncFormatter(currency)
        ax.xaxis.set_major_formatter(formatter)

        if _settings.block:
            plt.show()
        else:
            plt.ion()
            plt.show()
            plt.pause(plot_duration_secs)
        f_pdf.savefig(output_folder + os.sep +
                      file_stem + "_sales_pdf.jpg")

    # density result is normalized by bin widths
    bin_widths = edges_adv[1:] - edges_adv[:-1]
    pdf_adv = bins_adv*bin_widths
    pdf_no_adv = bins_no_adv*bin_widths
    # compute probability of overlap between the
    # two distributions
    empirical_p_value = (pdf_adv * pdf_no_adv).sum()

    ave_sales_increase \
        = DAYS_PER_YEAR*(ave_sales_adv \
                         - ave_sales_no_adv)

    ave_cost_increase \
        = unit_cost*DAYS_PER_YEAR*((ave_sales_adv/unit_price) \
                                   - (ave_sales_no_adv/unit_price))

    # differential risk assessement
    #
    # compare simulations with NO ADVERTISING
    #
    ave_sales_increase_diff \
        = DAYS_PER_YEAR*(ave_sales_no_adv_test \
                         - ave_sales_no_adv)

    if _settings.detail_level > 0:
        plot_ave_hist(ave_sales_increase_diff,
                      input_file,
                      output_folder,
                      'AVERAGE SALES INCREASE DIFF',
                      plot_duration_secs)


    ave_cost_increase_diff \
        = unit_cost*DAYS_PER_YEAR*((ave_sales_no_adv_test/unit_price) \
                                   - (ave_sales_no_adv/unit_price))

    annual_sales_no_adv_test = DAYS_PER_YEAR*ave_sales_no_adv_test

    # show sales/profit projections for year with no advertising

    annual_sales_no_adv = DAYS_PER_YEAR*ave_sales_no_adv

    ave_profit_increase_diff = ave_sales_increase_diff
    # deduct marginal cost of new units sold
    ave_profit_increase_diff \
        = ave_profit_increase_diff - ave_cost_increase_diff

    expected_profit_increase_diff \
        = ave_profit_increase_diff.mean()

    if _settings.detail_level > 0:
        fig_no_adv = plt.figure(figsize=(12, 9))
        sales_bins, sales_edges, patches \
            = plt.hist(annual_sales_no_adv, bins=_settings.bins)
        plt.title('ANNUAL SALES WITH NO ADVERTISING')
        plt.ylabel('NUMBER OF SIMULATIONS')
        plt.xlabel('DOLLARS')
        plt.grid()

        ax_list = fig_no_adv.axes
        ax = ax_list[0]
        formatter = FuncFormatter(currency)
        ax.xaxis.set_major_formatter(formatter)


        if _settings.block:
            plt.show()
        else:
            plt.ion()
            plt.show()  # sales projection histogram
            # wait to display the figure
            plt.pause(plot_duration_secs)

        image_file = file_stem + "_sales_projection_no_adv.jpg"
        print("saving sales projection bar chart to", image_file)
        fig_no_adv.savefig(output_folder + os.sep + image_file)
    else:
        sales_bins, sales_edges \
            = np.histogram(annual_sales_no_adv,
                           bins=_settings.bins)

    # show sales/profit projections for year with advertising

    annual_sales_adv = DAYS_PER_YEAR*ave_sales_adv

    if _settings.detail_level > 0:
        fig_adv = plt.figure(figsize=(12, 9))
        sales_bins, sales_edges, patches \
            = plt.hist(annual_sales_adv, bins=_settings.bins)
        n_loss_sales_adv = compute_loss(sales_bins, sales_edges)
        plt.title('ANNUAL SALES WITH ADVERTISING')
        plt.ylabel('NUMBER OF SIMULATIONS')
        plt.xlabel('DOLLARS')
        plt.grid()

        ax_list = fig_adv.axes
        ax = ax_list[0]
        formatter = FuncFormatter(currency)
        ax.xaxis.set_major_formatter(formatter)

        if _settings.block:
            plt.show()
        else:
            plt.ion()
            plt.show()  # sales projection histogram
            # wait to display the figure
            plt.pause(plot_duration_secs)

        image_file = file_stem + "_sales_projection_adv.jpg"
        print("saving sales projection bar chart to", image_file)
        fig_adv.savefig(output_folder + os.sep + image_file)
    else:
        sales_bins, sales_edges \
            = np.histogram(annual_sales_adv,
                           bins=_settings.bins)

    ave_profit_increase = ave_sales_increase - annual_adv_expense
    # deduct marginal cost of new units sold
    ave_profit_increase = ave_profit_increase - ave_cost_increase

    expected_profit_increase = ave_profit_increase.mean()

    if _settings.detail_level > 0:
        figure_2 = plt.figure(figsize=(12, 9))
        sales_bins, sales_edges, patches \
            = plt.hist(ave_sales_increase, bins=_settings.bins)
        n_loss_sales = compute_loss(sales_bins, sales_edges)
        plt.title('ANNUAL SALES INCREASE FROM ADVERTISING (' \
                  + str(number_sims) + ' SIMULATIONS)')
        plt.ylabel('NUMBER OF SIMULATIONS')
        plt.xlabel('DOLLARS')
        xlow, xhi = plt.xlim()
        delta_x = (xhi - xlow)
        ylow, yhi = plt.ylim()
        delta_y = (yhi - ylow)
        plt.text(xlow + 0.025*delta_x, yhi-0.05*delta_y, \
                 "Number of Simulations with " + \
                 "Sales Decline: %5.1f / %5.1f" \
                 % (n_loss_sales, number_sims), \
                 bbox=dict(facecolor='white', alpha=0.5))
        plt.grid()

        ax_list = figure_2.axes
        ax = ax_list[0]
        formatter = FuncFormatter(currency)
        ax.xaxis.set_major_formatter(formatter)


        if _settings.block:
            plt.show()
        else:
            plt.ion()
            plt.show()  # sales projection histogram
            # wait to display the figure
            plt.pause(plot_duration_secs)
    else:
        sales_bins, sales_edges = np.histogram(ave_sales_increase,
                                               bins=_settings.bins)
        n_loss_sales = compute_loss(sales_bins, sales_edges)


    # average daily sales increase
    if _settings.detail_level > 0:
        figure_2b = plt.figure(figsize=(12, 9))
        daily_sales_bins, daily_sales_edges, patches \
            = plt.hist(ave_sales_increase/DAYS_PER_YEAR, bins=_settings.bins)
        n_loss_daily_sales = compute_loss(daily_sales_bins, daily_sales_edges)

        plt.title('DAILY SALES INCREASE FROM ADVERTISING (' \
                  + str(number_sims) + ' SIMULATIONS)')
        plt.ylabel('NUMBER OF SIMULATIONS')
        plt.xlabel('DOLLARS')
        xlow, xhi = plt.xlim()
        delta_x = (xhi - xlow)
        ylow, yhi = plt.ylim()
        delta_y = (yhi - ylow)
        plt.text(xlow + 0.025*delta_x, yhi-0.05*delta_y, \
                 "Number of Simulations with " \
                 + "Sales Decline: %5.1f / %5.1f" \
                 % (n_loss_daily_sales, number_sims), \
                 bbox=dict(facecolor='white', alpha=0.5))
        plt.grid()

        ax_list = figure_2b.axes
        ax = ax_list[0]
        formatter = FuncFormatter(currency)
        ax.xaxis.set_major_formatter(formatter)

        if _settings.block:
            plt.ion()
            plt.show()
            # wait to display the figure
            plt.pause(plot_duration_secs)
        else:
            plt.show()
    else:
        daily_sales_bins, daily_sales_edges \
            = np.histogram(ave_sales_increase/DAYS_PER_YEAR,
                           bins=_settings.bins)
        n_loss_daily_sales = compute_loss(daily_sales_bins, daily_sales_edges)

    if _settings.detail_level > 0:
        figure_3 = plt.figure(figsize=(12, 9))
        profit_bins, profit_edges, patches = plt.hist(ave_profit_increase,
                                                      bins=_settings.bins)
        n_loss_profits = compute_loss(profit_bins, profit_edges)
        plt.title('ANNUAL PROFIT INCREASE FROM ADVERTISING (' \
                  + str(number_sims) + ' SIMULATIONS)')
        plt.ylabel('NUMBER OF SIMULATIONS')
        plt.xlabel('DOLLARS')
        plt.grid()
        xlow, xhi = plt.xlim()
        delta_x = (xhi - xlow)
        ylow, yhi = plt.ylim()
        delta_y = (yhi - ylow)
        plt.text(xlow + 0.025*delta_x, yhi-0.05*delta_y, \
                 "Number of Simulations with Losses: %5.1f / %5.1f" \
                 % (n_loss_profits, number_sims), \
                 bbox=dict(facecolor='white', alpha=0.5))

        ax_list = figure_3.axes
        ax = ax_list[0]
        formatter = FuncFormatter(currency)
        ax.xaxis.set_major_formatter(formatter)

        if _settings.block:
            plt.show()
        else:
            plt.ion()
            plt.show()
            # wait to display the figure
            plt.pause(plot_duration_secs)  # profit projections histogram
    else:
        profit_bins, profit_edges = np.histogram(ave_profit_increase,
                                                 bins=_settings.bins)
        n_loss_profits = compute_loss(profit_bins, profit_edges)

    if _settings.detail_level > 0:
        plot_projections(sales_edges,
                         sales_bins,
                         profit_edges,
                         profit_bins,
                         number_sims,
                         input_file,
                         expected_profit_increase,
                         annual_adv_expense,
                         n_loss_sales,
                         n_loss_profits,
                         seed_val,
                         plot_duration_secs,
                         output_folder,
                         suffix="_adv")


    sales_bins_diff, \
        sales_edges_diff = np.histogram(ave_sales_increase_diff,
                                        bins=_settings.bins)
    n_loss_sales_diff = compute_loss(sales_bins_diff,
                                     sales_edges_diff)

    profit_bins_diff, \
        profit_edges_diff = np.histogram(ave_profit_increase_diff,
                                         bins=_settings.bins)
    n_loss_profit_diff = compute_loss(profit_bins_diff,
                                      profit_edges_diff)

    if _settings.detail_level > 0:
        plot_projections(sales_edges_diff,
                         sales_bins_diff,
                         profit_edges_diff,
                         profit_bins_diff,
                         number_sims,
                         input_file,
                         expected_profit_increase_diff,
                         0.0,  # no advertising expense
                         n_loss_sales_diff,
                         n_loss_profit_diff,
                         seed_val,
                         plot_duration_secs,
                         output_folder,
                         suffix="_no_adv")

    if _settings.layers:
        plot_diff_risk(profit_edges_diff,
                       profit_bins_diff,
                       profit_edges,
                       profit_bins,
                       number_sims,
                       input_file,
                       expected_profit_increase,
                       0.0,  # no advertising expense
                       n_loss_sales_diff,
                       n_loss_profit_diff,
                       seed_val,
                       plot_duration_secs,
                       output_folder,
                       suffix="_diff",
                       show_no_adv=True,
                       show_with_adv=False,
                       show_ave_with_adv=False)

        plot_diff_risk(profit_edges_diff,
                       profit_bins_diff,
                       profit_edges,
                       profit_bins,
                       number_sims,
                       input_file,
                       expected_profit_increase,
                       0.0,  # no advertising expense
                       n_loss_sales_diff,
                       n_loss_profit_diff,
                       seed_val,
                       plot_duration_secs,
                       output_folder,
                       suffix="_diff",
                       show_no_adv=True,
                       show_with_adv=True,
                       show_ave_with_adv=False)

    # MAIN PLOT
    # plot profit projections for no advertising vs advertising case
    plot_diff_risk(profit_edges_diff,
                   profit_bins_diff,
                   profit_edges,
                   profit_bins,
                   number_sims,
                   input_file,
                   expected_profit_increase,
                   0.0,  # no advertising expense
                   n_loss_sales_diff,
                   n_loss_profit_diff,
                   seed_val,
                   plot_duration_secs,
                   output_folder,
                   suffix="_diff")

    sales_stats.empirical_p_value = empirical_p_value
    sales_stats.expected_profit_increase = expected_profit_increase

    # compute and generate final report
    report = make_report(daily_sales_np,
                         daily_sales_ma,
                         sales_stats)

    print(report)

    # write report to file
    with open(output_folder + os.sep
              + file_stem + "_report.txt", "w") as out_file:
        out_file.write(report)

    save_settings()
#  end of evaluate_advertising()

def exit(event=None):
    quit()

if __name__ == "__main__":


    # unittest.main()   # run unit tests
    locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
    if '-gui' in sys.argv[1:]:
        # run GUI
        root = Tk()
        root.title("AdEvaluator\u2122")
        #
        # Half the money I spend on advertising is wasted; the trouble is,
        # I don't know which half. John Wanamaker
        #
        # VGA (480w by 640h) compatible size
        root.geometry(GEOMETRY_STRING)  # image is 470 by xxx pixels
        # keyboard shortcuts for file menu
        root.bind('<Control-q>', exit)
        root.bind('<Control-o>', open_file)
        root.bind('<Control-v>', view_file)

        # keyboard shortcuts for run menu
        root.bind('<Control-s>', launch_settings)
        root.bind('<Control-r>', eval_file)  # run program

        # keyboard shortcuts for help menu
        root.bind('<Control-h>', show_help)
        root.bind('<Control-u>', show_usage)
        root.bind('<Control-l>', show_license)
        root.bind('<Control-g>', show_glossary)
        root.bind('<Control-d>', show_disclaimer)
        root.bind('<Control-w>', open_website)
        root.bind('<Control-a>', about_program)

        menu = Menu(root)
        root.config(menu=menu)
        file_menu = Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
#        file_menu.add_command(label="New", command=new_file)
        file_menu.add_command(label="Open Sales Report...",
                              command=open_file,
                              accelerator="Ctrl-O")
        file_menu.add_command(label="View Selected File",
                              command=view_file,
                              accelerator="Ctrl-V")
        file_menu.add_separator()
        file_menu.add_command(label="Exit",
                              command=exit,
                              accelerator="Ctrl-Q")

        run_menu = Menu(menu)
        menu.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Settings",
                             command=launch_settings,
                             accelerator="Ctrl-S")
        run_menu.add_separator()
        run_menu.add_command(label="Run Evaluation",
                             command=eval_file,
                             accelerator="Ctrl-R")

        # Help menu
        help_menu = Menu(menu)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="AdEvaluator\u2122 Help...",
                              command=show_help,
                              accelerator="Ctrl-H")
        help_menu.add_command(label="Usage...",
                              command=show_usage,
                              accelerator="Ctrl-U")
        help_menu.add_command(label="Glossary...",
                              command=show_glossary,
                              accelerator="Ctrl-G")
        help_menu.add_command(label="Disclaimer...",
                              command=show_disclaimer,
                              accelerator="Ctrl-D")
        help_menu.add_command(label="License...",
                              command=show_license,
                              accelerator="Ctrl-L")
        help_menu.add_command(label="AdEvaluator\u2122 Website",
                              command=open_website,
                              accelerator="Ctrl-W")
        help_menu.add_separator()
        help_menu.add_command(label="About...",
                              command=about_program,
                              accelerator="Ctrl-A")

        photo = PhotoImage(file=r"splashscreen.png")
        cv = Canvas()
        cv.pack(side='top', fill='both', expand='yes')
        cv.create_image(10, 10, image=photo, anchor='nw')
        if platform.system != 'Darwin':
            # bring main GUI window to front
            root.lift()
            root.call('wm', 'attributes', '.', '-topmost', True)
            root.after_idle(root.call, 'wm', 'attributes', '.',
                            '-topmost', False)
        else:
            pass
        root.mainloop()
    else:
        # command line operation
        evaluate_advertising(*sys.argv)
    print(__file__, "ALL DONE")

AdEvaluator(tm)

AdEvaluator(tm) evaluates the effect of advertising (or marketing,
sales, or public relations) on sales and profits by analyzing a sales
report in comma separated values (CSV) format from QuickBooks or other
accounting programs.  It requires a reference period without the
advertising and a test period with the advertising.  The advertising
should be the only change between the two periods.  There are some
additional limitations explained in the on-line help for the program.

This demo folder contains the AdEvaluator program and several
samples sales data files.  AdEvaluator is a Python 3 program
that uses a number of add-on packages for Python not included
in the base Python 3 distribution.  It was developed with the
Anaconda Python 3 distribution which contains all needed add-on
packages.

Anaconda can be downloaded from https://www.anaconda.com/download/

FILES:

AdEvaluator.bat -- Microsoft Windows DOS Batch file to launch
AdEvaluator GUI

eval_adv.bat -- Microsoft Windows DOS Batch file to launch AdEvaluator
from DOS command line

eval_adv.py -- Python 3 AdEvaluator program

splashscreen.png -- Mathematical Software splashscreen

eval-adv_version.txt -- AdEvaluator version number

view_settings.bat -- DOS command to run view_settings.py

view_settings.py -- report settings from settings shelf files

sales_seed_113.csv -- simulated sales data with a sales boost
from advertising

sales_no_increase.csv -- simulated sales data with no sales boost
from advertising

sales_renamed.csv -- CSV file with Date column title of BOB, for
demonstrating specifying the Date column header manually with the
settings.

sales_renamed_amount.csv -- CSV sales data file with Amount column
title ALICE, for demonstrating specifying the Amount column header
manually with settings.

sales_renamed_columns.csv -- CSV sales data with Date column title
of BOB and Amount column title of ALICE, for demonstrating specifying
multiple column headers at once.

sales_renamed_with_type.csv -- CSV sales data file with the Date
renamed to BOB and a Type column with the sales type, for
demonstrating selection of sales transactions by sales type ('Payment'
in this case).

sales_pvalue.csv -- CSV sales data file with sales boost with tiny
p-value but loses money, demonstrating weakness of p-value for
evaluating performance -- practical significance versus stastistical
significance proble.

sales_pvalue_null.csv -- CSV sales data file with no sales boost,
p-value is of order 1.0, not clear effect.

sales_big_increase.csv -- CSV sales data file with a large, obvious
sales boost, no mathematics required to see boost.

sales_decrease.csv -- CSV sales data file with sales decrease
caused by the advertising.

sales_small_decrease.csv -- CSV sales data file with a small
sales decrease due to advertising.

sales_medium_decrease.csv -- CSV sales data file with a medium
sized sales decrease due to advertising.

start_adv_90_days.csv -- CSV sales data file with advertising
started after 90 days (about 01/01/2018)

test_start_adv_90_days.au3  -- AutoIT Microsoft Windows GUI
test to test setting the advertising start date in the
GUI settings dialog

test_eval_adv_gui.au3 -- AutoIt Microsoft Windows GUI test
script

AutoIt is a freeware automation language for Microsoft Windows. In its
earliest release, the software was primarily intended to create
automation scripts (sometimes called macros) for Microsoft Windows
programs but has since grown to include enhancements in both
programming language design and overall functionality.

AutoIt can be downloaded from
https://www.autoitscript.com/site/autoit/downloads/

This program comes with ABSOLUTELY NO WARRANTY; for details use
-license option.  This is free software, and you are welcome to
redistribute it under certain conditions; use -license option for
details.

README.TXT -- this README file



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

(C) 2018 by John F. McGowan, Ph.D. (E-Mail: ceo@mathematical-software.com)

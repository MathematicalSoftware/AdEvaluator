@ECHO OFF
REM DOS Batch file for drag and drop invocation of eval_adv.py
ECHO "%~1"
start /min python eval_adv.py -gui %1
exit

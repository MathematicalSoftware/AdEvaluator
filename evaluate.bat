@ECHO OFF
REM DOS Batch file for drag and drop invocation of eval_adv.py
ECHO "%~1"
python eval_adv.py %1
pause

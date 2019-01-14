#cs ----------------------------------------------------------------------------

 AutoIt Version: 3.3.14.5
 Author:         myName

 Script Function:
	Template AutoIt script.

#ce ----------------------------------------------------------------------------

; Script Start - Add your code below here

#include <MsgBoxConstants.au3>
;MsgBox($MB_OK, "Tutorial", "Hello World!")

#include <MsgBoxConstants.au3>
#include <WinAPIFiles.au3>

Func DeleteShelf()
     Local $iDelete = FileDelete("eval_adv_settings.*")

     ; Display a message of whether the file was deleted.
;     If $iDelete Then
;        MsgBox($MB_SYSTEMMODAL, "", "The file was successfuly deleted.")
;      Else
;        MsgBox($MB_SYSTEMMODAL, "", "An error occurred whilst deleting the file.")
;      EndIf
EndFunc

; test for renaming two columns (DATE and AMOUNT)
DeleteShelf()
Sleep(2000) ; just in case deletion takes a while
Run("python eval_adv.py -gui", "", @SW_HIDE)
WinWaitActive("AdEvaluator")
Send("^o")
WinWaitActive("Open Sales Report")
Sleep(1000)
Send("sales_renamed_columns.csv")
Sleep(2000)
Send("{ENTER}")
Sleep(1000)
Send("^s")
WinWaitActive("Settings Dialog")
Send("{TAB}{TAB}{TAB}{TAB}{TAB}")
Send("BOB")
Sleep(2000)
Send("{TAB}")
Send("ALICE")
Sleep(2000)
Send("{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{SPACE}")
Sleep(2000)
Send("^r")
WinWaitActive("Figure 4")
WinWaitActive("AdEvaluator")
Send("^q")
Sleep(1000)
; end of rename columns test

MsgBox($MB_OK, "Test 1 Done", "Test 1 Done")

; test for cryptic error
DeleteShelf()
Sleep(2000) ; just in case deletion takes a while
Run("python eval_adv.py -gui", "", @SW_HIDE)
WinWaitActive("AdEvaluator")
Send("^o")
WinWaitActive("Open Sales Report")
Send("sales_renamed_with_type.csv")
Sleep(2000)
Send("{ENTER}")
Sleep(1000)
Send("^s")
WinWaitActive("Settings Dialog")
Send("{TAB}{TAB}{TAB}{TAB}{TAB}")
Send("BOB")
Sleep(2000)
Send("{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{SPACE}")
Sleep(2000)
Send("^r")
WinWaitActive("Figure 4")
WinWaitActive("AdEvaluator")
Send("^q")
Sleep(1000)
; end of cryptic error test

MsgBox($MB_OK, "Test 2 Done", "Test 2 Done")


; run the sales amount rename test
DeleteShelf()
Sleep(2000)
Run("python eval_adv.py -gui", "", @SW_HIDE)
WinWaitActive("AdEvaluator")
Send("^o")
WinWaitActive("Open Sales Report")
Send("sales_renamed_amount.csv")
Sleep(2000)
Send("{ENTER}")
Sleep(1000)
Send("^s")
WinWaitActive("Settings Dialog")
Send("{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}")
Send("ALICE")
Sleep(2000)
Send("{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{SPACE}")
Sleep(2000)
Send("^r")
WinWaitActive("Figure 4")
WinWaitActive("AdEvaluator")
Send("^q")
Sleep(1000)
; rerun to test persistence of changed settings
Run("python eval_adv.py -gui", "", @SW_HIDE)
WinWaitActive("AdEvaluator")
Send("^o")
WinWaitActive("Open Sales Report")
Send("sales_renamed_amount.csv")
Sleep(2000)
Send("{ENTER}")
Sleep(1000)
Send("^r")
WinWaitActive("Figure 4")
WinWaitActive("AdEvaluator")
Send("^q")
Sleep(1000)
; end sales amount rename test

MsgBox($MB_OK, "Test 3 Done", "Test 3 Done")


; run the date rename with sales type test
DeleteShelf()
Sleep(2000)
Run("python eval_adv.py -gui", "", @SW_HIDE)
; time delay in msec
WinWaitActive("AdEvaluator")
; open test file
Send("^o")
WinWaitActive("Open Sales Report")
Send("sales_renamed_with_type.csv")
Sleep(1000)
Send("{ENTER}")
Sleep(1000)
; launch settings dialog
Send("^s")
WinWaitActive("Settings Dialog")
Send("{TAB}{TAB}{TAB}{TAB}{TAB}")
; set the date column header
Send("BOB")
Sleep(1000)
; set the sales type header
Send("{TAB}{TAB}Type")
; set the sales type value
Send("{TAB}Payment")
Sleep(2000)
; click OK and dismiss settings dialog
Send("{TAB}{TAB}{TAB}{TAB}{TAB}{SPACE}")
Sleep(2000)
; run the ad evaluation with new settings
Send("^r")
WinWaitActive("Figure 4")
WinWaitActive("AdEvaluator")
Send("^q")
Sleep(1000)
; end date rename with sales type test

MsgBox($MB_OK, "Test 4 Done", "Test 4 Done")

; run the date rename test
DeleteShelf()
Sleep(2000)
Run("python eval_adv.py -gui", "", @SW_HIDE)
WinWaitActive("AdEvaluator")
Send("^o")
WinWaitActive("Open Sales Report")
Send("sales_renamed.csv{ENTER}")
Sleep(1000)
Send("^s")
WinWaitActive("Settings Dialog")
Send("{TAB}{TAB}{TAB}{TAB}{TAB}")
Send("BOB")
Sleep(2000)
Send("{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{SPACE}")
Sleep(2000)
Send("^r")
WinWaitActive("Figure 4")
WinWaitActive("AdEvaluator")
Send("^q")
Sleep(1000)
; end date rename test

MsgBox($MB_OK, "Test 5 Done", "Test 5 Done")

; basic test
DeleteShelf()
Sleep(2000)
Run("python eval_adv.py -gui", "", @SW_HIDE)
WinWaitActive("AdEvaluator")
Send("^o")
WinWaitActive("Open Sales Report")
Send("sales_seed_113.csv{ENTER}")
Sleep(1000)
; run the ad evaluator program
Send("^r")
WinWaitActive("Figure 4")
WinWaitActive("AdEvaluator")
Send("^q")
Sleep(1000)
; end basic test

MsgBox($MB_OK, "GUI Test Done", "AdEvaluator (TM) GUI Test Completed!")


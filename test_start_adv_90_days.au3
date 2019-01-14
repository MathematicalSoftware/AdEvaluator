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

; test for set advertising start date to 01/01/2018 (90 days)
DeleteShelf()
Sleep(2000) ; just in case deletion takes a while
Run("python eval_adv.py -gui", "", @SW_HIDE)
WinWaitActive("AdEvaluator")
Send("^o")
WinWaitActive("Open Sales Report")
Send("sales_start_90_days.csv")
Sleep(2000)
Send("{ENTER}")
Sleep(1000)
Send("^s")
WinWaitActive("Settings Dialog")
Send("{TAB}{TAB}")
Send("01/01/2018")
Sleep(2000)
Send("{TAB}{TAB}{TAB}{TAB}")
Sleep(2000)
Send("{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{SPACE}")
Sleep(2000)
Send("^r")
WinWaitActive("Figure 3")
WinWaitActive("AdEvaluator")
Send("^q")
Sleep(1000)
; end of set advertising start date test

MsgBox($MB_OK, "GUI Test Done", "test_start_adv_90_days done")

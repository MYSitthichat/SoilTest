Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "reg_main.bat" & chr(34), 0
Set WshShell = Nothing
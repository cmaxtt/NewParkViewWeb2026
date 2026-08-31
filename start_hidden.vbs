' Park View Drugs - Hidden Launcher (auto-restart)
' Runs the Flask app silently at startup, restarts if it crashes
' Location-agnostic: resolves the app dir from this script's own path.

Dim shell, pythonPath, scriptPath, workDir, cmd, fso
Set fso = CreateObject("Scripting.FileSystemObject")
workDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonPath = workDir & "\.venv\Scripts\python.exe"
scriptPath = workDir & "\run_prod.py"

Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = workDir

' Keep restarting if it crashes (max 5 tries, 10s delay)
For i = 1 To 5
    cmd = """" & pythonPath & """ """ & scriptPath & """"
    shell.Run cmd, 0, True
    If i < 5 Then
        WScript.Sleep 10000  ' Wait 10s before restart
    End If
Next

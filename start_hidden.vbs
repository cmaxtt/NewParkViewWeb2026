' Park View Drugs — Hidden Launcher (auto-restart)
' Runs the Flask app silently at startup, restarts if it crashes

Dim shell, pythonPath, scriptPath, workDir, cmd
pythonPath = "C:\Users\cmaxt\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
scriptPath = "C:\aa-NewWeb\run_prod.py"
workDir    = "C:\aa-NewWeb"

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

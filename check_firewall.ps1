Write-Host "=== Firewall Rules for Port 5000 ==="
$rules = Get-NetFirewallRule -Direction Inbound | Where-Object { $_.LocalPort -eq 5000 -or $_.DisplayName -like "*Park*" -or $_.DisplayName -like "*Flask*" -or $_.DisplayName -like "*5000*" } | ForEach-Object {
    $obj = $_ | Get-NetFirewallAddressFilter
    [PSCustomObject]@{
        Name = $_.DisplayName
        Enabled = $_.Enabled
        Action = $_.Action
        LocalPort = $_.LocalPort
        RemoteAddress = $obj.RemoteAddress
    }
}
if ($rules) { $rules | Format-Table -AutoSize }
else { Write-Host "No rules found for port 5000." -ForegroundColor Yellow }

Write-Host "`n=== All Inbound Rules on TCP 5000 ==="
Get-NetFirewallPortFilter -Protocol TCP | Where-Object { $_.LocalPort -eq 5000 } | ForEach-Object {
    $rule = $_ | Get-NetFirewallRule
    Write-Host "  $($rule.DisplayName) — Enabled=$($rule.Enabled) Action=$($rule.Action)"
}

Write-Host "`n=== Test Listeners ==="
netstat -ano | Select-String ":5000"

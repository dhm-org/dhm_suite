param(
    [string]$option = "enable",
	[switch]$Elevated
)
function Test-Admin {
  $currentUser = New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent())
  $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

if ((Test-Admin) -eq $false)  {
    if ($elevated) 
    {
        # Administrative privilege is required for adding remote wake registry keys. If elevating to 'Admin' fails, abort
		write-host "Couldn't elevate to run this script with Administrative privileges, aborting......"
    } 
    else {
        Start-Process powershell.exe -Verb RunAs -ArgumentList ('-noprofile -noexit -file "{0}" -elevated' -f ($myinvocation.MyCommand.Definition))
	}
	exit
}

$bthRegPath="HKLM:\System\CurrentControlSet\Services\BthPort\Parameters"
$bthRemWakeName="SystemRemoteWakeSupported"
$IntelBTAdapterList = @("VID_8087&PID_0A2A","VID_8087&PID_0A2B","VID_8087&PID_07DC","VID_8087&PID_0AA7","VID_8087&PID_0025","VID_8087&PID_0AAA")
$bthUSBDevPath="HKLM:\System\CurrentControlSet\Enum\USB"
$bthDevRWParam1="DeviceRemoteWakeSupported"
$bthDevRWParam2="RemoteWakeEnabled"
$needReboot=$false


if ($option -eq "enable") {
	write-host "Enabling Bluetooth Remote Wake........"
}
elseif ($option -eq "disable") {
	 write-host "Disabling Bluetooth Remote Wake......"
}
else {
	write-host "Invalid option, Usage: ibt-remwake-control.ps1 -option [enable|disable]"
	return
}

if (!(Test-Path $bthRegPath)){
	write-host "BTHPORT Registry path $bthRegPath not found !!!!"
	return
}

if ($option -eq "enable") {
	$bthRemWakeValue="1"
} else {
	$bthRemWakeValue="0"
}
New-ItemProperty -Path $bthRegPath -Name $bthRemWakeName -Value $bthRemWakeValue -PropertyType DWORD -Force | Out-Null
$needReboot=$true

foreach ($adapter in $IntelBTAdapterList) 
{
	Push-Location
	if (Test-Path "$bthUSBDevPath\$adapter")
	{
		Set-Location -Path "$bthUSBDevPath\$adapter"
		$devInst=Get-ChildItem -Name
		$fullDevParamPath="$bthUSBDevPath\$adapter\$devInst\Device Parameters"

		$Value=0
		if ($option -eq "enable") {
			$Value=1
		}	
		New-ItemProperty -Path $fullDevParamPath -Name $bthDevRWParam1 -Value $Value -PropertyType DWORD -Force | Out-Null
		New-ItemProperty -Path $fullDevParamPath -Name $bthDevRWParam2 -Value $Value -PropertyType DWORD -Force | Out-Null
	}
	Pop-Location
}
if ($needReboot) 
{
    write-host "" 
    write-host "Your Bluetooth Device Property has been changed; please power cycle the system for the change(s) to take effect"
}

# SIG # Begin signature block
# MIIZCQYJKoZIhvcNAQcCoIIY+jCCGPYCAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUlIUS8csrOZUggaDIxvfS3lzK
# 7m2gghZJMIIGKzCCBROgAwIBAgITMwAAsyJMoo9qTSqB7wACAACzIjANBgkqhkiG
# 9w0BAQUFADB5MQswCQYDVQQGEwJVUzELMAkGA1UECBMCQ0ExFDASBgNVBAcTC1Nh
# bnRhIENsYXJhMRowGAYDVQQKExFJbnRlbCBDb3Jwb3JhdGlvbjErMCkGA1UEAxMi
# SW50ZWwgRXh0ZXJuYWwgQmFzaWMgSXNzdWluZyBDQSAzQjAeFw0xNDA2MTEwMzQ2
# MDJaFw0xNzA1MjYwMzQ2MDJaMIGIMQswCQYDVQQGEwJVUzELMAkGA1UECBMCQ0Ex
# FDASBgNVBAcTC1NhbnRhIENsYXJhMRowGAYDVQQKExFJbnRlbCBDb3Jwb3JhdGlv
# bjE6MDgGA1UEAxMxSW50ZWwgQ29ycG9yYXRpb24tV2lyZWxlc3MgQ29ubmVjdGl2
# aXR5IFNvbHV0aW9uczCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAK1h
# bZD1ZL/LkmnX42WU5WcLJCpdQDPXpaMMlRn+G4+QJbbvTqX3KsDDL9u78fZo/ocq
# CbS3GJoy7A17ppQKnxeByj+s3hLQ4DIFreMVXteLytTGsBu3Q2rd2ng+9iSD6xfZ
# CtotD/x6MEQX1yiGscjGhVybwHBItxKqzZRobmarnftfqZtrs88LJDtSfgZnvlp/
# p+zyaNY6gxsQwd0EKYgC8jiDIxIGT6YBhLOudtx4T0+8Kpcs+4rDQbKrrvhHlGwX
# T4d06H/Nel7z+vmJt0lXcwmf90Ur+LzOYP3ri4SR01TqP7ovWPZqNIwX+24ks95q
# 6/rZWlhAoj4tV6thFt0CAwEAAaOCApowggKWMAsGA1UdDwQEAwIHgDA9BgkrBgEE
# AYI3FQcEMDAuBiYrBgEEAYI3FQiGw4x1hJnlUYP9gSiFjp9TgpHACWeE28M+h7We
# LQIBZAIBCjAdBgNVHQ4EFgQUIKGpHrk48ulTWVquTRkOQ4L9MeswHwYDVR0jBBgw
# FoAU5ZwArkMAvRpaSreJtueI0A53LSIwgc8GA1UdHwSBxzCBxDCBwaCBvqCBu4ZX
# aHR0cDovL3d3dy5pbnRlbC5jb20vcmVwb3NpdG9yeS9DUkwvSW50ZWwlMjBFeHRl
# cm5hbCUyMEJhc2ljJTIwSXNzdWluZyUyMENBJTIwM0IoMikuY3JshmBodHRwOi8v
# Y2VydGlmaWNhdGVzLmludGVsLmNvbS9yZXBvc2l0b3J5L0NSTC9JbnRlbCUyMEV4
# dGVybmFsJTIwQmFzaWMlMjBJc3N1aW5nJTIwQ0ElMjAzQigyKS5jcmwwgfUGCCsG
# AQUFBwEBBIHoMIHlMGwGCCsGAQUFBzAChmBodHRwOi8vd3d3LmludGVsLmNvbS9y
# ZXBvc2l0b3J5L2NlcnRpZmljYXRlcy9JbnRlbCUyMEV4dGVybmFsJTIwQmFzaWMl
# MjBJc3N1aW5nJTIwQ0ElMjAzQigyKS5jcnQwdQYIKwYBBQUHMAKGaWh0dHA6Ly9j
# ZXJ0aWZpY2F0ZXMuaW50ZWwuY29tL3JlcG9zaXRvcnkvY2VydGlmaWNhdGVzL0lu
# dGVsJTIwRXh0ZXJuYWwlMjBCYXNpYyUyMElzc3VpbmclMjBDQSUyMDNCKDIpLmNy
# dDAMBgNVHRMBAf8EAjAAMBMGA1UdJQQMMAoGCCsGAQUFBwMDMBsGCSsGAQQBgjcV
# CgQOMAwwCgYIKwYBBQUHAwMwDQYJKoZIhvcNAQEFBQADggEBACOKkmDia1kssdRD
# I7vY39icJ5nqEisUbPNcFawXuSqwpIe6FOnvjxhuV7RkR+OX3t9NgKdAdsPJOvXV
# qRUqZBkt7iImTJ6XjRXYn3Nw5uAasLnvb/43uyrOLZmuohqWJEXqUhJo/YfgtR0M
# A6+lWgmECIXUOUUlz/bjuzx9I+UDaOGhUXyGTPkXhxkdPp3ojFjKvmeJzNfAHpGG
# R0KtY7vAgWYX8/Wqdz5FTad5WvXBuFWUK/8D3OZG+7/WIECEMByOYXKNQynOd/aY
# /Fp5s2yfW11+B8qoLzV9+mEHmpAZTadfiOOXXUccgoi/thGuliJmnid39IA5+lvX
# RptcVPMwgga5MIIFoaADAgECAgphLP+IAAEAAAAQMA0GCSqGSIb3DQEBBQUAMFIx
# CzAJBgNVBAYTAlVTMRowGAYDVQQKExFJbnRlbCBDb3Jwb3JhdGlvbjEnMCUGA1UE
# AxMeSW50ZWwgRXh0ZXJuYWwgQmFzaWMgUG9saWN5IENBMB4XDTEzMDIwODIyMjEy
# M1oXDTE4MDIwODIyMzEyM1oweTELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAkNBMRQw
# EgYDVQQHEwtTYW50YSBDbGFyYTEaMBgGA1UEChMRSW50ZWwgQ29ycG9yYXRpb24x
# KzApBgNVBAMTIkludGVsIEV4dGVybmFsIEJhc2ljIElzc3VpbmcgQ0EgM0IwggEi
# MA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCwAJOu8spspk3MSL9KI/wqm8hu
# 7QuDB7E8Zzl1YoBtENGo8NanM6CY2IX6hc8K68n1vZsLtPe4s8Fk459gP9BLLZw/
# uz4f1ouKaKiTcf4w0uWXrO8ghhXqsfduQ39t8wCec6fXodSjWNttYcK+UWqjJPpv
# gCcyoBLYfJz2Rli2yB1hagWqhfco4QgpywKk33N2Kvsdrpi/69h/CRpiO7+xDgbL
# jIzi6sxFgbKV4/qH9KgX6uy/CA9/sUAPT3u86baqM+JkxkNvEq4YqXIEGuUmEBP3
# 4StRULAWnFIZFgokCga7Jt3wGtMdXjGs4MTnKrP7GJ/K0wXHnd1vammpsn6FAgMB
# AAGjggNoMIIDZDASBgkrBgEEAYI3FQEEBQIDAgACMCMGCSsGAQQBgjcVAgQWBBQG
# ZYumkqtDvEJakC31y5FolgZ5zzAdBgNVHQ4EFgQU5ZwArkMAvRpaSreJtueI0A53
# LSIwgfoGA1UdIASB8jCB7zCB7AYKKoZIhvhNAQUBaTCB3TCBnAYIKwYBBQUHAgIw
# gY8egYwASQBuAHQAZQBsACAAQwBvAHIAcABvAHIAYQB0AGkAbwBuACAARQB4AHQA
# ZQByAG4AYQBsACAAQgBhAHMAaQBjACAAUABvAGwAaQBjAHkAIABDAGUAcgB0AGkA
# ZgBpAGMAYQB0AGUAIABQAHIAYQBjAHQAaQBjAGUAIABTAHQAYQB0AGUAbQBlAG4A
# dDA8BggrBgEFBQcCARYwaHR0cDovL3d3dy5pbnRlbC5jb20vcmVwb3NpdG9yeS9w
# a2ljcHMvaW5kZXguaHRtMBkGCSsGAQQBgjcUAgQMHgoAUwB1AGIAQwBBMAsGA1Ud
# DwQEAwIBhjASBgNVHRMBAf8ECDAGAQH/AgEAMB8GA1UdIwQYMBaAFFY6bxerJAzl
# tzFksBHt2+ojvl68MIHDBgNVHR8EgbswgbgwgbWggbKgga+GUWh0dHA6Ly93d3cu
# aW50ZWwuY29tL3JlcG9zaXRvcnkvQ1JML0ludGVsJTIwRXh0ZXJuYWwlMjBCYXNp
# YyUyMFBvbGljeSUyMENBKDEpLmNybIZaaHR0cDovL2NlcnRpZmljYXRlcy5pbnRl
# bC5jb20vcmVwb3NpdG9yeS9DUkwvSW50ZWwlMjBFeHRlcm5hbCUyMEJhc2ljJTIw
# UG9saWN5JTIwQ0EoMSkuY3JsMIHpBggrBgEFBQcBAQSB3DCB2TBmBggrBgEFBQcw
# AoZaaHR0cDovL3d3dy5pbnRlbC5jb20vcmVwb3NpdG9yeS9jZXJ0aWZpY2F0ZXMv
# SW50ZWwlMjBFeHRlcm5hbCUyMEJhc2ljJTIwUG9saWN5JTIwQ0EoMSkuY3J0MG8G
# CCsGAQUFBzAChmNodHRwOi8vY2VydGlmaWNhdGVzLmludGVsLmNvbS9yZXBvc2l0
# b3J5L2NlcnRpZmljYXRlcy9JbnRlbCUyMEV4dGVybmFsJTIwQmFzaWMlMjBQb2xp
# Y3klMjBDQSgxKS5jcnQwDQYJKoZIhvcNAQEFBQADggEBAEe7k+YDsdlXDv9g6Q/H
# XobmI/fe+m3CdzLvI/aPzG8lctSpS60RonO7i9K3uIeUdIkMzFzqOprAdTqXWXwi
# AD16x8Vb6NSTE+yPlM2oM9+k15qhyNijtEl+FzoC6WZWl40WtHCrvGsQSOdFexPH
# TQW8oCwFFr4GfvZ5Z4+cNFTmfuoZdxTxnTtV5DOfabunpyJUUSxnfQRSqntm3qlq
# rYyhXHk5zRyF7IkGmYVGJ6ABV26TNlFF4Vo6Wa9bQflwncQWDgXnlbQBtJMaWQuK
# Mfe2SMhq9iKMnpIob6iTtKdyUzraLPrUPb8JI3/fzGUq0JGqUDHIZfU4WNSzm+Yx
# EAgwgglZMIIIQaADAgECAhB5F0qpFBc2/hWnyp8s/0WIMA0GCSqGSIb3DQEBBQUA
# MG8xCzAJBgNVBAYTAlNFMRQwEgYDVQQKEwtBZGRUcnVzdCBBQjEmMCQGA1UECxMd
# QWRkVHJ1c3QgRXh0ZXJuYWwgVFRQIE5ldHdvcmsxIjAgBgNVBAMTGUFkZFRydXN0
# IEV4dGVybmFsIENBIFJvb3QwHhcNMTMwMjAxMDAwMDAwWhcNMjAwNTMwMTA0ODM4
# WjBSMQswCQYDVQQGEwJVUzEaMBgGA1UEChMRSW50ZWwgQ29ycG9yYXRpb24xJzAl
# BgNVBAMTHkludGVsIEV4dGVybmFsIEJhc2ljIFBvbGljeSBDQTCCASIwDQYJKoZI
# hvcNAQEBBQADggEPADCCAQoCggEBAMK4hJVCLdywqpiTm7Psg6FjwxeSKoFpOpqC
# KG2Iz33sbWYmFOiNxH7wMKDcTw5DdlqMHKHFGTCWxHhKuXmwZLBZ8X9doAcZSFYi
# GMGQM7u2hb4QzMjykCNwvAhtGUgvQAWdRN7pnQNwhLnjTpj/0woTagpdt/gRtUG/
# zyZKQDvhn6VklYU3FedzH/3CrxR3Ixja8c3UqKvX8lu2uoH3BhEGNC1ZJsBVlHyd
# ME/JGni69BNLaM5CH6NNSjVjc7+jXGD/NEDgUQ5QKVrvTg5hFSRzw25ceI800NyS
# 2vuA7wTTo1VDqfpoEZo4ltKy3a8cDsSKiDsDY8HjAqf4YMV/4U0CAwEAAaOCBgww
# ggYIMB8GA1UdIwQYMBaAFK29mHo0tCb3+sQmVO8DveAky1QaMB0GA1UdDgQWBBRW
# Om8XqyQM5bcxZLAR7dvqI75evDAOBgNVHQ8BAf8EBAMCAYYwEgYDVR0TAQH/BAgw
# BgEB/wIBATBeBgNVHSUEVzBVBggrBgEFBQcDAQYIKwYBBQUHAwIGCCsGAQUFBwMD
# BggrBgEFBQcDBAYIKwYBBQUHAwgGCisGAQQBgjcKAwQGCisGAQQBgjcKAwwGCSsG
# AQQBgjcVBTAXBgNVHSAEEDAOMAwGCiqGSIb4TQEFAWkwSQYDVR0fBEIwQDA+oDyg
# OoY4aHR0cDovL2NybC50cnVzdC1wcm92aWRlci5jb20vQWRkVHJ1c3RFeHRlcm5h
# bENBUm9vdC5jcmwwgcIGCCsGAQUFBwEBBIG1MIGyMEQGCCsGAQUFBzAChjhodHRw
# Oi8vY3J0LnRydXN0LXByb3ZpZGVyLmNvbS9BZGRUcnVzdEV4dGVybmFsQ0FSb290
# LnA3YzA+BggrBgEFBQcwAoYyaHR0cDovL2NydC50cnVzdC1wcm92aWRlci5jb20v
# QWRkVHJ1c3RVVE5TR0NDQS5jcnQwKgYIKwYBBQUHMAGGHmh0dHA6Ly9vY3NwLnRy
# dXN0LXByb3ZpZGVyLmNvbTCCBBcGA1UdHgSCBA4wggQKoIID1DALgQlpbnRlbC5j
# b20wC4IJYXBwdXAuY29tMA6CDGNsb3VkbnBvLm9yZzATghFlZGFjYWR0b29sa2l0
# Lm9yZzALgglmdGwxMC5jb20wC4IJaWhjbXMubmV0MA6CDGluYy1uZXN0Lm5ldDAW
# ghRpbmRpYWVkdXNlcnZpY2VzLmNvbTANggtpbnRlbC5jby5qcDANggtpbnRlbC5j
# by5rcjANggtpbnRlbC5jby51azALgglpbnRlbC5jb20wCoIIaW50ZWwuZnIwC4IJ
# aW50ZWwubmV0MBOCEWludGVsYWxsaWFuY2UuY29tMBSCEmludGVsYXBhY3N0b3Jl
# LmNvbTAWghRpbnRlbGFzc2V0ZmluZGVyLmNvbTAZghdpbnRlbGJldHRlcnRvZ2V0
# aGVyLmNvbTAUghJpbnRlbGNoYWxsZW5nZS5jb20wE4IRaW50ZWxjbG91ZHNzby5j
# b20wHoIcaW50ZWxjb25zdW1lcmVsZWN0cm9uaWNzLmNvbTASghBpbnRlbGNvcmUy
# MDEwLnJ1MBaCFGludGVsZmVsbG93c2hpcHMuY29tMBaCFGludGVsaHlicmlkY2xv
# dWQuY29tMBSCEmludGVscG9ydGZvbGlvLmNvbTAOggxpbnRlbC1yYS5jb20wFIIS
# aW50ZWwtcmVzZWFyY2gubmV0MBSCEmludGVscm1hc3VydmV5LmNvbTAYghZpbnRl
# bHNtYWxsYnVzaW5lc3MuY29tMBGCD215aW50ZWxlZGdlLmNvbTARgg9teS1sYXB0
# b3AuY28udWswEoIQb3JpZ2luLWFwcHVwLmNvbTAeghxvcmlnaW4taW50ZWdyYXRp
# b24tYXBwdXAuY29tMAiCBnBjLmNvbTAUghJwY3RoZWZ0ZGVmZW5jZS5jb20wFIIS
# cGN0aGVmdGRlZmVuc2UuY29tMA6CDHB2YXRyaWFsLm5ldDAZghdyZWRlZmluZXlv
# dXJuZXR3b3JrLmNvbTAPgg1yZXRhaWwtaWEuY29tMBSCEnNlcnZlci1pbnNpZ2h0
# LmNvbTATghF0aGVpbnRlbHN0b3JlLmNvbTAdght0aHJlYWRpbmdidWlsZGluZ2Js
# b2Nrcy5vcmcwG4IZdGh1bmRlcmJvbHR0ZWNobm9sb2d5Lm5ldDAggh51bHRyYWJv
# b2stc29mdHdhcmUtY29udGVzdC5jb20wUKROMEwxCzAJBgNVBAYTAlVTMQswCQYD
# VQQIEwJDQTEUMBIGA1UEBxMLU2FudGEgQ2xhcmExGjAYBgNVBAoTEUludGVsIENv
# cnBvcmF0aW9uoTAwCocIAAAAAAAAAAAwIocgAAAAAAAAAAAAAAAAAAAAAAAAAAAA
# AAAAAAAAAAAAAAAwDQYJKoZIhvcNAQEFBQADggEBAFhvv81DB0IT/LjQrYEh8opv
# 74e8Jop8AL1oDCsZZCwRZ7Op2XkKrDldZQAWO1NGbqKmtWeZ2+i/oiWuBJURCTov
# 3qy3Pbi8AXQwgEdIVEyg+2uouKKEt/Q05XvO3FJ49DFtQlGuh7+UrL6WFvtV5XmC
# ZP2sUDjk3MuBLOd3b52bI1x9BAP0B55+1FfiZpRN67VcXGKejC2D5kYU4qETgP3a
# 4IYnEZIrvYcXT8sZGEtejOYN2Y99I3ZvpP+guj3jbTfWJjjoGpwjkshWHxoajgDW
# M6ZrlfqCHnQLD6SG3yMzfJ42FLNc4qPtSKCOKPHXTPbAm7T1PKPlqGOiLAil1f4x
# ggIqMIICJgIBATCBkDB5MQswCQYDVQQGEwJVUzELMAkGA1UECBMCQ0ExFDASBgNV
# BAcTC1NhbnRhIENsYXJhMRowGAYDVQQKExFJbnRlbCBDb3Jwb3JhdGlvbjErMCkG
# A1UEAxMiSW50ZWwgRXh0ZXJuYWwgQmFzaWMgSXNzdWluZyBDQSAzQgITMwAAsyJM
# oo9qTSqB7wACAACzIjAJBgUrDgMCGgUAoHAwEAYKKwYBBAGCNwIBDDECMAAwGQYJ
# KoZIhvcNAQkDMQwGCisGAQQBgjcCAQQwHAYKKwYBBAGCNwIBCzEOMAwGCisGAQQB
# gjcCARUwIwYJKoZIhvcNAQkEMRYEFGy9aP9OosmPriOcyOdQ/JygZs4HMA0GCSqG
# SIb3DQEBAQUABIIBAKJ9L2rbeVRdllE5PTsYD52Gk/N8pylIa6cxK4oSzLHKJQ+u
# CyKrdik/2JX2k9Xn/KKa1xwJEdFhsNVA0WP06sTkfW97xl6oavYrrhMa8vEt4jHJ
# lEjzZpIQI2l0UH40bcpgpmhB/UJua7Jl01BAYHqpwjPf75/D1nFx3+6qW3SobU1s
# X1Ic23wOwwZKXCggpTGHHfK7b/JMsRlFF5Z2dqr6egndmz6N21Gzt6BYSXAj4JB9
# Ev5gvE3L99LxNoVFPNhGDq4MHSGa+WM2yriZFZVowlH+Lj+TOUW/pq8IFJ5eahrC
# DpaytVLy7MpexsHnLEM1xmbLymFDuQ+wtZU6UsI=
# SIG # End signature block

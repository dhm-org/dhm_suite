@echo off
@echo Uninstalling Intel (R) Wireless Bluetooth (R) drivers in silent mode now...
Pushd "%~dp0"
dir /b /s *.inf > temp.txt
for /f "tokens=*" %%F in (temp.txt) do (
DPInst.exe /sw /q /u "%%F"
)
@del temp.txt
@echo "Uninstall done ....."
@pause

@echo off

cd /d "%~dp0"

py serial_client.py --stdin

pause
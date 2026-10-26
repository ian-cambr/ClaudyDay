@echo off
rem Double-click to open Claudy Day with your live Claude Code stats. Close this window to stop it.
title Claudy Day
python "%~dp0serve.py" %*
if errorlevel 1 pause

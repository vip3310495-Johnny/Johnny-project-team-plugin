@echo off
setlocal EnableExtensions

rem Prefer the Python executable supplied by Codex, then standard Windows launchers.
if defined CODEX_PYTHON if exist "%CODEX_PYTHON%" (
  "%CODEX_PYTHON%" "%~1"
  exit /b %ERRORLEVEL%
)
where py >nul 2>nul && (
  py -3 "%~1"
  exit /b %ERRORLEVEL%
)
where python3 >nul 2>nul && (
  python3 "%~1"
  exit /b %ERRORLEVEL%
)
where python >nul 2>nul && (
  python "%~1"
  exit /b %ERRORLEVEL%
)

echo Johnny hook could not find Python. Set CODEX_PYTHON to Codex's Python executable, or install Python 3 and make python available. 1>&2
exit /b 0

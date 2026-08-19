@echo off
setlocal EnableExtensions

rem Prefer the Python executable supplied by Codex, then standard Windows launchers.
if defined CODEX_PYTHON if exist "%CODEX_PYTHON%" (
  "%CODEX_PYTHON%" "%~1"
  exit /b %ERRORLEVEL%
)
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "%~1"
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

rem Without Python, remain fail-open only when no enabled Johnny repository is in scope.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0johnny_python_fallback.ps1"
exit /b %ERRORLEVEL%

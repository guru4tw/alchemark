@echo off
REM ============================================================
REM  Alchemark batch convert (Windows wrapper)
REM
REM  Usage:
REM    batch_convert.bat                       Scan current dir
REM    batch_convert.bat C:\path\to\folder     Scan specific folder
REM    batch_convert.bat C:\in -o C:\out       Forward extra flags
REM
REM  Defaults applied: --recursive --preserve-images
REM  Output:           <input>\md
REM  Log:              <input>\log\batch_convert_YYYYMMDD_HHMMSS.log
REM ============================================================

setlocal EnableDelayedExpansion

REM Force UTF-8 codepage so Chinese / Japanese filenames are not mangled.
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"

REM Locate batch_convert.py and project root.
REM   .bat lives at  <project>\scripts\batch_convert.bat
REM   project root = one level up from scripts\
set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%batch_convert.py"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

if not exist "%PY_SCRIPT%" (
    echo ERROR: cannot find "%PY_SCRIPT%"
    echo        ^(this .bat must live next to batch_convert.py^)
    pause
    exit /b 2
)

REM First positional arg = input folder; the rest forward to Python script.
set "INPUT=."
if not "%~1"=="" (
    set "INPUT=%~1"
    shift
)

REM ----------------------------------------------------------------
REM  Pick a Python interpreter.
REM    1. Active venv (VIRTUAL_ENV)
REM    2. The "py" launcher (py -3)
REM    3. python on PATH
REM ----------------------------------------------------------------
set "PYEXE="
set "PY_SOURCE="
if defined VIRTUAL_ENV (
    if exist "%VIRTUAL_ENV%\Scripts\python.exe" (
        set "PYEXE=%VIRTUAL_ENV%\Scripts\python.exe"
        set "PY_SOURCE=active venv"
    )
)
if not defined PYEXE (
    where py >nul 2>nul && (
        set "PYEXE=py -3"
        set "PY_SOURCE=py launcher"
    )
)
if not defined PYEXE (
    where python >nul 2>nul && (
        set "PYEXE=python"
        set "PY_SOURCE=python on PATH"
    )
)
if not defined PYEXE (
    echo.
    echo ====================================================================
    echo  ERROR: no Python interpreter found
    echo ====================================================================
    echo  Tried, in order:
    echo    1^) %%VIRTUAL_ENV%%\Scripts\python.exe   ^(VIRTUAL_ENV not set^)
    echo    2^) py -3                                ^(launcher not on PATH^)
    echo    3^) python                                ^(not on PATH^)
    echo.
    echo  Install Python 3.9+ from https://python.org/downloads/
    echo  ^(check "Add Python to PATH" during install^), then re-run this .bat.
    echo.
    pause
    exit /b 2
)

REM ----------------------------------------------------------------
REM  Capture full diagnostics about the chosen interpreter.
REM ----------------------------------------------------------------
set "PYPATH="
set "PYVER="
for /f "delims=" %%v in ('%PYEXE% -c "import sys; print(sys.executable)" 2^>nul') do set "PYPATH=%%v"
for /f "delims=" %%v in ('%PYEXE% -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2^>nul') do set "PYVER=%%v"
if not defined PYPATH set "PYPATH=^(unknown^)"
if not defined PYVER set "PYVER=^(unknown^)"

REM ----------------------------------------------------------------
REM  Verify alchemark is importable.
REM  Capture the import error so we can show the actual failure reason.
REM ----------------------------------------------------------------
set "IMPORT_ERR_FILE=%TEMP%\alchemark_import_err_%RANDOM%.txt"
%PYEXE% -c "import alchemark; import sys; print(getattr(alchemark, '__version__', '?'))" 1>"%IMPORT_ERR_FILE%.out" 2>"%IMPORT_ERR_FILE%"
set "ALCHEMARK_RC=%ERRORLEVEL%"

if "%ALCHEMARK_RC%" NEQ "0" (
    REM ---------- Detailed error report ----------
    echo.
    echo ====================================================================
    echo  ERROR: 'alchemark' is not importable from this Python environment
    echo ====================================================================
    echo  Python interpreter : !PYPATH!
    echo  Picked from        : !PY_SOURCE!
    echo  Python version     : !PYVER!
    if defined VIRTUAL_ENV (
        echo  Active venv        : %VIRTUAL_ENV%
    ) else (
        echo  Active venv        : ^(none^)
    )
    echo  Project root       : !PROJECT_ROOT!
    echo  Script being run   : %PY_SCRIPT%
    echo.
    echo  --- Actual import error ---
    if exist "%IMPORT_ERR_FILE%" type "%IMPORT_ERR_FILE%"
    echo  ---------------------------
    echo.
    echo  How to fix
    echo  ----------
    echo  Option A^)  Install alchemark into THIS Python interpreter:
    echo.
    echo                "!PYPATH!" -m pip install -e "!PROJECT_ROOT!"[all]
    echo.
    echo  Option B^)  Activate the venv that ALREADY has alchemark, then re-run:
    echo.
    echo                call ^<venv_path^>\Scripts\activate.bat
    echo                "%~f0" %*
    echo.
    echo  Option C^)  Set VIRTUAL_ENV to that venv's path before launching this .bat:
    echo.
    echo                set "VIRTUAL_ENV=^<venv_path^>"
    echo                "%~f0" %*
    echo.
    echo  Quick check ^(Powershell or cmd^):
    echo     "!PYPATH!" -m pip show alchemark
    echo ====================================================================
    if exist "%IMPORT_ERR_FILE%"     del "%IMPORT_ERR_FILE%"     2>nul
    if exist "%IMPORT_ERR_FILE%.out" del "%IMPORT_ERR_FILE%.out" 2>nul
    if not defined CI pause
    endlocal & exit /b 2
)

REM Read installed alchemark version for the banner.
set "ALCHEMARK_VER="
if exist "%IMPORT_ERR_FILE%.out" (
    set /p ALCHEMARK_VER=<"%IMPORT_ERR_FILE%.out"
)
if exist "%IMPORT_ERR_FILE%"     del "%IMPORT_ERR_FILE%"     2>nul
if exist "%IMPORT_ERR_FILE%.out" del "%IMPORT_ERR_FILE%.out" 2>nul

REM ----------------------------------------------------------------
REM  Banner + run
REM ----------------------------------------------------------------
echo.
echo ====================================================================
echo  Alchemark batch convert
echo ====================================================================
echo  Input folder    : %INPUT%
echo  Python          : !PYPATH! ^(!PYVER!^)
echo  alchemark       : !ALCHEMARK_VER!
echo  Defaults        : --recursive --preserve-images
echo  Extra args      : %*
echo ====================================================================
echo.

%PYEXE% "%PY_SCRIPT%" -i "%INPUT%" --recursive --preserve-images %*
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo [OK] All files converted successfully.
) else (
    echo [FAIL] Conversion finished with errors. Exit code: %RC%
    echo        See the log file printed above for full detail.
)
echo.

if not defined CI pause

endlocal & exit /b %RC%

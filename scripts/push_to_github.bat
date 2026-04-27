@echo off
REM ============================================================
REM  push_to_github.bat — one-shot uploader for guru4tw/alchemark
REM
REM  What it does (all idempotent — safe to re-run):
REM    1. Cleans __pycache__, .pytest_cache, .mypy_cache, .ruff_cache,
REM       dist/, build/, *.coverage, *_images, docs/claude-skills, *.bundle.
REM    2. Initialises git (if not already initialised) on branch `main`.
REM    3. Stages all tracked files, makes a commit if there's something to commit.
REM    4. Tags v0.1.0 (only if not already present).
REM    5. Adds the GitHub remote (https://github.com/guru4tw/alchemark.git)
REM       if not already configured.
REM    6. Pushes main + tags.
REM
REM  Prerequisites:
REM    * git installed and on PATH
REM    * empty repo already created at https://github.com/guru4tw/alchemark
REM      (no README / no .gitignore / no LICENSE — they're already in the project)
REM    * GitHub Personal Access Token (PAT) ready when prompted for password
REM      https://github.com/settings/tokens?type=beta
REM        - Repository access: only this repo
REM        - Permission: Contents = Read and write
REM ============================================================

setlocal EnableDelayedExpansion

chcp 65001 >nul

REM Locate project root: this .bat lives at <project>\scripts\push_to_github.bat
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

set "REPO_URL=https://github.com/guru4tw/alchemark.git"
set "REPO_BRANCH=main"
set "RELEASE_TAG=v0.1.0"
set "COMMIT_MSG=Initial release: Alchemark v0.1.0"

echo.
echo ====================================================================
echo  Push Alchemark to GitHub
echo ====================================================================
echo  Project root : %PROJECT_ROOT%
echo  Remote URL   : %REPO_URL%
echo  Branch       : %REPO_BRANCH%
echo  Tag          : %RELEASE_TAG%
echo ====================================================================
echo.

REM Sanity: git installed?
where git >nul 2>nul
if errorlevel 1 (
    echo ERROR: git is not on PATH.
    echo Install Git for Windows from https://git-scm.com/download/win and re-run.
    pause
    exit /b 2
)

cd /d "%PROJECT_ROOT%"
if errorlevel 1 (
    echo ERROR: cannot cd to project root: %PROJECT_ROOT%
    pause
    exit /b 2
)

REM ----------------------------------------------------------------
REM  Step 1: Clean up local-only artefacts
REM ----------------------------------------------------------------
echo [1/6] Cleaning local caches and build artefacts...
for %%D in (
    __pycache__
    .pytest_cache
    .mypy_cache
    .ruff_cache
    build
    dist
    pytest-cache-files-po1pi5jx
    docs\claude-skills
) do (
    if exist "%%D" rmdir /s /q "%%D" 2>nul
)
REM Recursively remove any lingering __pycache__ / *_images dirs
for /d /r %%D in (__pycache__) do @if exist "%%D" rmdir /s /q "%%D" 2>nul
for /d /r %%D in (*_images) do @if exist "%%D" rmdir /s /q "%%D" 2>nul
del /q .coverage .coverage.* coverage.xml 2>nul
del /q *.bundle 2>nul
del /q scripts\*.patch 2>nul
echo    done.
echo.

REM ----------------------------------------------------------------
REM  Step 2: Initialise git if needed
REM ----------------------------------------------------------------
echo [2/6] Initialising git repository...
if exist ".git" (
    echo    already a git repo — skipping git init.
) else (
    git init -b %REPO_BRANCH%
    if errorlevel 1 (
        echo ERROR: git init failed.
        pause
        exit /b 1
    )
)
git config user.name  "guru4tw"        >nul 2>nul
git config user.email "joe.idv@gmail.com" >nul 2>nul
echo.

REM ----------------------------------------------------------------
REM  Step 3: Stage + commit (only if there's something to commit)
REM ----------------------------------------------------------------
echo [3/6] Staging files...
git add -A
echo.
echo    Files to be committed:
git diff --cached --name-only
echo.

git diff --cached --quiet
if %ERRORLEVEL%==0 (
    echo    nothing new to commit — skipping commit.
) else (
    echo [4/6] Committing...
    git commit -m "%COMMIT_MSG%"
    if errorlevel 1 (
        echo ERROR: git commit failed.
        pause
        exit /b 1
    )
)
echo.

REM ----------------------------------------------------------------
REM  Step 5: Tag if not already tagged
REM ----------------------------------------------------------------
echo [5/6] Tagging %RELEASE_TAG%...
git rev-parse %RELEASE_TAG% >nul 2>nul
if %ERRORLEVEL%==0 (
    echo    tag %RELEASE_TAG% already exists — skipping.
) else (
    git tag -a %RELEASE_TAG% -m "%RELEASE_TAG% — initial public release"
)
echo.

REM ----------------------------------------------------------------
REM  Step 6: Add remote + push
REM ----------------------------------------------------------------
echo [6/6] Configuring remote 'origin'...
git remote get-url origin >nul 2>nul
if %ERRORLEVEL%==0 (
    for /f "delims=" %%U in ('git remote get-url origin') do set "EXISTING_URL=%%U"
    if /I "!EXISTING_URL!"=="%REPO_URL%" (
        echo    origin already points to %REPO_URL%.
    ) else (
        echo    origin currently points to !EXISTING_URL!
        echo    re-pointing to %REPO_URL%...
        git remote set-url origin %REPO_URL%
    )
) else (
    git remote add origin %REPO_URL%
)
echo.

echo ====================================================================
echo  Ready to push.  When prompted for credentials:
echo    Username: guru4tw
echo    Password: ^<your GitHub Personal Access Token^>
echo  Get a PAT at: https://github.com/settings/tokens?type=beta
echo ====================================================================
echo.
choice /M "Proceed with 'git push' now?"
if errorlevel 2 (
    echo Aborted by user. Repo is staged and ready — push manually with:
    echo     git push -u origin %REPO_BRANCH%
    echo     git push --tags
    pause
    exit /b 0
)

echo.
echo Pushing main...
git push -u origin %REPO_BRANCH%
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
    echo.
    echo ERROR: push failed ^(exit %RC%^).
    echo Common causes:
    echo   * The GitHub repo doesn't exist yet ^^- create it at:
    echo         https://github.com/new   ^(name: alchemark, owner: guru4tw, EMPTY^)
    echo   * Wrong username / token, or token lacks 'Contents: write' permission.
    echo   * Repo on GitHub already has commits ^^- run:  git pull --rebase origin main
    pause
    exit /b %RC%
)

echo.
echo Pushing tags...
git push --tags
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
    echo WARNING: tag push failed; main was pushed OK.
)

echo.
echo ====================================================================
echo  [OK] Done. View at: https://github.com/guru4tw/alchemark
echo ====================================================================

if not defined CI pause
endlocal & exit /b 0

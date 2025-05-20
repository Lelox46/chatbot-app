@echo off
setlocal

:: === KONFIGURATION ===
set ENV_DIR=.venv
set PYTHON_EXE=%ENV_DIR%\Scripts\python.exe
set CONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
set CONDA_INSTALLER=miniconda_installer.exe
set CONDA_TARGET=miniconda

:: === CHECK: Python vorhanden? ===
where python >nul 2>nul
if %errorlevel%==0 (
    echo [INFO] System-Python gefunden.
    set PYTHON=python
    goto CHECK_ENV
)

:: === CHECK: Bereits installierte portable Python-Umgebung? ===
if exist "%PYTHON_EXE%" (
    echo [INFO] Lokales Python gefunden.
    set PYTHON=%PYTHON_EXE%
    goto CHECK_ENV
)

echo [INFO] Python nicht gefunden. Miniconda wird heruntergeladen...

:: === Miniconda downloaden ===
curl -L -o %CONDA_INSTALLER% %CONDA_URL%
if not exist %CONDA_INSTALLER% (
    echo [FEHLER] Download von Miniconda fehlgeschlagen.
    pause
    exit /b 1
)

:: === Miniconda installieren ===
echo [INFO] Installiere Miniconda...
start /wait "" %CONDA_INSTALLER% /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=%CD%\%CONDA_TARGET%

:: === Erstelle venv ===
echo [INFO] Erstelle virtuelles Environment...
call %CONDA_TARGET%\Scripts\activate.bat
%CONDA_TARGET%\python.exe -m venv %ENV_DIR%
del %CONDA_INSTALLER%
set PYTHON=%PYTHON_EXE%

:: === ENV AKTIVIEREN & PACKAGES INSTALLIEREN ===
:CHECK_ENV
echo [INFO] Stelle sicher, dass pip und streamlit vorhanden sind...
"%PYTHON%" -m ensurepip --upgrade >nul 2>nul
"%PYTHON%" -m pip install --upgrade pip >nul
"%PYTHON%" -m pip install streamlit >nul

:: === Starte Streamlit-App ===
echo [INFO] Starte Streamlit App...
"%PYTHON%" -m streamlit run app2.py

pause


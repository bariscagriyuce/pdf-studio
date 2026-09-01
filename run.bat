@echo off
REM PDF Studio - Windows baslatici.
REM Ilk calistirmada sanal ortami kurar, sonrakilerde dogrudan acar.
setlocal
cd /d "%~dp0"

set "VPY=.venv\Scripts\python.exe"

if not exist "%VPY%" (
    echo Sanal ortam olusturuluyor...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if not exist "%VPY%" (
        echo Python bulunamadi. https://www.python.org/downloads/ adresinden kurun.
        pause
        exit /b 1
    )
    "%VPY%" -m pip install --upgrade pip
    "%VPY%" -m pip install -r requirements.txt
)

"%VPY%" -c "import PySide6, pymupdf" 2>nul || "%VPY%" -m pip install -r requirements.txt

"%VPY%" -m pdfstudio %*

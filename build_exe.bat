@echo off
echo Dang cai dat/cap nhat PyInstaller...
pip install pyinstaller

echo Dang dong goi file EXE...
pyinstaller --noconfirm --onefile --windowed --name "FBReportTool" --clean --paths "FBReportHelper" FBReportHelper/main.py

echo.
echo Xong! File EXE nam trong thu muc 'dist'.
pause

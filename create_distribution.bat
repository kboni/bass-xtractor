@echo off
echo Creating Bass Extractor GUI distribution package...
echo.

REM Create distribution folder
if not exist "BassExtractorGUI_Distribution" mkdir "BassExtractorGUI_Distribution"

REM Copy executable
echo Copying executable...
copy "dist\BassExtractorGUI.exe" "BassExtractorGUI_Distribution\"

REM Copy installer script
echo Copying installer script...
copy "install_dependencies.bat" "BassExtractorGUI_Distribution\"

REM Copy README
echo Copying README...
copy "EXECUTABLE_README.txt" "BassExtractorGUI_Distribution\"

REM Create a simple run script
echo Creating run script...
echo @echo off > "BassExtractorGUI_Distribution\run_gui.bat"
echo echo Starting Bass Extractor GUI... >> "BassExtractorGUI_Distribution\run_gui.bat"
echo BassExtractorGUI.exe >> "BassExtractorGUI_Distribution\run_gui.bat"
echo pause >> "BassExtractorGUI_Distribution\run_gui.bat"

echo.
echo Distribution package created in "BassExtractorGUI_Distribution" folder
echo.
echo Contents:
echo   - BassExtractorGUI.exe (main executable)
echo   - install_dependencies.bat (dependency installer)
echo   - EXECUTABLE_README.txt (usage instructions)
echo   - run_gui.bat (simple launcher)
echo.
echo Ready to distribute!
pause 
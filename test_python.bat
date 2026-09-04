@echo off
setlocal

echo Running Python connect tests ...
echo.

cd test\python
python test_connect.py
set "FAILED=%ERRORLEVEL%"
cd ..\..

echo.
if "%FAILED%"=="0" (
    echo Python tests PASSED.
) else (
    echo Python tests FAILED.
)

endlocal
exit /b %FAILED%

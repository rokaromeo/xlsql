@echo off
setlocal

echo Running PHP connect tests ...
echo.

php test\php\test_connect.php
set "FAILED=%ERRORLEVEL%"

echo.
if "%FAILED%"=="0" (
    echo PHP tests PASSED.
) else (
    echo PHP tests FAILED.
)

endlocal
exit /b %FAILED%

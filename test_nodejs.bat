@echo off
setlocal

echo Running Node.js connect tests ...
echo.

cd test\nodejs
if not exist node_modules call npm install >nul
call npm test
set "FAILED=%ERRORLEVEL%"
cd ..\..

echo.
if "%FAILED%"=="0" (
    echo Node.js tests PASSED.
) else (
    echo Node.js tests FAILED.
)

endlocal
exit /b %FAILED%

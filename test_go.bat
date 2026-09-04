@echo off
setlocal

echo Running Go connect tests ...
echo.

cd test\go
go run .
set "FAILED=%ERRORLEVEL%"
cd ..\..

echo.
if "%FAILED%"=="0" (
    echo Go tests PASSED.
) else (
    echo Go tests FAILED.
)

endlocal
exit /b %FAILED%

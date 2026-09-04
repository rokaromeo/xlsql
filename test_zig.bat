@echo off
setlocal

echo Running Zig connect tests ...
echo.

cd test\zig
zig build run
set "FAILED=%ERRORLEVEL%"
cd ..\..

echo.
if "%FAILED%"=="0" (
    echo Zig tests PASSED.
) else (
    echo Zig tests FAILED.
)

endlocal
exit /b %FAILED%

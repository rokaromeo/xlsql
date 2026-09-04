@echo off
setlocal

echo Running Rust connect tests ...
echo.

cd test\rust
cargo run --quiet
set "FAILED=%ERRORLEVEL%"
cd ..\..

echo.
if "%FAILED%"=="0" (
    echo Rust tests PASSED.
) else (
    echo Rust tests FAILED.
)

endlocal
exit /b %FAILED%

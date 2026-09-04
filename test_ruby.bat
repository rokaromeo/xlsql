@echo off
setlocal

echo Running Ruby connect tests ...
echo.

cd test\ruby
call bundle exec ruby connect_test.rb
set "FAILED=%ERRORLEVEL%"
cd ..\..

echo.
if "%FAILED%"=="0" (
    echo Ruby tests PASSED.
) else (
    echo Ruby tests FAILED.
)

endlocal
exit /b %FAILED%

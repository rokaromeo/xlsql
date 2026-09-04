@echo off
setlocal enabledelayedexpansion

set "HOST=127.0.0.1"
set "PORT=5432"
set "DATA=build\python\data.xlsx"

echo ========================================
echo  xlsql test runner
echo ========================================
echo.

echo [1/2] Starting xlsql server on %HOST%:%PORT% ...
powershell -NoProfile -Command "$p = Start-Process -FilePath python -ArgumentList 'server.py --host %HOST% --port %PORT% --data %DATA%' -PassThru; Set-Content -Path .%PORT%.srvpid -Value $p.Id"
set /p SRVPID=<.%PORT%.srvpid
del .%PORT%.srvpid 2>nul

echo Server process PID: %SRVPID%
echo Waiting for server to accept connections ...

set "READY="
for /l %%i in (1,1,30) do (
    powershell -NoProfile -Command "try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('%HOST%', %PORT%); $c.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
    if not errorlevel 1 (
        set "READY=1"
        goto :ready
    )
    timeout /t 1 /nobreak >nul
)

echo Server did not start in time. Aborting.
if defined SRVPID (
    echo Stopping xlsql server process %SRVPID% ...
    taskkill /pid %SRVPID% /f >nul 2>&1
)
exit /b 1

:ready
echo Server is up.
echo.
echo [2/2] Running client connect tests ...
echo.

set "FAILED=0"

echo --- Python ---
cd test\python
python test_connect.py
if errorlevel 1 set "FAILED=1"
cd ..\..
echo.

echo --- Node.js ---
cd test\nodejs
if not exist node_modules call npm install >nul
call npm test
if errorlevel 1 set "FAILED=1"
cd ..\..
echo.

echo --- PHP ---
php test\php\test_connect.php
if errorlevel 1 set "FAILED=1"
echo.

echo --- Ruby ---
cd test\ruby
call bundle exec ruby connect_test.rb
if errorlevel 1 set "FAILED=1"
cd ..\..
echo.

echo --- Go ---
cd test\go
go run .
if errorlevel 1 set "FAILED=1"
cd ..\..
echo.

echo --- Rust ---
cd test\rust
cargo run --quiet
if errorlevel 1 set "FAILED=1"
cd ..\..
echo.

echo.
echo ========================================
if "%FAILED%"=="1" (
    echo Some tests FAILED.
) else (
    echo All tests PASSED.
)
echo ========================================

echo.
echo Stopping xlsql server %SRVPID% ...
if defined SRVPID taskkill /pid %SRVPID% /f >nul 2>&1
echo Done.

endlocal
exit /b %FAILED%

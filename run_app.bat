@echo off
REM 
    cd /d --> legal-AI Directory here <--

REM 
call myenv\Scripts\activate

REM 
start "" python app-public\app_public.py

REM 
timeout /t 2 /nobreak > NUL

REM 
start "" "http://localhost:8001"

REM 
deactivate

@echo off
REM Script de inicialização do Sistema de Ordem de Serviço (Windows)

REM Verifica se Python está disponível
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python não encontrado. Instale o Python 3.10+ do site oficial: https://python.org
    pause
    exit /b 1
)

REM Verifica versão do Python
for /f "tokens=2" %%i in ('python --version') do set PY_VER=%%i
for /f "tokens=1 delims=." %%i in ("%PY_VER%") do set PY_MAJOR=%%i
for /f "tokens=2 delims=." %%i in ("%PY_VER%") do set PY_MINOR=%%i

if %PY_MAJOR% lss 3 (
    echo Python 3.10+ necessário. Versão atual: %PY_VER%
    pause
    exit /b 1
)
if %PY_MAJOR% equ 3 if %PY_MINOR% lss 10 (
    echo Python 3.10+ necessário. Versão atual: %PY_VER%
    pause
    exit /b 1
)

REM Verifica se PyQt6 está instalado
python -c "import PyQt6" 2>nul
if %errorlevel% neq 0 (
    echo PyQt6 não encontrado. Instalando...
    python -m pip install PyQt6 --user
    if %errorlevel% neq 0 (
        echo Erro ao instalar PyQt6. Tente executar como administrador.
        pause
        exit /b 1
    )
)

REM Executa a aplicação
cd /d "%~dp0"
python main.py
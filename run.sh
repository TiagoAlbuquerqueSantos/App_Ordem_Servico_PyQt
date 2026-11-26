#!/bin/bash
# Script de inicialização do Sistema de Ordem de Serviço

# Detecta Python disponível
PYTHON_CMD=""

if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "Python 3.10+ não encontrado. Instale o Python primeiro."
    exit 1
fi

# Verifica se PyQt6 está instalado
if ! $PYTHON_CMD -c "import PyQt6" 2>/dev/null; then
    echo "PyQt6 não encontrado. Instalando..."
    $PYTHON_CMD -m pip install PyQt6 --user
fi

# Executa a aplicação
cd "$(dirname "$0")"
exec $PYTHON_CMD main.py
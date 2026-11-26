#!/usr/bin/env python3
"""
Sistema de Ordem de Serviço - PyQt6
Aplicação desktop para gestão de ordens de serviço
"""

import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.main_window import MainWindow
from database.connection import init_database


def main():
    """Função principal da aplicação"""
    # Inicializa o banco de dados
    init_database()
    
    # Cria a aplicação Qt
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    
    # Configurações de alta DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Ordem de Serviço")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("OS Manager")
    
    # Carrega estilo (o MainWindow irá aplicar o tema salvo)
    # Não carregamos estilo aqui para evitar flash de tema errado
    
    # Cria e mostra a janela principal
    window = MainWindow()
    window.show()
    
    # Executa a aplicação
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
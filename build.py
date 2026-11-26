#!/usr/bin/env python3
"""
Build script para criar executável com PyInstaller (opcional)
"""

import subprocess
import os


def build_executable():
    """Cria executável standalone"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(script_dir, "main.py")

    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--name=OrdemServico",
        "--windowed",
        "--onefile",
        "--icon=res/icon.ico" if os.path.exists(os.path.join(script_dir, "res/icon.ico")) else "",
        "--add-data=res/style.qss:res",
        "--hidden-import=PyQt6.QtPrintSupport",
        "--hidden-import=sqlite3",
        main_py
    ]

    # Remove empty strings
    cmd = [c for c in cmd if c]

    print("Executando:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=script_dir)

    if result.returncode == 0:
        print("\nBuild concluído com sucesso!")
        print(f"Executável em: {script_dir}/dist/OrdemServico")
    else:
        print("\nErro no build.")


if __name__ == "__main__":
    build_executable()

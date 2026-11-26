#!/usr/bin/env python3
"""
Widgets personalizados
"""

from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen


class StatusBadge(QLabel):
    """Badge colorido para status da OS"""
    
    CORES = {
        'ABERTA': '#3498db',
        'EM_ANDAMENTO': '#f39c12',
        'AGUARDANDO_PECAS': '#e74c3c',
        'AGUARDANDO_APROVACAO': '#9b59b6',
        'CONCLUIDA': '#27ae60',
        'ENTREGUE': '#2c3e50',
        'CANCELADA': '#95a5a6',
        '': '#bdc3c7'
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(120)
        self.setMaximumWidth(150)
        self.setStyleSheet("""
            QLabel {
                border-radius: 12px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 11px;
                color: white;
            }
        """)
        self._status = ""
    
    def set_status(self, status: str):
        """Define o status e atualiza cor"""
        self._status = status
        cor = self.CORES.get(status, '#bdc3c7')
        self.setText(status if status else "-")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {cor};
                border-radius: 12px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 11px;
                color: white;
            }}
        """)


class PrioridadeBadge(QLabel):
    """Badge para prioridade"""
    
    CORES = {
        'URGENTE': '#e74c3c',
        'ALTA': '#e67e22',
        'NORMAL': '#f39c12',
        'BAIXA': '#27ae60',
        '': '#bdc3c7'
    }
    
    ICONES = {
        'URGENTE': '🔴',
        'ALTA': '🟠',
        'NORMAL': '🟡',
        'BAIXA': '🟢',
        '': '⚪'
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(100)
        self.setStyleSheet("""
            QLabel {
                border-radius: 10px;
                padding: 3px 10px;
                font-weight: bold;
                font-size: 10px;
                color: white;
            }
        """)
        self._prioridade = ""
    
    def set_prioridade(self, prioridade: str):
        self._prioridade = prioridade
        cor = self.CORES.get(prioridade, '#bdc3c7')
        icone = self.ICONES.get(prioridade, '⚪')
        self.setText(f"{icone} {prioridade}" if prioridade else "-")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {cor};
                border-radius: 10px;
                padding: 3px 10px;
                font-weight: bold;
                font-size: 10px;
                color: white;
            }}
        """)


class MoneyEdit(QWidget):
    """Widget para edição de valores monetários"""
    
    def __init__(self, parent=None, valor: float = 0.0):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        from PyQt6.QtWidgets import QDoubleSpinBox
        self.spin = QDoubleSpinBox()
        self.spin.setDecimals(2)
        self.spin.setMaximum(999999.99)
        self.spin.setPrefix("R$ ")
        self.spin.setValue(valor)
        self.spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.UpDownArrows)
        
        layout.addWidget(self.spin)
    
    def value(self) -> float:
        return self.spin.value()
    
    def setValue(self, valor: float):
        self.spin.setValue(valor)
    
    def setReadOnly(self, readonly: bool):
        self.spin.setReadOnly(readonly)
        self.spin.setButtonSymbols(
            QDoubleSpinBox.ButtonSymbols.NoButtons if readonly else QDoubleSpinBox.ButtonSymbols.UpDownArrows
        )
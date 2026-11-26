#!/usr/bin/env python3
"""
Janela Principal da Aplicação
"""

import os
from typing import Optional, List

from PyQt6.QtCore import Qt, QDate, QTimer, QSize, QSettings
from PyQt6.QtGui import QAction, QFont, QColor, QBrush, QPalette
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QLineEdit, QComboBox, QDateEdit, QLabel, QMessageBox,
    QToolBar, QStatusBar, QMenu, QDialog, QFormLayout,
    QTextEdit, QSplitter, QFrame, QScrollArea, QAbstractItemView
)

from models import (
    OrdemServico, OSItem, STATUS_OS,
    PRIORIDADES
)
from repositories import (
    ClienteRepository, EquipamentoRepository, OrdemServicoRepository
)
from ui.dialogs import (
    ClienteDialog, EquipamentoDialog, OrdemServicoDialog,
    OSDetalhesDialog, RelatorioDialog, ConfiguracoesDialog
)
from ui.widgets import StatusBadge, PrioridadeBadge


class MainWindow(QMainWindow):
    """Janela principal do sistema"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Ordem de Serviço v1.0")
        self.resize(1400, 800)

        # Repositórios
        self.cliente_repo = ClienteRepository()
        self.equipamento_repo = EquipamentoRepository()
        self.os_repo = OrdemServicoRepository()

        # Estado
        self.os_selecionada: Optional[OrdemServico] = None
        self.pagina_atual = 1
        self.por_pagina = 50
        self.filtros_ativos = {}

        # Configurações de tema
        self.settings = QSettings("OrdemServico", "OSManager")
        self.tema_atual = self.settings.value("tema", "dark")  # dark por padrão

        self._setup_ui()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_shortcuts()
        self._carregar_tema()
        self._carregar_dados_iniciais()

        # Timer para auto-refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._atualizar_estatisticas)
        self.refresh_timer.start(30000)  # 30 segundos

    def _setup_ui(self):
        """Configura a interface principal"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)

        # Área superior - Filtros e Tabela de OS
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)

        # Barra de filtros
        self._criar_barra_filtros(top_layout)

        # Tabela de Ordens de Serviço
        self.tabela_os = QTableWidget()
        self._configurar_tabela_os()
        top_layout.addWidget(self.tabela_os)

        # Paginação
        self._criar_paginacao(top_layout)

        splitter.addWidget(top_widget)

        # Área inferior - Detalhes da OS selecionada
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # Abas de detalhes
        self.tabs_detalhes = QTabWidget()
        bottom_layout.addWidget(self.tabs_detalhes)

        # Aba Informações Gerais
        self._criar_aba_info_gerais()

        # Aba Itens (Peças/Serviços)
        self._criar_aba_itens()

        # Aba Histórico
        self._criar_aba_historico()

        splitter.addWidget(bottom_widget)
        splitter.setSizes([500, 300])

        # Conecta sinais
        self.tabela_os.itemSelectionChanged.connect(self._on_selecao_os)
        self.tabela_os.doubleClicked.connect(self._on_double_click_os)

    def _criar_barra_filtros(self, parent_layout):
        """Cria a barra de filtros superior"""
        filtros_frame = QFrame()
        filtros_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        filtros_layout = QHBoxLayout(filtros_frame)
        filtros_layout.setContentsMargins(10, 5, 10, 5)

        # Busca geral
        filtros_layout.addWidget(QLabel("Busca:"))
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Número OS, Cliente, Descrição, Técnico...")
        self.input_busca.setMinimumWidth(250)
        self.input_busca.returnPressed.connect(self._aplicar_filtros)
        filtros_layout.addWidget(self.input_busca)

        # Status
        filtros_layout.addWidget(QLabel("Status:"))
        self.combo_status = QComboBox()
        self.combo_status.addItem("Todos", "")
        for status in STATUS_OS:
            self.combo_status.addItem(status, status)
        self.combo_status.currentIndexChanged.connect(self._aplicar_filtros)
        filtros_layout.addWidget(self.combo_status)

        # Prioridade
        filtros_layout.addWidget(QLabel("Prioridade:"))
        self.combo_prioridade = QComboBox()
        self.combo_prioridade.addItem("Todas", "")
        for p in PRIORIDADES:
            self.combo_prioridade.addItem(p, p)
        self.combo_prioridade.currentIndexChanged.connect(self._aplicar_filtros)
        filtros_layout.addWidget(self.combo_prioridade)

        # Data início
        filtros_layout.addWidget(QLabel("De:"))
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate.currentDate().addDays(-30))
        self.date_inicio.dateChanged.connect(self._aplicar_filtros)
        filtros_layout.addWidget(self.date_inicio)

        # Data fim
        filtros_layout.addWidget(QLabel("Até:"))
        self.date_fim = QDateEdit()
        self.date_fim.setCalendarPopup(True)
        self.date_fim.setDate(QDate.currentDate())
        self.date_fim.dateChanged.connect(self._aplicar_filtros)
        filtros_layout.addWidget(self.date_fim)

        # Botão limpar filtros
        btn_limpar = QPushButton("Limpar")
        btn_limpar.clicked.connect(self._limpar_filtros)
        filtros_layout.addWidget(btn_limpar)

        filtros_layout.addStretch()

        # Estatísticas rápidas
        self.label_stats = QLabel("Carregando...")
        self.label_stats.setStyleSheet("font-weight: bold; color: #2c3e50;")
        filtros_layout.addWidget(self.label_stats)

        parent_layout.addWidget(filtros_frame)

    def _configurar_tabela_os(self):
        """Configura a tabela de ordens de serviço"""
        colunas = [
            ("Nº OS", 120), ("Cliente", 200), ("Equipamento", 180),
            ("Status", 100), ("Prioridade", 80), ("Técnico", 120),
            ("Abertura", 100), ("Previsão", 100), ("Valor Total", 100)
        ]

        self.tabela_os.setColumnCount(len(colunas))
        self.tabela_os.setHorizontalHeaderLabels([c[0] for c in colunas])

        header = self.tabela_os.horizontalHeader()
        for i, (_, width) in enumerate(colunas):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            self.tabela_os.setColumnWidth(i, width)
        header.setStretchLastSection(True)

        self.tabela_os.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_os.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela_os.setAlternatingRowColors(True)
        self.tabela_os.setSortingEnabled(True)
        self.tabela_os.verticalHeader().setVisible(False)
        self.tabela_os.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def _criar_paginacao(self, parent_layout):
        """Cria controles de paginação"""
        pag_frame = QFrame()
        pag_layout = QHBoxLayout(pag_frame)
        pag_layout.setContentsMargins(10, 5, 10, 5)

        self.btn_primeira = QPushButton("« Primeira")
        self.btn_anterior = QPushButton("‹ Anterior")
        self.btn_proxima = QPushButton("Próxima ›")
        self.btn_ultima = QPushButton("Última »")

        self.btn_primeira.clicked.connect(lambda: self._ir_para_pagina(1))
        self.btn_anterior.clicked.connect(lambda: self._ir_para_pagina(self.pagina_atual - 1))
        self.btn_proxima.clicked.connect(lambda: self._ir_para_pagina(self.pagina_atual + 1))
        self.btn_ultima.clicked.connect(self._ir_para_ultima_pagina)

        self.label_pagina = QLabel("Página 1 de 1")
        self.label_pagina.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_pagina.setMinimumWidth(150)

        self.combo_por_pagina = QComboBox()
        self.combo_por_pagina.addItems(["25", "50", "100", "200"])
        self.combo_por_pagina.setCurrentText("50")
        self.combo_por_pagina.currentTextChanged.connect(self._alterar_por_pagina)

        pag_layout.addWidget(self.btn_primeira)
        pag_layout.addWidget(self.btn_anterior)
        pag_layout.addWidget(self.label_pagina)
        pag_layout.addWidget(self.btn_proxima)
        pag_layout.addWidget(self.btn_ultima)
        pag_layout.addStretch()
        pag_layout.addWidget(QLabel("Por página:"))
        pag_layout.addWidget(self.combo_por_pagina)

        parent_layout.addWidget(pag_frame)

    def _criar_aba_info_gerais(self):
        """Cria aba de informações gerais da OS"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Scroll area para muitos campos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QFormLayout(scroll_content)
        scroll_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Campos de informação (read-only)
        self.lbl_numero_os = QLabel("-")
        self.lbl_numero_os.setFont(QFont("Monospace", 10, QFont.Weight.Bold))
        scroll_layout.addRow("Nº OS:", self.lbl_numero_os)

        self.lbl_cliente = QLabel("-")
        scroll_layout.addRow("Cliente:", self.lbl_cliente)

        self.lbl_equipamento = QLabel("-")
        scroll_layout.addRow("Equipamento:", self.lbl_equipamento)

        self.badge_status = StatusBadge()
        scroll_layout.addRow("Status:", self.badge_status)

        self.badge_prioridade = PrioridadeBadge()
        scroll_layout.addRow("Prioridade:", self.badge_prioridade)

        self.lbl_tecnico = QLabel("-")
        scroll_layout.addRow("Técnico:", self.lbl_tecnico)

        self.lbl_data_abertura = QLabel("-")
        scroll_layout.addRow("Abertura:", self.lbl_data_abertura)

        self.lbl_data_previsao = QLabel("-")
        scroll_layout.addRow("Previsão Entrega:", self.lbl_data_previsao)

        self.lbl_data_conclusao = QLabel("-")
        scroll_layout.addRow("Conclusão:", self.lbl_data_conclusao)

        self.lbl_data_entrega = QLabel("-")
        scroll_layout.addRow("Entrega:", self.lbl_data_entrega)

        self.lbl_valor_pecas = QLabel("R$ 0,00")
        scroll_layout.addRow("Peças:", self.lbl_valor_pecas)

        self.lbl_valor_mao_obra = QLabel("R$ 0,00")
        scroll_layout.addRow("Mão de Obra:", self.lbl_valor_mao_obra)

        self.lbl_valor_total = QLabel("R$ 0,00")
        self.lbl_valor_total.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.lbl_valor_total.setStyleSheet("color: #27ae60;")
        scroll_layout.addRow("Total:", self.lbl_valor_total)

        # Text areas
        self.txt_descricao = QTextEdit()
        self.txt_descricao.setReadOnly(True)
        self.txt_descricao.setMaximumHeight(80)
        scroll_layout.addRow("Descrição do Serviço:", self.txt_descricao)

        self.txt_diagnostico = QTextEdit()
        self.txt_diagnostico.setReadOnly(True)
        self.txt_diagnostico.setMaximumHeight(80)
        scroll_layout.addRow("Diagnóstico:", self.txt_diagnostico)

        self.txt_solucao = QTextEdit()
        self.txt_solucao.setReadOnly(True)
        self.txt_solucao.setMaximumHeight(80)
        scroll_layout.addRow("Solução Aplicada:", self.txt_solucao)

        self.txt_observacoes = QTextEdit()
        self.txt_observacoes.setReadOnly(True)
        self.txt_observacoes.setMaximumHeight(60)
        scroll_layout.addRow("Observações:", self.txt_observacoes)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.tabs_detalhes.addTab(widget, "📋 Informações")

    def _criar_aba_itens(self):
        """Cria aba de itens (peças/serviços)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar de itens
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))

        self.btn_add_item = QPushButton("➕ Adicionar Item")
        self.btn_add_item.clicked.connect(self._adicionar_item)
        toolbar.addWidget(self.btn_add_item)

        self.btn_edit_item = QPushButton("✏️ Editar")
        self.btn_edit_item.clicked.connect(self._editar_item)
        self.btn_edit_item.setEnabled(False)
        toolbar.addWidget(self.btn_edit_item)

        self.btn_del_item = QPushButton("🗑️ Excluir")
        self.btn_del_item.clicked.connect(self._excluir_item)
        self.btn_del_item.setEnabled(False)
        toolbar.addWidget(self.btn_del_item)

        toolbar.addSeparator()

        self.lbl_total_itens = QLabel("Total: R$ 0,00")
        self.lbl_total_itens.setStyleSheet("font-weight: bold; padding: 0 10px;")
        toolbar.addWidget(self.lbl_total_itens)

        layout.addWidget(toolbar)

        # Tabela de itens
        self.tabela_itens = QTableWidget()
        self.tabela_itens.setColumnCount(6)
        self.tabela_itens.setHorizontalHeaderLabels([
            "Tipo", "Descrição", "Qtd", "Vl. Unit.", "Vl. Total", "ID"
        ])
        self.tabela_itens.setColumnHidden(5, True)  # ID oculto
        self.tabela_itens.horizontalHeader().setStretchLastSection(True)
        self.tabela_itens.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_itens.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_itens.itemSelectionChanged.connect(self._on_selecao_item)

        layout.addWidget(self.tabela_itens)

        self.tabs_detalhes.addTab(widget, "📦 Itens (Peças/Serviços)")

    def _criar_aba_historico(self):
        """Cria aba de histórico da OS"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.tabela_historico = QTableWidget()
        self.tabela_historico.setColumnCount(5)
        self.tabela_historico.setHorizontalHeaderLabels([
            "Data/Hora", "Status Anterior", "Novo Status", "Descrição", "Usuário"
        ])
        self.tabela_historico.horizontalHeader().setStretchLastSection(True)
        self.tabela_historico.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.tabela_historico)

        self.tabs_detalhes.addTab(widget, "📜 Histórico")

    def _setup_toolbar(self):
        """Configura a toolbar principal"""
        toolbar = QToolBar("Principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Nova OS
        action_nova = QAction("➕ Nova OS", self)
        action_nova.setShortcut("Ctrl+N")
        action_nova.triggered.connect(self._nova_os)
        toolbar.addAction(action_nova)

        # Novo Cliente
        action_cliente = QAction("👤 Novo Cliente", self)
        action_cliente.setShortcut("Ctrl+Shift+C")
        action_cliente.triggered.connect(self._novo_cliente)
        toolbar.addAction(action_cliente)

        # Novo Equipamento
        action_equip = QAction("💻 Novo Equipamento", self)
        action_equip.setShortcut("Ctrl+Shift+E")
        action_equip.triggered.connect(self._novo_equipamento)
        toolbar.addAction(action_equip)

        toolbar.addSeparator()

        # Editar OS
        self.action_editar = QAction("✏️ Editar OS", self)
        self.action_editar.setShortcut("Ctrl+E")
        self.action_editar.setEnabled(False)
        self.action_editar.triggered.connect(self._editar_os)
        toolbar.addAction(self.action_editar)

        # Duplicar OS
        self.action_duplicar = QAction("📋 Duplicar", self)
        self.action_duplicar.setEnabled(False)
        self.action_duplicar.triggered.connect(self._duplicar_os)
        toolbar.addAction(self.action_duplicar)

        # Excluir OS
        self.action_excluir = QAction("🗑️ Excluir", self)
        self.action_excluir.setShortcut("Delete")
        self.action_excluir.setEnabled(False)
        self.action_excluir.triggered.connect(self._excluir_os)
        toolbar.addAction(self.action_excluir)

        toolbar.addSeparator()

        # Ações rápidas de status
        self.menu_status = QMenu(self)
        for status in STATUS_OS:
            action = QAction(status, self)
            action.triggered.connect(lambda checked, s=status: self._alterar_status_rapido(s))
            self.menu_status.addAction(action)

        self.btn_status_rapido = QPushButton("🔄 Alterar Status ▼")
        self.btn_status_rapido.setMenu(self.menu_status)
        self.btn_status_rapido.setEnabled(False)
        toolbar.addWidget(self.btn_status_rapido)

        toolbar.addSeparator()

        # Imprimir/Exportar
        action_imprimir = QAction("🖨️ Imprimir OS", self)
        action_imprimir.setShortcut("Ctrl+P")
        action_imprimir.triggered.connect(self._imprimir_os)
        toolbar.addAction(action_imprimir)

        action_exportar = QAction("📊 Exportar", self)
        action_exportar.triggered.connect(self._exportar_dados)
        toolbar.addAction(action_exportar)

        toolbar.addSeparator()

        # Relatórios
        action_relatorios = QAction("📈 Relatórios", self)
        action_relatorios.triggered.connect(self._abrir_relatorios)
        toolbar.addAction(action_relatorios)

        # Configurações
        action_config = QAction("⚙️ Configurações", self)
        action_config.triggered.connect(self._abrir_configuracoes)
        toolbar.addAction(action_config)

        # Refresh
        action_refresh = QAction("🔄 Atualizar", self)
        action_refresh.setShortcut("F5")
        action_refresh.triggered.connect(self._carregar_os)
        toolbar.addAction(action_refresh)

        toolbar.addSeparator()

        # Seletor de Tema
        self.btn_tema = QPushButton("🌙 Tema Escuro" if self.tema_atual == "dark" else "☀️ Tema Claro")
        self.btn_tema.setCheckable(True)
        self.btn_tema.setChecked(self.tema_atual == "dark")
        self.btn_tema.clicked.connect(self._alternar_tema)
        self.btn_tema.setToolTip("Alternar entre tema claro e escuro")
        toolbar.addWidget(self.btn_tema)

    def _setup_statusbar(self):
        """Configura a barra de status"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.lbl_status_geral = QLabel("Pronto")
        self.statusBar.addWidget(self.lbl_status_geral, 1)

        self.lbl_total_registros = QLabel("Total: 0")
        self.statusBar.addPermanentWidget(self.lbl_total_registros)

        self.lbl_versao = QLabel("v1.0.0")
        self.statusBar.addPermanentWidget(self.lbl_versao)

    def _setup_shortcuts(self):
        """Configura atalhos de teclado"""
        from PyQt6.QtGui import QShortcut, QKeySequence

        # F5 - Atualizar
        QShortcut(QKeySequence("F5"), self, self._carregar_os)

        # Escape - Limpar seleção
        QShortcut(QKeySequence("Escape"), self, self._limpar_selecao)

        # Enter - Editar OS selecionada
        QShortcut(QKeySequence("Return"), self, self._editar_os_selecionada)

    def _carregar_tema(self):
        """Carrega e aplica o tema salvo"""
        self._aplicar_tema(self.tema_atual)

    def _alternar_tema(self, checked: bool):
        """Alterna entre tema claro e escuro"""
        novo_tema = "dark" if checked else "light"
        self.tema_atual = novo_tema
        self.settings.setValue("tema", novo_tema)
        self._aplicar_tema(novo_tema)
        self.btn_tema.setText("🌙 Tema Escuro" if novo_tema == "dark" else "☀️ Tema Claro")
        self.statusBar.showMessage(f"Tema alterado para {'escuro' if novo_tema == 'dark' else 'claro'}", 2000)

    def _aplicar_tema(self, tema: str):
        """Aplica o tema especificado"""
        app = self.qApp if hasattr(self, 'qApp') else None
        if not app:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()

        if tema == "dark":
            style_path = os.path.join(os.path.dirname(__file__), "../..", "res", "style_dark.qss")
        else:
            style_path = os.path.join(os.path.dirname(__file__), "../..", "res", "style.qss")

        style_path = os.path.normpath(style_path)

        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        else:
            # Fallback: estilo básico programático
            if tema == "dark":
                self._aplicar_tema_dark_programatico(app)
            else:
                app.setStyleSheet("")

    def _aplicar_tema_dark_programatico(self, app):
        """Aplica tema escuro básico via código (fallback)"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 46))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(205, 214, 244))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 56))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 46))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(30, 30, 46))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(205, 214, 244))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(205, 214, 244))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(40, 40, 56))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(205, 214, 244))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(243, 139, 168))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(137, 180, 250))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(137, 180, 250))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(30, 30, 46))
        app.setPalette(dark_palette)

    def _carregar_dados_iniciais(self):
        """Carrega dados iniciais ao abrir"""
        self._carregar_os()
        self._atualizar_estatisticas()
        self.statusBar.showMessage("Sistema carregado com sucesso", 3000)

    def _carregar_os(self):
        """Carrega lista de OS com filtros atuais"""
        self.lbl_status_geral.setText("Carregando ordens de serviço...")

        # Prepara filtros
        status = self.combo_status.currentData()
        prioridade = self.combo_prioridade.currentData()
        data_inicio = self.date_inicio.date().toPyDate()
        data_fim = self.date_fim.date().toPyDate()
        termo = self.input_busca.text().strip()

        try:
            ordens, total = self.os_repo.listar(
                status=status,
                data_inicio=data_inicio,
                data_fim=data_fim,
                termo_busca=termo,
                pagina=self.pagina_atual,
                por_pagina=self.por_pagina
            )

            self._popular_tabela_os(ordens)
            self._atualizar_paginacao(total)
            self.lbl_status_geral.setText(f"{len(ordens)} ordem(ns) carregada(s) - Total: {total}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar OS: {str(e)}")
            self.lbl_status_geral.setText("Erro ao carregar")

    def _popular_tabela_os(self, ordens: List[OrdemServico]):
        """Preenche a tabela com as OS"""
        self.tabela_os.setRowCount(len(ordens))

        for row, os in enumerate(ordens):
            # Nº OS
            item = QTableWidgetItem(os.numero_os)
            item.setData(Qt.ItemDataRole.UserRole, os.id)
            self.tabela_os.setItem(row, 0, item)

            # Cliente
            self.tabela_os.setItem(row, 1, QTableWidgetItem(os.cliente_nome))

            # Equipamento
            self.tabela_os.setItem(row, 2, QTableWidgetItem(os.equipamento_descricao))

            # Status (com badge colorido)
            status_item = QTableWidgetItem(os.status)
            status_item.setForeground(QBrush(QColor(os.status_cor)))
            status_item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            self.tabela_os.setItem(row, 3, status_item)

            # Prioridade
            prioridade_item = QTableWidgetItem(os.prioridade)
            cores_prio = {'URGENTE': '#e74c3c', 'ALTA': '#e67e22', 'NORMAL': '#f39c12', 'BAIXA': '#27ae60'}
            prioridade_item.setForeground(QBrush(QColor(cores_prio.get(os.prioridade, '#34495e'))))
            self.tabela_os.setItem(row, 4, prioridade_item)

            # Técnico
            self.tabela_os.setItem(row, 5, QTableWidgetItem(os.tecnico_responsavel or "-"))

            # Data abertura
            data_ab = os.data_abertura.strftime("%d/%m/%Y %H:%M") if os.data_abertura else "-"
            self.tabela_os.setItem(row, 6, QTableWidgetItem(data_ab))

            # Data previsão
            data_prev = os.data_previsao_entrega.strftime("%d/%m/%Y") if os.data_previsao_entrega else "-"
            self.tabela_os.setItem(row, 7, QTableWidgetItem(data_prev))

            # Valor total
            valor_item = QTableWidgetItem(
                f"R$ {os.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            valor_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabela_os.setItem(row, 8, valor_item)

    def _atualizar_paginacao(self, total: int):
        """Atualiza controles de paginação"""
        total_paginas = max(1, (total + self.por_pagina - 1) // self.por_pagina)
        self.label_pagina.setText(f"Página {self.pagina_atual} de {total_paginas} ({total} registros)")

        self.btn_primeira.setEnabled(self.pagina_atual > 1)
        self.btn_anterior.setEnabled(self.pagina_atual > 1)
        self.btn_proxima.setEnabled(self.pagina_atual < total_paginas)
        self.btn_ultima.setEnabled(self.pagina_atual < total_paginas)

    def _ir_para_pagina(self, pagina: int):
        """Navega para página específica"""
        if pagina < 1:
            return
        self.pagina_atual = pagina
        self._carregar_os()

    def _ir_para_ultima_pagina(self):
        """Vai para última página (precisa saber total)"""
        # Para simplificar, vamos apenas carregar a última página possível
        # Em uma implementação real, faríamos uma query de count primeiro
        pass

    def _alterar_por_pagina(self, texto: str):
        """Altera quantidade por página"""
        self.por_pagina = int(texto)
        self.pagina_atual = 1
        self._carregar_os()

    def _aplicar_filtros(self):
        """Aplica filtros e recarrega"""
        self.pagina_atual = 1
        self._carregar_os()

    def _limpar_filtros(self):
        """Limpa todos os filtros"""
        self.input_busca.clear()
        self.combo_status.setCurrentIndex(0)
        self.combo_prioridade.setCurrentIndex(0)
        self.date_inicio.setDate(QDate.currentDate().addDays(-30))
        self.date_fim.setDate(QDate.currentDate())
        self.pagina_atual = 1
        self._carregar_os()

    def _on_selecao_os(self):
        """Chamado quando seleção da tabela muda"""
        selected = self.tabela_os.selectedItems()
        has_selection = len(selected) > 0

        self.action_editar.setEnabled(has_selection)
        self.action_duplicar.setEnabled(has_selection)
        self.action_excluir.setEnabled(has_selection)
        self.btn_status_rapido.setEnabled(has_selection)

        if has_selection:
            row = selected[0].row()
            os_id = self.tabela_os.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self._carregar_detalhes_os(os_id)
        else:
            self._limpar_detalhes()

    def _on_double_click_os(self):
        """Duplo clique na OS - edita"""
        self._editar_os()

    def _carregar_detalhes_os(self, os_id: int):
        """Carrega detalhes da OS selecionada"""
        os = self.os_repo.buscar_por_id(os_id)
        if not os:
            return

        self.os_selecionada = os

        # Info gerais
        self.lbl_numero_os.setText(os.numero_os)
        self.lbl_cliente.setText(os.cliente_nome)
        self.lbl_equipamento.setText(os.equipamento_descricao)
        self.badge_status.set_status(os.status)
        self.badge_prioridade.set_prioridade(os.prioridade)
        self.lbl_tecnico.setText(os.tecnico_responsavel or "-")

        self.lbl_data_abertura.setText(os.data_abertura.strftime("%d/%m/%Y %H:%M") if os.data_abertura else "-")
        self.lbl_data_previsao.setText(
            os.data_previsao_entrega.strftime("%d/%m/%Y") if os.data_previsao_entrega else "-")
        self.lbl_data_conclusao.setText(os.data_conclusao.strftime("%d/%m/%Y %H:%M") if os.data_conclusao else "-")
        self.lbl_data_entrega.setText(os.data_entrega.strftime("%d/%m/%Y %H:%M") if os.data_entrega else "-")

        self.lbl_valor_pecas.setText(f"R$ {os.valor_pecas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_valor_mao_obra.setText(
            f"R$ {os.valor_mao_obra:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_valor_total.setText(f"R$ {os.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        self.txt_descricao.setPlainText(os.descricao_servico or "-")
        self.txt_diagnostico.setPlainText(os.diagnostico or "-")
        self.txt_solucao.setPlainText(os.solucao_aplicada or "-")
        self.txt_observacoes.setPlainText(os.observacoes or "-")

        # Itens
        self._popular_tabela_itens(os.itens)

        # Histórico
        self._popular_tabela_historico(os.id)

    def _popular_tabela_itens(self, itens: List[OSItem]):
        """Preenche tabela de itens"""
        self.tabela_itens.setRowCount(len(itens))

        total_pecas = 0
        total_servicos = 0

        for row, item in enumerate(itens):
            self.tabela_itens.setItem(row, 0, QTableWidgetItem(item.tipo))
            self.tabela_itens.setItem(row, 1, QTableWidgetItem(item.descricao))

            qtd_item = QTableWidgetItem(str(item.quantidade))
            qtd_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabela_itens.setItem(row, 2, qtd_item)

            vl_unit = QTableWidgetItem(
                f"R$ {item.valor_unitario:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            vl_unit.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabela_itens.setItem(row, 3, vl_unit)

            vl_total = QTableWidgetItem(
                f"R$ {item.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            vl_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            vl_total.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            self.tabela_itens.setItem(row, 4, vl_total)

            # ID oculto
            id_item = QTableWidgetItem(str(item.id or 0))
            self.tabela_itens.setItem(row, 5, id_item)

            if item.tipo == 'PECA':
                total_pecas += item.valor_total
            else:
                total_servicos += item.valor_total

        self.lbl_total_itens.setText(
            f"Peças: R$ {total_pecas:,.2f} | Serviços: R$ {total_servicos:,.2f} | Total: R$ {total_pecas + total_servicos:,.2f}"
            .replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def _popular_tabela_historico(self, os_id: int):
        """Preenche tabela de histórico"""
        from repositories import OSHistoricoRepository
        hist_repo = OSHistoricoRepository()
        historico = hist_repo.buscar_por_os(os_id)

        self.tabela_historico.setRowCount(len(historico))

        for row, h in enumerate(historico):
            data_str = h.data_movimentacao.strftime("%d/%m/%Y %H:%M") if h.data_movimentacao else "-"
            self.tabela_historico.setItem(row, 0, QTableWidgetItem(data_str))
            self.tabela_historico.setItem(row, 1, QTableWidgetItem(h.status_anterior or "-"))

            # Novo status colorido
            status_item = QTableWidgetItem(h.status_novo)
            # Usar cores similares ao status
            status_item.setForeground(
                QBrush(QColor('#27ae60' if h.status_novo in ['CONCLUIDA', 'ENTREGUE'] else '#3498db')))
            self.tabela_historico.setItem(row, 2, status_item)

            self.tabela_historico.setItem(row, 3, QTableWidgetItem(h.descricao or "-"))
            self.tabela_historico.setItem(row, 4, QTableWidgetItem(h.usuario or "Sistema"))

    def _limpar_detalhes(self):
        """Limpa painel de detalhes"""
        self.os_selecionada = None
        self.lbl_numero_os.setText("-")
        self.lbl_cliente.setText("-")
        self.lbl_equipamento.setText("-")
        self.badge_status.set_status("")
        self.badge_prioridade.set_prioridade("")
        self.lbl_tecnico.setText("-")
        self.lbl_data_abertura.setText("-")
        self.lbl_data_previsao.setText("-")
        self.lbl_data_conclusao.setText("-")
        self.lbl_data_entrega.setText("-")
        self.lbl_valor_pecas.setText("R$ 0,00")
        self.lbl_valor_mao_obra.setText("R$ 0,00")
        self.lbl_valor_total.setText("R$ 0,00")
        self.txt_descricao.clear()
        self.txt_diagnostico.clear()
        self.txt_solucao.clear()
        self.txt_observacoes.clear()
        self.tabela_itens.setRowCount(0)
        self.tabela_historico.setRowCount(0)
        self.lbl_total_itens.setText("Total: R$ 0,00")

    def _on_selecao_item(self):
        """Seleção de item na tabela de itens"""
        has_sel = len(self.tabela_itens.selectedItems()) > 0
        self.btn_edit_item.setEnabled(has_sel)
        self.btn_del_item.setEnabled(has_sel)

    def _atualizar_estatisticas(self):
        """Atualiza estatísticas na barra de filtros"""
        try:
            stats = self.os_repo.obter_estatisticas()
            partes = []
            for status in ['ABERTA', 'EM_ANDAMENTO', 'AGUARDANDO_PECAS', 'AGUARDANDO_APROVACAO', 'CONCLUIDA']:
                if status in stats['por_status']:
                    partes.append(f"{status}: {stats['por_status'][status]}")
            self.label_stats.setText(" | ".join(partes) if partes else "Sem dados")
        except Exception:
            pass

    # === AÇÕES DA TOOLBAR ===

    def _nova_os(self):
        """Abre dialog para nova OS"""
        dialog = OrdemServicoDialog(self, cliente_repo=self.cliente_repo, equipamento_repo=self.equipamento_repo)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            os = dialog.get_ordem_servico()
            try:
                self.os_repo.criar(os)
                self._carregar_os()
                self.statusBar.showMessage(f"OS {os.numero_os} criada com sucesso!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao criar OS: {str(e)}")

    def _novo_cliente(self):
        """Abre dialog para novo cliente"""
        dialog = ClienteDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            cliente = dialog.get_cliente()
            try:
                self.cliente_repo.criar(cliente)
                self.statusBar.showMessage(f"Cliente {cliente.nome} cadastrado!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao cadastrar cliente: {str(e)}")

    def _novo_equipamento(self):
        """Abre dialog para novo equipamento"""
        # Precisa selecionar cliente primeiro
        clientes = self.cliente_repo.buscar_todos()
        if not clientes:
            QMessageBox.warning(self, "Aviso", "Cadastre um cliente primeiro!")
            return

        dialog = EquipamentoDialog(self, clientes=clientes)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            equip = dialog.get_equipamento()
            try:
                self.equipamento_repo.criar(equip)
                self.statusBar.showMessage(f"Equipamento cadastrado!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao cadastrar equipamento: {str(e)}")

    def _editar_os(self):
        """Edita OS selecionada"""
        if not self.os_selecionada:
            return

        dialog = OrdemServicoDialog(self, os=self.os_selecionada,
                                    cliente_repo=self.cliente_repo,
                                    equipamento_repo=self.equipamento_repo)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            os_atualizada = dialog.get_ordem_servico()
            try:
                self.os_repo.atualizar(os_atualizada)
                self._carregar_os()
                self.statusBar.showMessage(f"OS {os_atualizada.numero_os} atualizada!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao atualizar OS: {str(e)}")

    def _editar_os_selecionada(self):
        """Atalho Enter para editar"""
        if self.os_selecionada and self.action_editar.isEnabled():
            self._editar_os()

    def _duplicar_os(self):
        """Duplica OS selecionada"""
        if not self.os_selecionada:
            return

        # Cria cópia
        nova_os = OrdemServico(
            cliente_id=self.os_selecionada.cliente_id,
            equipamento_id=self.os_selecionada.equipamento_id,
            status='ABERTA',
            prioridade=self.os_selecionada.prioridade,
            tecnico_responsavel=self.os_selecionada.tecnico_responsavel,
            descricao_servico=self.os_selecionada.descricao_servico,
            diagnostico="",
            solucao_aplicada="",
            observacoes=f"Duplicada da {self.os_selecionada.numero_os}",
            itens=[OSItem(
                tipo=item.tipo,
                descricao=item.descricao,
                quantidade=item.quantidade,
                valor_unitario=item.valor_unitario
            ) for item in self.os_selecionada.itens]
        )

        try:
            self.os_repo.criar(nova_os)
            self._carregar_os()
            self.statusBar.showMessage(f"OS duplicada como {nova_os.numero_os}!", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao duplicar: {str(e)}")

    def _excluir_os(self):
        """Exclui OS selecionada"""
        if not self.os_selecionada:
            return

        resp = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Excluir OS {self.os_selecionada.numero_os}?\nEsta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if resp == QMessageBox.StandardButton.Yes:
            try:
                self.os_repo.excluir(self.os_selecionada.id)
                self._carregar_os()
                self.statusBar.showMessage("OS excluída!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir: {str(e)}")

    def _alterar_status_rapido(self, novo_status: str):
        """Altera status rapidamente"""
        if not self.os_selecionada:
            return

        try:
            self.os_repo.alterar_status(self.os_selecionada.id, novo_status)
            self._carregar_os()
            self.statusBar.showMessage(f"Status alterado para {novo_status}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao alterar status: {str(e)}")

    def _imprimir_os(self):
        """Imprime OS selecionada"""
        if not self.os_selecionada:
            QMessageBox.warning(self, "Aviso", "Selecione uma OS para imprimir")
            return

        dialog = OSDetalhesDialog(self, self.os_selecionada)
        dialog.exec()

    def _exportar_dados(self):
        """Exporta dados para CSV/Excel"""
        QMessageBox.information(self, "Exportar", "Funcionalidade de exportação em desenvolvimento")

    def _abrir_relatorios(self):
        """Abre dialog de relatórios"""
        dialog = RelatorioDialog(self)
        dialog.exec()

    def _abrir_configuracoes(self):
        """Abre configurações"""
        dialog = ConfiguracoesDialog(self)
        dialog.exec()

    def _adicionar_item(self):
        """Adiciona item à OS (apenas se estiver editando)"""
        QMessageBox.information(self, "Info", "Edite a OS para adicionar itens")

    def _editar_item(self):
        """Edita item selecionado"""
        QMessageBox.information(self, "Info", "Edite a OS para modificar itens")

    def _excluir_item(self):
        """Exclui item selecionado"""
        QMessageBox.information(self, "Info", "Edite a OS para remover itens")

    def _limpar_selecao(self):
        """Limpa seleção atual"""
        self.tabela_os.clearSelection()


# Import necessário para QStyle

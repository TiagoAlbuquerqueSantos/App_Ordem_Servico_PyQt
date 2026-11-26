#!/usr/bin/env python3
"""
Dialogs da aplicação
"""

from typing import List

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QWidget, QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QSpinBox, QDoubleSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialogButtonBox, QGroupBox, QCheckBox,
    QScrollArea, QFrame, QAbstractItemView, QCompleter
)

from models import (
    Cliente, Equipamento, OrdemServico, OSItem, STATUS_OS,
    PRIORIDADES, TIPOS_ITEM, TIPOS_EQUIPAMENTO
)
from repositories import ClienteRepository, EquipamentoRepository


class BaseDialog(QDialog):
    """Dialog base com funcionalidades comuns"""
    
    def __init__(self, parent=None, titulo: str = ""):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.resize(600, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Área de conteúdo (scroll)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.Shape.NoFrame)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(10)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        # Botões padrão
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        self.btn_ok = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.btn_ok.setText("Salvar")
        self.btn_cancel = self.button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.btn_cancel.setText("Cancelar")
    
    def _on_accept(self):
        """Valida antes de aceitar"""
        if self.validar():
            self.accept()
    
    def validar(self) -> bool:
        """Validação customizada - sobrescrever nas subclasses"""
        return True


class ClienteDialog(BaseDialog):
    """Dialog para cadastro/edição de cliente"""
    
    def __init__(self, parent=None, cliente: Cliente = None):
        self.cliente = cliente or Cliente()
        self.editando = cliente is not None
        titulo = "Editar Cliente" if self.editando else "Novo Cliente"
        super().__init__(parent, titulo)
        self.resize(550, 500)
        
        if self.editando:
            self._carregar_dados()
    
    def _setup_ui(self):
        super()._setup_ui()
        
        # Dados Pessoais
        group_dados = QGroupBox("Dados do Cliente")
        form = QFormLayout(group_dados)
        
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome completo ou Razão Social")
        form.addRow("Nome *:", self.input_nome)
        
        self.input_cpf_cnpj = QLineEdit()
        self.input_cpf_cnpj.setPlaceholderText("CPF ou CNPJ (apenas números)")
        form.addRow("CPF/CNPJ:", self.input_cpf_cnpj)
        
        self.input_telefone = QLineEdit()
        self.input_telefone.setPlaceholderText("(XX) XXXXX-XXXX")
        form.addRow("Telefone:", self.input_telefone)
        
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("email@exemplo.com")
        form.addRow("E-mail:", self.input_email)
        
        self.content_layout.addWidget(group_dados)
        
        # Endereço
        group_end = QGroupBox("Endereço")
        form_end = QFormLayout(group_end)
        
        self.input_endereco = QLineEdit()
        form_end.addRow("Endereço:", self.input_endereco)
        
        self.input_cidade = QLineEdit()
        form_end.addRow("Cidade:", self.input_cidade)
        
        self.input_estado = QComboBox()
        self.input_estado.setEditable(True)
        estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
                   "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
                   "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
        self.input_estado.addItems(estados)
        form_end.addRow("Estado:", self.input_estado)
        
        self.input_cep = QLineEdit()
        self.input_cep.setPlaceholderText("00000-000")
        form_end.addRow("CEP:", self.input_cep)
        
        self.content_layout.addWidget(group_end)
        
        # Observações
        group_obs = QGroupBox("Observações")
        layout_obs = QVBoxLayout(group_obs)
        self.input_obs = QTextEdit()
        self.input_obs.setMaximumHeight(80)
        self.input_obs.setPlaceholderText("Observações gerais sobre o cliente...")
        layout_obs.addWidget(self.input_obs)
        self.content_layout.addWidget(group_obs)
        
        # Status
        self.check_ativo = QCheckBox("Cliente Ativo")
        self.check_ativo.setChecked(True)
        self.content_layout.addWidget(self.check_ativo)
    
    def _carregar_dados(self):
        """Carrega dados do cliente para edição"""
        self.input_nome.setText(self.cliente.nome)
        self.input_cpf_cnpj.setText(self.cliente.cpf_cnpj)
        self.input_telefone.setText(self.cliente.telefone)
        self.input_email.setText(self.cliente.email)
        self.input_endereco.setText(self.cliente.endereco)
        self.input_cidade.setText(self.cliente.cidade)
        idx = self.input_estado.findText(self.cliente.estado)
        if idx >= 0:
            self.input_estado.setCurrentIndex(idx)
        else:
            self.input_estado.setCurrentText(self.cliente.estado)
        self.input_cep.setText(self.cliente.cep)
        self.input_obs.setPlainText(self.cliente.observacoes)
        self.check_ativo.setChecked(self.cliente.ativo)
    
    def validar(self) -> bool:
        if not self.input_nome.text().strip():
            QMessageBox.warning(self, "Validação", "Nome é obrigatório!")
            self.input_nome.setFocus()
            return False
        return True
    
    def get_cliente(self) -> Cliente:
        self.cliente.nome = self.input_nome.text().strip()
        self.cliente.cpf_cnpj = self.input_cpf_cnpj.text().strip()
        self.cliente.telefone = self.input_telefone.text().strip()
        self.cliente.email = self.input_email.text().strip()
        self.cliente.endereco = self.input_endereco.text().strip()
        self.cliente.cidade = self.input_cidade.text().strip()
        self.cliente.estado = self.input_estado.currentText().strip()
        self.cliente.cep = self.input_cep.text().strip()
        self.cliente.observacoes = self.input_obs.toPlainText().strip()
        self.cliente.ativo = self.check_ativo.isChecked()
        return self.cliente


class EquipamentoDialog(BaseDialog):
    """Dialog para cadastro/edição de equipamento"""
    
    def __init__(self, parent=None, equipamento: Equipamento = None, clientes: List[Cliente] = None):
        self.equipamento = equipamento or Equipamento()
        self.clientes = clientes or []
        self.editando = equipamento is not None
        titulo = "Editar Equipamento" if self.editando else "Novo Equipamento"
        super().__init__(parent, titulo)
        self.resize(550, 450)
        
        if self.editando:
            self._carregar_dados()
    
    def _setup_ui(self):
        super()._setup_ui()
        
        # Cliente
        group_cliente = QGroupBox("Cliente")
        form = QFormLayout(group_cliente)
        
        self.combo_cliente = QComboBox()
        for c in self.clientes:
            self.combo_cliente.addItem(f"{c.nome} ({c.cpf_cnpj})" if c.cpf_cnpj else c.nome, c.id)
        form.addRow("Cliente *:", self.combo_cliente)
        
        self.content_layout.addWidget(group_cliente)
        
        # Dados do Equipamento
        group_eq = QGroupBox("Dados do Equipamento")
        form_eq = QFormLayout(group_eq)
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.setEditable(True)
        self.combo_tipo.addItems(TIPOS_EQUIPAMENTO)
        form_eq.addRow("Tipo *:", self.combo_tipo)
        
        self.input_marca = QLineEdit()
        form_eq.addRow("Marca:", self.input_marca)
        
        self.input_modelo = QLineEdit()
        form_eq.addRow("Modelo:", self.input_modelo)
        
        self.input_serie = QLineEdit()
        self.input_serie.setPlaceholderText("Número de série / IMEI")
        form_eq.addRow("Nº Série:", self.input_serie)
        
        self.content_layout.addWidget(group_eq)
        
        # Defeito e Acessórios
        group_def = QGroupBox("Defeito e Acessórios")
        layout_def = QVBoxLayout(group_def)
        
        layout_def.addWidget(QLabel("Defeito Relatado:"))
        self.input_defeito = QTextEdit()
        self.input_defeito.setMaximumHeight(80)
        self.input_defeito.setPlaceholderText("Descreva o defeito relatado pelo cliente...")
        layout_def.addWidget(self.input_defeito)
        
        layout_def.addWidget(QLabel("Acessórios Acompanhados:"))
        self.input_acessorios = QTextEdit()
        self.input_acessorios.setMaximumHeight(60)
        self.input_acessorios.setPlaceholderText("Ex: Carregador, mouse, capa, fonte...")
        layout_def.addWidget(self.input_acessorios)
        
        self.content_layout.addWidget(group_def)
    
    def _carregar_dados(self):
        idx = self.combo_cliente.findData(self.equipamento.cliente_id)
        if idx >= 0:
            self.combo_cliente.setCurrentIndex(idx)
        
        self.combo_tipo.setCurrentText(self.equipamento.tipo)
        self.input_marca.setText(self.equipamento.marca)
        self.input_modelo.setText(self.equipamento.modelo)
        self.input_serie.setText(self.equipamento.numero_serie)
        self.input_defeito.setPlainText(self.equipamento.defeito_relatado)
        self.input_acessorios.setPlainText(self.equipamento.acessorios)
    
    def validar(self) -> bool:
        if self.combo_cliente.currentData() is None:
            QMessageBox.warning(self, "Validação", "Selecione um cliente!")
            return False
        if not self.combo_tipo.currentText().strip():
            QMessageBox.warning(self, "Validação", "Tipo do equipamento é obrigatório!")
            self.combo_tipo.setFocus()
            return False
        return True
    
    def get_equipamento(self) -> Equipamento:
        self.equipamento.cliente_id = self.combo_cliente.currentData()
        self.equipamento.tipo = self.combo_tipo.currentText().strip()
        self.equipamento.marca = self.input_marca.text().strip()
        self.equipamento.modelo = self.input_modelo.text().strip()
        self.equipamento.numero_serie = self.input_serie.text().strip()
        self.equipamento.defeito_relatado = self.input_defeito.toPlainText().strip()
        self.equipamento.acessorios = self.input_acessorios.toPlainText().strip()
        return self.equipamento


class ItemDialog(BaseDialog):
    """Dialog para adicionar/editar item (peça/serviço)"""
    
    def __init__(self, parent=None, item: OSItem = None):
        self.item = item or OSItem()
        self.editando = item is not None
        titulo = "Editar Item" if self.editando else "Novo Item"
        super().__init__(parent, titulo)
        self.resize(500, 300)
        
        if self.editando:
            self._carregar_dados()
    
    def _setup_ui(self):
        super()._setup_ui()
        
        form = QFormLayout()
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(TIPOS_ITEM)
        form.addRow("Tipo *:", self.combo_tipo)
        
        self.input_descricao = QLineEdit()
        self.input_descricao.setPlaceholderText("Descrição da peça ou serviço")
        form.addRow("Descrição *:", self.input_descricao)
        
        self.spin_qtd = QSpinBox()
        self.spin_qtd.setMinimum(1)
        self.spin_qtd.setMaximum(999)
        self.spin_qtd.setValue(1)
        form.addRow("Quantidade *:", self.spin_qtd)
        
        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setDecimals(2)
        self.spin_valor.setMaximum(999999.99)
        self.spin_valor.setPrefix("R$ ")
        form.addRow("Valor Unit. *:", self.spin_valor)
        
        # Total (read-only)
        self.lbl_total = QLabel("R$ 0,00")
        self.lbl_total.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.lbl_total.setStyleSheet("color: #27ae60;")
        form.addRow("Total:", self.lbl_total)
        
        # Conecta sinais para atualizar total
        self.spin_qtd.valueChanged.connect(self._atualizar_total)
        self.spin_valor.valueChanged.connect(self._atualizar_total)
        
        self.content_layout.addLayout(form)
        self._atualizar_total()
    
    def _carregar_dados(self):
        self.combo_tipo.setCurrentText(self.item.tipo)
        self.input_descricao.setText(self.item.descricao)
        self.spin_qtd.setValue(self.item.quantidade)
        self.spin_valor.setValue(self.item.valor_unitario)
    
    def _atualizar_total(self):
        total = self.spin_qtd.value() * self.spin_valor.value()
        self.lbl_total.setText(f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    def validar(self) -> bool:
        if not self.input_descricao.text().strip():
            QMessageBox.warning(self, "Validação", "Descrição é obrigatória!")
            self.input_descricao.setFocus()
            return False
        if self.spin_valor.value() < 0:
            QMessageBox.warning(self, "Validação", "Valor não pode ser negativo!")
            return False
        return True
    
    def get_item(self) -> OSItem:
        self.item.tipo = self.combo_tipo.currentText()
        self.item.descricao = self.input_descricao.text().strip()
        self.item.quantidade = self.spin_qtd.value()
        self.item.valor_unitario = self.spin_valor.value()
        self.item.valor_total = self.item.quantidade * self.item.valor_unitario
        return self.item


class OrdemServicoDialog(BaseDialog):
    """Dialog principal para criar/editar Ordem de Serviço"""
    
    def __init__(self, parent=None, os: OrdemServico = None, 
                 cliente_repo: ClienteRepository = None,
                 equipamento_repo: EquipamentoRepository = None):
        self.os = os or OrdemServico()
        self.cliente_repo = cliente_repo
        self.equipamento_repo = equipamento_repo
        self.editando = os is not None
        titulo = "Editar Ordem de Serviço" if self.editando else "Nova Ordem de Serviço"
        super().__init__(parent, titulo)
        self.resize(800, 700)
        
        self.itens_originais = []  # Para detectar mudanças
        
        if self.editando:
            self._carregar_dados()
    
    def _setup_ui(self):
        super()._setup_ui()
        
        # Abas
        tabs = QTabWidget()
        self.content_layout.addWidget(tabs)
        
        # Aba 1: Dados Principais
        self._criar_aba_dados(tabs)
        
        # Aba 2: Itens (Peças/Serviços)
        self._criar_aba_itens(tabs)
        
        # Aba 3: Observações
        self._criar_aba_obs(tabs)
    
    def _criar_aba_dados(self, tabs):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Cliente e Equipamento
        group_ce = QGroupBox("Cliente e Equipamento")
        form = QFormLayout(group_ce)
        
        self.combo_cliente = QComboBox()
        self.combo_cliente.setEditable(True)
        self.combo_cliente.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._carregar_clientes()
        form.addRow("Cliente *:", self.combo_cliente)
        
        self.combo_equipamento = QComboBox()
        self.combo_equipamento.setEditable(True)
        form.addRow("Equipamento *:", self.combo_equipamento)
        
        # Conecta mudança de cliente para filtrar equipamentos
        self.combo_cliente.currentIndexChanged.connect(self._filtrar_equipamentos)
        
        layout.addWidget(group_ce)
        
        # Dados da OS
        group_os = QGroupBox("Dados da Ordem de Serviço")
        form_os = QFormLayout(group_os)
        
        self.input_numero = QLineEdit()
        self.input_numero.setReadOnly(True)
        self.input_numero.setStyleSheet("background-color: #f0f0f0;")
        form_os.addRow("Nº OS:", self.input_numero)
        
        self.combo_status = QComboBox()
        self.combo_status.addItems(STATUS_OS)
        form_os.addRow("Status:", self.combo_status)
        
        self.combo_prioridade = QComboBox()
        self.combo_prioridade.addItems(PRIORIDADES)
        self.combo_prioridade.setCurrentText("NORMAL")
        form_os.addRow("Prioridade:", self.combo_prioridade)
        
        self.input_tecnico = QLineEdit()
        self.input_tecnico.setPlaceholderText("Nome do técnico responsável")
        form_os.addRow("Técnico:", self.input_tecnico)
        
        self.date_previsao = QDateEdit()
        self.date_previsao.setCalendarPopup(True)
        self.date_previsao.setDate(QDate.currentDate().addDays(7))
        self.date_previsao.setSpecialValueText("Não definida")
        form_os.addRow("Previsão Entrega:", self.date_previsao)
        
        layout.addWidget(group_os)
        
        # Descrição do Serviço
        group_desc = QGroupBox("Descrição do Serviço")
        layout_desc = QVBoxLayout(group_desc)
        self.txt_descricao = QTextEdit()
        self.txt_descricao.setPlaceholderText("Descreva o serviço a ser realizado...")
        self.txt_descricao.setMaximumHeight(100)
        layout_desc.addWidget(self.txt_descricao)
        layout.addWidget(group_desc)
        
        # Diagnóstico e Solução
        group_diag = QGroupBox("Diagnóstico e Solução")
        layout_diag = QVBoxLayout(group_diag)
        
        layout_diag.addWidget(QLabel("Diagnóstico:"))
        self.txt_diagnostico = QTextEdit()
        self.txt_diagnostico.setPlaceholderText("Diagnóstico técnico do problema...")
        self.txt_diagnostico.setMaximumHeight(80)
        layout_diag.addWidget(self.txt_diagnostico)
        
        layout_diag.addWidget(QLabel("Solução Aplicada:"))
        self.txt_solucao = QTextEdit()
        self.txt_solucao.setPlaceholderText("Descreva a solução realizada...")
        self.txt_solucao.setMaximumHeight(80)
        layout_diag.addWidget(self.txt_solucao)
        
        layout.addWidget(group_diag)
        
        tabs.addTab(widget, "📋 Dados Principais")
    
    def _criar_aba_itens(self, tabs):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.btn_add_item = QPushButton("➕ Adicionar Peça")
        self.btn_add_item.clicked.connect(lambda: self._abrir_item_dialog('PECA'))
        toolbar.addWidget(self.btn_add_item)
        
        self.btn_add_servico = QPushButton("⚙️ Adicionar Serviço")
        self.btn_add_servico.clicked.connect(lambda: self._abrir_item_dialog('SERVICO'))
        toolbar.addWidget(self.btn_add_servico)
        
        self.btn_edit_item = QPushButton("✏️ Editar")
        self.btn_edit_item.clicked.connect(self._editar_item_selecionado)
        self.btn_edit_item.setEnabled(False)
        toolbar.addWidget(self.btn_edit_item)
        
        self.btn_del_item = QPushButton("🗑️ Excluir")
        self.btn_del_item.clicked.connect(self._excluir_item_selecionado)
        self.btn_del_item.setEnabled(False)
        toolbar.addWidget(self.btn_del_item)
        
        toolbar.addStretch()
        
        # Totais
        self.lbl_total_pecas = QLabel("Peças: R$ 0,00")
        self.lbl_total_servicos = QLabel("Serviços: R$ 0,00")
        self.lbl_total_geral = QLabel("Total: R$ 0,00")
        self.lbl_total_geral.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.lbl_total_geral.setStyleSheet("color: #27ae60;")
        
        toolbar.addWidget(self.lbl_total_pecas)
        toolbar.addWidget(self.lbl_total_servicos)
        toolbar.addWidget(self.lbl_total_geral)
        
        layout.addLayout(toolbar)
        
        # Tabela de itens
        self.tabela_itens = QTableWidget()
        self.tabela_itens.setColumnCount(6)
        self.tabela_itens.setHorizontalHeaderLabels([
            "Tipo", "Descrição", "Qtd", "Vl. Unit.", "Vl. Total", "ID"
        ])
        self.tabela_itens.setColumnHidden(5, True)
        self.tabela_itens.horizontalHeader().setStretchLastSection(True)
        self.tabela_itens.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_itens.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_itens.itemSelectionChanged.connect(self._on_selecao_item)
        self.tabela_itens.doubleClicked.connect(self._editar_item_selecionado)
        
        layout.addWidget(self.tabela_itens)
        
        tabs.addTab(widget, "📦 Itens (Peças/Serviços)")
    
    def _criar_aba_obs(self, tabs):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("Observações Gerais")
        layout_obs = QVBoxLayout(group)
        self.txt_obs = QTextEdit()
        self.txt_obs.setPlaceholderText("Observações adicionais sobre a OS...")
        layout_obs.addWidget(self.txt_obs)
        layout.addWidget(group)
        
        tabs.addTab(widget, "📝 Observações")
    
    def _carregar_clientes(self):
        """Carrega lista de clientes no combo"""
        self.combo_cliente.clear()
        self.combo_cliente.addItem("Selecione...", None)
        
        if self.cliente_repo:
            clientes = self.cliente_repo.buscar_todos(apenas_ativos=True)
            for c in clientes:
                texto = f"{c.nome} ({c.cpf_cnpj})" if c.cpf_cnpj else c.nome
                self.combo_cliente.addItem(texto, c.id)
        
        # Configura completer para busca
        from PyQt6.QtCore import QStringListModel
        nomes = [self.combo_cliente.itemText(i) for i in range(1, self.combo_cliente.count())]
        completer = QCompleter(QStringListModel(nomes), self.combo_cliente)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.combo_cliente.setCompleter(completer)
    
    def _filtrar_equipamentos(self):
        """Filtra equipamentos do cliente selecionado"""
        self.combo_equipamento.clear()
        self.combo_equipamento.addItem("Selecione...", None)
        
        cliente_id = self.combo_cliente.currentData()
        if cliente_id and self.equipamento_repo:
            equipamentos = self.equipamento_repo.buscar_por_cliente(cliente_id)
            for e in equipamentos:
                self.combo_equipamento.addItem(e.descricao_completa, e.id)
    
    def _carregar_dados(self):
        """Carrega dados da OS para edição"""
        self.input_numero.setText(self.os.numero_os)
        
        # Cliente
        idx = self.combo_cliente.findData(self.os.cliente_id)
        if idx >= 0:
            self.combo_cliente.setCurrentIndex(idx)
        
        # Equipamento (após carregar cliente)
        self._filtrar_equipamentos()
        idx = self.combo_equipamento.findData(self.os.equipamento_id)
        if idx >= 0:
            self.combo_equipamento.setCurrentIndex(idx)
        
        self.combo_status.setCurrentText(self.os.status)
        self.combo_prioridade.setCurrentText(self.os.prioridade)
        self.input_tecnico.setText(self.os.tecnico_responsavel or "")
        
        if self.os.data_previsao_entrega:
            self.date_previsao.setDate(QDate.fromString(
                self.os.data_previsao_entrega.isoformat(), "yyyy-MM-dd"
            ))
        
        self.txt_descricao.setPlainText(self.os.descricao_servico or "")
        self.txt_diagnostico.setPlainText(self.os.diagnostico or "")
        self.txt_solucao.setPlainText(self.os.solucao_aplicada or "")
        self.txt_obs.setPlainText(self.os.observacoes or "")
        
        # Carrega itens
        self._popular_tabela_itens(self.os.itens)
        self.itens_originais = [item.to_dict() for item in self.os.itens]
    
    def _popular_tabela_itens(self, itens: List[OSItem]):
        """Preenche tabela de itens"""
        self.tabela_itens.setRowCount(len(itens))
        
        total_pecas = 0.0
        total_servicos = 0.0
        
        for row, item in enumerate(itens):
            self.tabela_itens.setItem(row, 0, QTableWidgetItem(item.tipo))
            self.tabela_itens.setItem(row, 1, QTableWidgetItem(item.descricao))
            
            qtd_item = QTableWidgetItem(str(item.quantidade))
            qtd_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabela_itens.setItem(row, 2, qtd_item)
            
            vl_unit = QTableWidgetItem(f"R$ {item.valor_unitario:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            vl_unit.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabela_itens.setItem(row, 3, vl_unit)
            
            vl_total = QTableWidgetItem(f"R$ {item.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            vl_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            vl_total.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            self.tabela_itens.setItem(row, 4, vl_total)
            
            id_item = QTableWidgetItem(str(item.id or 0))
            self.tabela_itens.setItem(row, 5, id_item)
            
            if item.tipo == 'PECA':
                total_pecas += item.valor_total
            else:
                total_servicos += item.valor_total
        
        self.lbl_total_pecas.setText(f"Peças: R$ {total_pecas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_total_servicos.setText(f"Serviços: R$ {total_servicos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_total_geral.setText(f"Total: R$ {total_pecas + total_servicos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    def _on_selecao_item(self):
        has_sel = len(self.tabela_itens.selectedItems()) > 0
        self.btn_edit_item.setEnabled(has_sel)
        self.btn_del_item.setEnabled(has_sel)
    
    def _abrir_item_dialog(self, tipo_padrao: str):
        """Abre dialog para novo item"""
        item = OSItem(tipo=tipo_padrao)
        dialog = ItemDialog(self, item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            novo_item = dialog.get_item()
            self.os.itens.append(novo_item)
            self._popular_tabela_itens(self.os.itens)
    
    def _editar_item_selecionado(self):
        """Edita item selecionado"""
        selected = self.tabela_itens.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        item_id = int(self.tabela_itens.item(row, 5).text())
        
        # Encontra item na lista
        item = next((i for i in self.os.itens if i.id == item_id), None)
        if not item and row < len(self.os.itens):
            item = self.os.itens[row]
        
        if item:
            dialog = ItemDialog(self, item)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                item_atualizado = dialog.get_item()
                # Atualiza na lista
                for i, it in enumerate(self.os.itens):
                    if it.id == item_id or (item_id == 0 and i == row):
                        self.os.itens[i] = item_atualizado
                        break
                self._popular_tabela_itens(self.os.itens)
    
    def _excluir_item_selecionado(self):
        """Exclui item selecionado"""
        selected = self.tabela_itens.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        if row < len(self.os.itens):
            resp = QMessageBox.question(
                self, "Confirmar", "Excluir este item?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if resp == QMessageBox.StandardButton.Yes:
                self.os.itens.pop(row)
                self._popular_tabela_itens(self.os.itens)
    
    def validar(self) -> bool:
        if self.combo_cliente.currentData() is None:
            QMessageBox.warning(self, "Validação", "Selecione um cliente!")
            return False
        
        if self.combo_equipamento.currentData() is None:
            QMessageBox.warning(self, "Validação", "Selecione um equipamento!")
            return False
        
        return True
    
    def get_ordem_servico(self) -> OrdemServico:
        self.os.cliente_id = self.combo_cliente.currentData()
        self.os.equipamento_id = self.combo_equipamento.currentData()
        self.os.status = self.combo_status.currentText()
        self.os.prioridade = self.combo_prioridade.currentText()
        self.os.tecnico_responsavel = self.input_tecnico.text().strip()
        self.os.descricao_servico = self.txt_descricao.toPlainText().strip()
        self.os.diagnostico = self.txt_diagnostico.toPlainText().strip()
        self.os.solucao_aplicada = self.txt_solucao.toPlainText().strip()
        self.os.observacoes = self.txt_obs.toPlainText().strip()
        
        # Data previsão
        if self.date_previsao.date().isValid():
            self.os.data_previsao_entrega = self.date_previsao.date().toPyDate()
        else:
            self.os.data_previsao_entrega = None
        
        # Recalcula totais dos itens
        self.os.valor_pecas = sum(i.valor_total for i in self.os.itens if i.tipo == 'PECA')
        self.os.valor_mao_obra = sum(i.valor_total for i in self.os.itens if i.tipo == 'SERVICO')
        self.os.valor_total = self.os.valor_pecas + self.os.valor_mao_obra
        
        return self.os


class OSDetalhesDialog(QDialog):
    """Dialog para visualização/impressão detalhada da OS"""
    
    def __init__(self, parent=None, os: OrdemServico = None):
        super().__init__(parent)
        self.os = os
        self.setWindowTitle(f"OS {os.numero_os} - Detalhes")
        self.resize(700, 900)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        
        # Cabeçalho
        self._criar_cabecalho(content_layout)
        
        # Dados do Cliente/Equipamento
        self._criar_dados_cliente_equip(content_layout)
        
        # Descrição, Diagnóstico, Solução
        self._criar_textos(content_layout)
        
        # Itens
        self._criar_tabela_itens(content_layout)
        
        # Totais
        self._criar_totais(content_layout)
        
        # Observações
        if self.os.observacoes:
            group = QGroupBox("Observações")
            group_layout = QVBoxLayout(group)
            lbl = QLabel(self.os.observacoes)
            lbl.setWordWrap(True)
            group_layout.addWidget(lbl)
            content_layout.addWidget(group)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_imprimir = QPushButton("🖨️ Imprimir")
        btn_imprimir.clicked.connect(self._imprimir)
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_imprimir)
        btn_layout.addWidget(btn_fechar)
        layout.addLayout(btn_layout)
    
    def _criar_cabecalho(self, layout):
        group = QGroupBox()
        group.setStyleSheet("QGroupBox { border: none; font-size: 14px; }")
        glayout = QVBoxLayout(group)
        
        lbl_titulo = QLabel("ORDEM DE SERVIÇO")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        glayout.addWidget(lbl_titulo)
        
        lbl_numero = QLabel(self.os.numero_os)
        lbl_numero.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_numero.setFont(QFont("Monospace", 14, QFont.Weight.Bold))
        lbl_numero.setStyleSheet("color: #2c3e50;")
        glayout.addWidget(lbl_numero)
        
        # Status
        from ui.widgets import StatusBadge, PrioridadeBadge
        hlayout = QHBoxLayout()
        hlayout.addStretch()
        badge_status = StatusBadge()
        badge_status.set_status(self.os.status)
        hlayout.addWidget(badge_status)
        
        badge_prio = PrioridadeBadge()
        badge_prio.set_prioridade(self.os.prioridade)
        hlayout.addWidget(badge_prio)
        hlayout.addStretch()
        glayout.addLayout(hlayout)
        
        layout.addWidget(group)
    
    def _criar_dados_cliente_equip(self, layout):
        group = QGroupBox("Dados do Cliente e Equipamento")
        form = QFormLayout(group)
        
        form.addRow("Cliente:", QLabel(self.os.cliente_nome))
        form.addRow("Equipamento:", QLabel(self.os.equipamento_descricao))
        
        if self.os.tecnico_responsavel:
            form.addRow("Técnico:", QLabel(self.os.tecnico_responsavel))
        
        data_ab = self.os.data_abertura.strftime("%d/%m/%Y %H:%M") if self.os.data_abertura else "-"
        form.addRow("Abertura:", QLabel(data_ab))
        
        if self.os.data_previsao_entrega:
            form.addRow("Previsão:", QLabel(self.os.data_previsao_entrega.strftime("%d/%m/%Y")))
        
        if self.os.data_conclusao:
            form.addRow("Conclusão:", QLabel(self.os.data_conclusao.strftime("%d/%m/%Y %H:%M")))
        
        if self.os.data_entrega:
            form.addRow("Entrega:", QLabel(self.os.data_entrega.strftime("%d/%m/%Y %H:%M")))
        
        layout.addWidget(group)
    
    def _criar_textos(self, layout):
        textos = [
            ("Descrição do Serviço", self.os.descricao_servico),
            ("Diagnóstico", self.os.diagnostico),
            ("Solução Aplicada", self.os.solucao_aplicada)
        ]
        
        for titulo, texto in textos:
            if texto:
                group = QGroupBox(titulo)
                glayout = QVBoxLayout(group)
                lbl = QLabel(texto)
                lbl.setWordWrap(True)
                lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                glayout.addWidget(lbl)
                layout.addWidget(group)
    
    def _criar_tabela_itens(self, layout):
        group = QGroupBox("Itens (Peças e Serviços)")
        glayout = QVBoxLayout(group)
        
        tabela = QTableWidget()
        tabela.setColumnCount(5)
        tabela.setHorizontalHeaderLabels(["Tipo", "Descrição", "Qtd", "Vl. Unit.", "Vl. Total"])
        tabela.horizontalHeader().setStretchLastSection(True)
        tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabela.setRowCount(len(self.os.itens))
        
        for row, item in enumerate(self.os.itens):
            tabela.setItem(row, 0, QTableWidgetItem(item.tipo))
            tabela.setItem(row, 1, QTableWidgetItem(item.descricao))
            
            qtd = QTableWidgetItem(str(item.quantidade))
            qtd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tabela.setItem(row, 2, qtd)
            
            vu = QTableWidgetItem(f"R$ {item.valor_unitario:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            vu.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabela.setItem(row, 3, vu)
            
            vt = QTableWidgetItem(f"R$ {item.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            vt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            vt.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            tabela.setItem(row, 4, vt)
        
        glayout.addWidget(tabela)
        layout.addWidget(group)
    
    def _criar_totais(self, layout):
        group = QGroupBox("Valores")
        form = QFormLayout(group)
        
        form.addRow("Total Peças:", QLabel(f"R$ {self.os.valor_pecas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
        form.addRow("Total Mão de Obra:", QLabel(f"R$ {self.os.valor_mao_obra:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
        
        lbl_total = QLabel(f"R$ {self.os.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        lbl_total.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_total.setStyleSheet("color: #27ae60;")
        form.addRow("TOTAL:", lbl_total)
        
        layout.addWidget(group)
    
    def _imprimir(self):
        """Imprime a OS"""
        from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
        from PyQt6.QtGui import QTextDocument
        
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Gera HTML para impressão
            html = self._gerar_html_impressao()
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print(printer)
    
    def _gerar_html_impressao(self) -> str:
        """Gera HTML para impressão"""
        itens_html = ""
        for item in self.os.itens:
            itens_html += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">{item.tipo}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{item.descricao}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{item.quantidade}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">R$ {item.valor_unitario:,.2f}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;"><b>R$ {item.valor_total:,.2f}</b></td>
            </tr>
            """
        
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h1 {{ margin: 0; color: #2c3e50; }}
                .header .numero {{ font-family: monospace; font-size: 1.5em; color: #34495e; }}
                .section {{ margin-bottom: 20px; }}
                .section h2 {{ border-bottom: 2px solid #3498db; padding-bottom: 5px; color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th {{ background: #34495e; color: white; padding: 10px; text-align: left; }}
                .totais {{ text-align: right; margin-top: 20px; }}
                .total-final {{ font-size: 1.3em; font-weight: bold; color: #27ae60; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>ORDEM DE SERVIÇO</h1>
                <div class="numero">{self.os.numero_os}</div>
                <div>Status: {self.os.status} | Prioridade: {self.os.prioridade}</div>
            </div>
            
            <div class="section">
                <h2>Cliente e Equipamento</h2>
                <p><b>Cliente:</b> {self.os.cliente_nome}</p>
                <p><b>Equipamento:</b> {self.os.equipamento_descricao}</p>
                <p><b>Técnico:</b> {self.os.tecnico_responsavel or '-'}</p>
                <p><b>Abertura:</b> {self.os.data_abertura.strftime('%d/%m/%Y %H:%M') if self.os.data_abertura else '-'}</p>
                <p><b>Previsão:</b> {self.os.data_previsao_entrega.strftime('%d/%m/%Y') if self.os.data_previsao_entrega else '-'}</p>
            </div>
            
            <div class="section">
                <h2>Descrição do Serviço</h2>
                <p>{self.os.descricao_servico or '-'}</p>
            </div>
            
            <div class="section">
                <h2>Diagnóstico</h2>
                <p>{self.os.diagnostico or '-'}</p>
            </div>
            
            <div class="section">
                <h2>Solução Aplicada</h2>
                <p>{self.os.solucao_aplicada or '-'}</p>
            </div>
            
            <div class="section">
                <h2>Itens</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Tipo</th><th>Descrição</th><th>Qtd</th><th>Vl. Unit.</th><th>Vl. Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {itens_html}
                    </tbody>
                </table>
            </div>
            
            <div class="totais">
                <p>Total Peças: R$ {self.os.valor_pecas:,.2f}</p>
                <p>Total Mão de Obra: R$ {self.os.valor_mao_obra:,.2f}</p>
                <p class="total-final">TOTAL: R$ {self.os.valor_total:,.2f}</p>
            </div>
            
            {f'<div class="section"><h2>Observações</h2><p>{self.os.observacoes}</p></div>' if self.os.observacoes else ''}
        </body>
        </html>
        """


class RelatorioDialog(QDialog):
    """Dialog para relatórios"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Relatórios")
        self.resize(600, 400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Relatórios Disponíveis:"))
        
        botoes = [
            ("📊 OS por Status", self._relatorio_status),
            ("📈 Faturamento por Período", self._relatorio_faturamento),
            ("👥 OS por Cliente", self._relatorio_clientes),
            ("🔧 OS por Técnico", self._relatorio_tecnicos),
            ("📦 Peças mais Utilizadas", self._relatorio_pecas),
        ]
        
        for texto, callback in botoes:
            btn = QPushButton(texto)
            btn.setMinimumHeight(50)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.accept)
        layout.addWidget(btn_fechar)
    
    def _relatorio_status(self):
        QMessageBox.information(self, "Relatório", "Relatório de OS por Status - Em desenvolvimento")
    
    def _relatorio_faturamento(self):
        QMessageBox.information(self, "Relatório", "Relatório de Faturamento - Em desenvolvimento")
    
    def _relatorio_clientes(self):
        QMessageBox.information(self, "Relatório", "Relatório por Cliente - Em desenvolvimento")
    
    def _relatorio_tecnicos(self):
        QMessageBox.information(self, "Relatório", "Relatório por Técnico - Em desenvolvimento")
    
    def _relatorio_pecas(self):
        QMessageBox.information(self, "Relatório", "Relatório de Peças - Em desenvolvimento")


class ConfiguracoesDialog(QDialog):
    """Dialog de configurações"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.resize(500, 400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Aba Geral
        geral = QWidget()
        g_layout = QFormLayout(geral)
        
        self.input_empresa = QLineEdit()
        self.input_empresa.setPlaceholderText("Nome da empresa/assistência técnica")
        g_layout.addRow("Empresa:", self.input_empresa)
        
        self.input_cnpj = QLineEdit()
        g_layout.addRow("CNPJ:", self.input_cnpj)
        
        self.input_endereco = QLineEdit()
        g_layout.addRow("Endereço:", self.input_endereco)
        
        self.input_telefone = QLineEdit()
        g_layout.addRow("Telefone:", self.input_telefone)
        
        self.input_email = QLineEdit()
        g_layout.addRow("E-mail:", self.input_email)
        
        tabs.addTab(geral, "Geral")
        
        # Aba OS
        os_tab = QWidget()
        os_layout = QFormLayout(os_tab)
        
        self.spin_dias_garantia = QSpinBox()
        self.spin_dias_garantia.setRange(0, 365)
        self.spin_dias_garantia.setValue(90)
        os_layout.addRow("Dias de Garantia:", self.spin_dias_garantia)
        
        self.check_auto_backup = QCheckBox("Backup automático diário")
        self.check_auto_backup.setChecked(True)
        os_layout.addRow(self.check_auto_backup)
        
        tabs.addTab(os_tab, "Ordens de Serviço")
        
        # Aba Aparência
        aparencia = QWidget()
        a_layout = QFormLayout(aparencia)
        
        self.combo_tema = QComboBox()
        self.combo_tema.addItems(["Claro", "Escuro", "Sistema"])
        a_layout.addRow("Tema:", self.combo_tema)
        
        tabs.addTab(aparencia, "Aparência")
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_salvar = QPushButton("Salvar")
        btn_salvar.clicked.connect(self._salvar)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_salvar)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)
    
    def _salvar(self):
        QMessageBox.information(self, "Configurações", "Configurações salvas! (Simulação)")
        self.accept()
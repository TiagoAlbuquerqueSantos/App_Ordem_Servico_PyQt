#!/usr/bin/env python3
"""
Modelos de dados da aplicação
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List


@dataclass
class Cliente:
    """Modelo de Cliente"""
    id: Optional[int] = None
    nome: str = ""
    cpf_cnpj: str = ""
    telefone: str = ""
    email: str = ""
    endereco: str = ""
    cidade: str = ""
    estado: str = ""
    cep: str = ""
    observacoes: str = ""
    data_cadastro: Optional[datetime] = None
    ativo: bool = True
    
    def __post_init__(self):
        if self.data_cadastro is None:
            self.data_cadastro = datetime.now()
    
    @property
    def nome_formatado(self) -> str:
        return f"{self.nome} ({self.cpf_cnpj})" if self.cpf_cnpj else self.nome
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf_cnpj': self.cpf_cnpj,
            'telefone': self.telefone,
            'email': self.email,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'observacoes': self.observacoes,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ativo': self.ativo
        }
    
    @classmethod
    def from_row(cls, row) -> 'Cliente':
        """Cria instância a partir de uma row do SQLite"""
        return cls(
            id=row['id'],
            nome=row['nome'],
            cpf_cnpj=row['cpf_cnpj'] or '',
            telefone=row['telefone'] or '',
            email=row['email'] or '',
            endereco=row['endereco'] or '',
            cidade=row['cidade'] or '',
            estado=row['estado'] or '',
            cep=row['cep'] or '',
            observacoes=row['observacoes'] or '',
            data_cadastro=datetime.fromisoformat(row['data_cadastro']) if row['data_cadastro'] else None,
            ativo=bool(row['ativo'])
        )


@dataclass
class Equipamento:
    """Modelo de Equipamento"""
    id: Optional[int] = None
    cliente_id: int = 0
    tipo: str = ""
    marca: str = ""
    modelo: str = ""
    numero_serie: str = ""
    defeito_relatado: str = ""
    acessorios: str = ""
    data_cadastro: Optional[datetime] = None
    
    def __post_init__(self):
        if self.data_cadastro is None:
            self.data_cadastro = datetime.now()
    
    @property
    def descricao_completa(self) -> str:
        parts = [self.tipo]
        if self.marca:
            parts.append(self.marca)
        if self.modelo:
            parts.append(self.modelo)
        return " - ".join(parts)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'tipo': self.tipo,
            'marca': self.marca,
            'modelo': self.modelo,
            'numero_serie': self.numero_serie,
            'defeito_relatado': self.defeito_relatado,
            'acessorios': self.acessorios,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }
    
    @classmethod
    def from_row(cls, row) -> 'Equipamento':
        return cls(
            id=row['id'],
            cliente_id=row['cliente_id'],
            tipo=row['tipo'],
            marca=row['marca'] or '',
            modelo=row['modelo'] or '',
            numero_serie=row['numero_serie'] or '',
            defeito_relatado=row['defeito_relatado'] or '',
            acessorios=row['acessorios'] or '',
            data_cadastro=datetime.fromisoformat(row['data_cadastro']) if row['data_cadastro'] else None
        )


@dataclass
class OSItem:
    """Item da Ordem de Serviço (Peça ou Serviço)"""
    id: Optional[int] = None
    os_id: int = 0
    tipo: str = "SERVICO"  # PECA ou SERVICO
    descricao: str = ""
    quantidade: int = 1
    valor_unitario: float = 0.0
    valor_total: float = 0.0
    
    def __post_init__(self):
        self.valor_total = self.quantidade * self.valor_unitario
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'os_id': self.os_id,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'quantidade': self.quantidade,
            'valor_unitario': self.valor_unitario,
            'valor_total': self.valor_total
        }
    
    @classmethod
    def from_row(cls, row) -> 'OSItem':
        return cls(
            id=row['id'],
            os_id=row['os_id'],
            tipo=row['tipo'],
            descricao=row['descricao'],
            quantidade=row['quantidade'],
            valor_unitario=row['valor_unitario'],
            valor_total=row['valor_total']
        )


@dataclass
class OrdemServico:
    """Modelo de Ordem de Serviço"""
    id: Optional[int] = None
    numero_os: str = ""
    cliente_id: int = 0
    equipamento_id: int = 0
    status: str = "ABERTA"
    prioridade: str = "NORMAL"
    tecnico_responsavel: str = ""
    descricao_servico: str = ""
    diagnostico: str = ""
    solucao_aplicada: str = ""
    valor_pecas: float = 0.0
    valor_mao_obra: float = 0.0
    valor_total: float = 0.0
    data_abertura: Optional[datetime] = None
    data_previsao_entrega: Optional[date] = None
    data_conclusao: Optional[datetime] = None
    data_entrega: Optional[datetime] = None
    observacoes: str = ""
    itens: List[OSItem] = field(default_factory=list)
    
    # Campos relacionados (preenchidos via join)
    cliente_nome: str = ""
    equipamento_descricao: str = ""
    
    def __post_init__(self):
        if self.data_abertura is None:
            self.data_abertura = datetime.now()
        if not self.numero_os:
            self.numero_os = self._gerar_numero_os()
    
    def _gerar_numero_os(self) -> str:
        """Gera número da OS baseado na data atual"""
        now = datetime.now()
        return f"OS{now.strftime('%Y%m%d%H%M%S')}"
    
    @property
    def status_cor(self) -> str:
        """Retorna cor para o status"""
        cores = {
            'ABERTA': '#3498db',
            'EM_ANDAMENTO': '#f39c12',
            'AGUARDANDO_PECAS': '#e74c3c',
            'AGUARDANDO_APROVACAO': '#9b59b6',
            'CONCLUIDA': '#27ae60',
            'ENTREGUE': '#2c3e50',
            'CANCELADA': '#95a5a6'
        }
        return cores.get(self.status, '#34495e')
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'numero_os': self.numero_os,
            'cliente_id': self.cliente_id,
            'equipamento_id': self.equipamento_id,
            'status': self.status,
            'prioridade': self.prioridade,
            'tecnico_responsavel': self.tecnico_responsavel,
            'descricao_servico': self.descricao_servico,
            'diagnostico': self.diagnostico,
            'solucao_aplicada': self.solucao_aplicada,
            'valor_pecas': self.valor_pecas,
            'valor_mao_obra': self.valor_mao_obra,
            'valor_total': self.valor_total,
            'data_abertura': self.data_abertura.isoformat() if self.data_abertura else None,
            'data_previsao_entrega': self.data_previsao_entrega.isoformat() if self.data_previsao_entrega else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'data_entrega': self.data_entrega.isoformat() if self.data_entrega else None,
            'observacoes': self.observacoes,
            'itens': [item.to_dict() for item in self.itens]
        }
    
    @classmethod
    def from_row(cls, row) -> 'OrdemServico':
        return cls(
            id=row['id'],
            numero_os=row['numero_os'],
            cliente_id=row['cliente_id'],
            equipamento_id=row['equipamento_id'],
            status=row['status'],
            prioridade=row['prioridade'],
            tecnico_responsavel=row['tecnico_responsavel'] or '',
            descricao_servico=row['descricao_servico'] or '',
            diagnostico=row['diagnostico'] or '',
            solucao_aplicada=row['solucao_aplicada'] or '',
            valor_pecas=row['valor_pecas'] or 0,
            valor_mao_obra=row['valor_mao_obra'] or 0,
            valor_total=row['valor_total'] or 0,
            data_abertura=datetime.fromisoformat(row['data_abertura']) if row['data_abertura'] else None,
            data_previsao_entrega=datetime.fromisoformat(row['data_previsao_entrega']).date() if row['data_previsao_entrega'] else None,
            data_conclusao=datetime.fromisoformat(row['data_conclusao']) if row['data_conclusao'] else None,
            data_entrega=datetime.fromisoformat(row['data_entrega']) if row['data_entrega'] else None,
            observacoes=row['observacoes'] or '',
            cliente_nome=row['cliente_nome'] if 'cliente_nome' in row.keys() else '',
            equipamento_descricao=row['equipamento_descricao'] if 'equipamento_descricao' in row.keys() else ''
        )


@dataclass
class OSHistorico:
    """Histórico de movimentações da OS"""
    id: Optional[int] = None
    os_id: int = 0
    status_anterior: str = ""
    status_novo: str = ""
    descricao: str = ""
    usuario: str = ""
    data_movimentacao: Optional[datetime] = None
    
    def __post_init__(self):
        if self.data_movimentacao is None:
            self.data_movimentacao = datetime.now()
    
    @classmethod
    def from_row(cls, row) -> 'OSHistorico':
        return cls(
            id=row['id'],
            os_id=row['os_id'],
            status_anterior=row['status_anterior'] or '',
            status_novo=row['status_novo'],
            descricao=row['descricao'] or '',
            usuario=row['usuario'] or '',
            data_movimentacao=datetime.fromisoformat(row['data_movimentacao']) if row['data_movimentacao'] else None
        )


# Constantes de status e prioridades
STATUS_OS = [
    'ABERTA',
    'EM_ANDAMENTO',
    'AGUARDANDO_PECAS',
    'AGUARDANDO_APROVACAO',
    'CONCLUIDA',
    'ENTREGUE',
    'CANCELADA'
]

PRIORIDADES = ['BAIXA', 'NORMAL', 'ALTA', 'URGENTE']

TIPOS_ITEM = ['PECA', 'SERVICO']

TIPOS_EQUIPAMENTO = [
    'Notebook', 'Desktop', 'Monitor', 'Impressora', 'Celular',
    'Tablet', 'Servidor', 'Roteador', 'Switch', 'Outro'
]
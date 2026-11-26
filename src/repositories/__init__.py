#!/usr/bin/env python3
"""
Camada de acesso a dados (Repository Pattern)
"""

from datetime import datetime, date
from typing import List, Optional, Tuple

from database.connection import get_db
from models import Cliente, Equipamento, OrdemServico, OSItem, OSHistorico


class ClienteRepository:
    """Repositório de Clientes"""

    def __init__(self):
        self.db = get_db()

    def criar(self, cliente: Cliente) -> int:
        """Insere novo cliente e retorna o ID"""
        cursor = self.db.execute("""
            INSERT INTO clientes (nome, cpf_cnpj, telefone, email, endereco, cidade, estado, cep, observacoes, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cliente.nome, cliente.cpf_cnpj, cliente.telefone, cliente.email,
            cliente.endereco, cliente.cidade, cliente.estado, cliente.cep,
            cliente.observacoes, cliente.ativo
        ))
        return cursor.lastrowid

    def atualizar(self, cliente: Cliente) -> bool:
        """Atualiza cliente existente"""
        cursor = self.db.execute("""
            UPDATE clientes SET nome=?, cpf_cnpj=?, telefone=?, email=?, endereco=?,
                cidade=?, estado=?, cep=?, observacoes=?, ativo=?
            WHERE id=?
        """, (
            cliente.nome, cliente.cpf_cnpj, cliente.telefone, cliente.email,
            cliente.endereco, cliente.cidade, cliente.estado, cliente.cep,
            cliente.observacoes, cliente.ativo, cliente.id
        ))
        return cursor.rowcount > 0

    def buscar_por_id(self, id: int) -> Optional[Cliente]:
        """Busca cliente por ID"""
        row = self.db.fetch_one("SELECT * FROM clientes WHERE id = ?", (id,))
        return Cliente.from_row(row) if row else None

    def buscar_todos(self, apenas_ativos: bool = True, termo_busca: str = "") -> List[Cliente]:
        """Lista todos os clientes com filtro opcional"""
        query = "SELECT * FROM clientes"
        params = []

        conditions = []
        if apenas_ativos:
            conditions.append("ativo = 1")
        if termo_busca:
            conditions.append("(nome LIKE ? OR cpf_cnpj LIKE ? OR telefone LIKE ?)")
            params.extend([f"%{termo_busca}%"] * 3)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY nome"

        rows = self.db.fetch_all(query, tuple(params))
        return [Cliente.from_row(row) for row in rows]

    def excluir(self, id: int) -> bool:
        """Exclui cliente (soft delete - marca como inativo)"""
        cursor = self.db.execute("UPDATE clientes SET ativo = 0 WHERE id = ?", (id,))
        return cursor.rowcount > 0

    def contar(self, apenas_ativos: bool = True) -> int:
        """Conta total de clientes"""
        query = "SELECT COUNT(*) as total FROM clientes"
        if apenas_ativos:
            query += " WHERE ativo = 1"
        row = self.db.fetch_one(query)
        return row['total'] if row else 0


class EquipamentoRepository:
    """Repositório de Equipamentos"""

    def __init__(self):
        self.db = get_db()

    def criar(self, equipamento: Equipamento) -> int:
        cursor = self.db.execute("""
            INSERT INTO equipamentos (cliente_id, tipo, marca, modelo, numero_serie, defeito_relatado, acessorios)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            equipamento.cliente_id, equipamento.tipo, equipamento.marca,
            equipamento.modelo, equipamento.numero_serie, equipamento.defeito_relatado,
            equipamento.acessorios
        ))
        return cursor.lastrowid

    def atualizar(self, equipamento: Equipamento) -> bool:
        cursor = self.db.execute("""
            UPDATE equipamentos SET tipo=?, marca=?, modelo=?, numero_serie=?,
                defeito_relatado=?, acessorios=?
            WHERE id=?
        """, (
            equipamento.tipo, equipamento.marca, equipamento.modelo,
            equipamento.numero_serie, equipamento.defeito_relatado,
            equipamento.acessorios, equipamento.id
        ))
        return cursor.rowcount > 0

    def buscar_por_id(self, id: int) -> Optional[Equipamento]:
        row = self.db.fetch_one("SELECT * FROM equipamentos WHERE id = ?", (id,))
        return Equipamento.from_row(row) if row else None

    def buscar_por_cliente(self, cliente_id: int) -> List[Equipamento]:
        rows = self.db.fetch_all(
            "SELECT * FROM equipamentos WHERE cliente_id = ? ORDER BY data_cadastro DESC",
            (cliente_id,)
        )
        return [Equipamento.from_row(row) for row in rows]

    def buscar_todos(self, termo_busca: str = "") -> List[Equipamento]:
        query = "SELECT * FROM equipamentos"
        params = []
        if termo_busca:
            query += " WHERE tipo LIKE ? OR marca LIKE ? OR modelo LIKE ? OR numero_serie LIKE ?"
            params = [f"%{termo_busca}%"] * 4
        query += " ORDER BY data_cadastro DESC"
        rows = self.db.fetch_all(query, tuple(params))
        return [Equipamento.from_row(row) for row in rows]


class OSItemRepository:
    """Repositório de Itens da OS"""

    def __init__(self):
        self.db = get_db()

    def criar(self, item: OSItem) -> int:
        cursor = self.db.execute("""
            INSERT INTO os_itens (os_id, tipo, descricao, quantidade, valor_unitario, valor_total)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item.os_id, item.tipo, item.descricao, item.quantidade, item.valor_unitario, item.valor_total))
        return cursor.lastrowid

    def criar_muitos(self, itens: List[OSItem]) -> List[int]:
        ids = []
        for item in itens:
            ids.append(self.criar(item))
        return ids

    def buscar_por_os(self, os_id: int) -> List[OSItem]:
        rows = self.db.fetch_all("SELECT * FROM os_itens WHERE os_id = ? ORDER BY id", (os_id,))
        return [OSItem.from_row(row) for row in rows]

    def excluir_por_os(self, os_id: int) -> bool:
        cursor = self.db.execute("DELETE FROM os_itens WHERE os_id = ?", (os_id,))
        return cursor.rowcount > 0

    def calcular_totais(self, os_id: int) -> Tuple[float, float]:
        """Calcula totais de peças e mão de obra"""
        row = self.db.fetch_one("""
            SELECT 
                SUM(CASE WHEN tipo = 'PECA' THEN valor_total ELSE 0 END) as total_pecas,
                SUM(CASE WHEN tipo = 'SERVICO' THEN valor_total ELSE 0 END) as total_servicos
            FROM os_itens WHERE os_id = ?
        """, (os_id,))
        return (row['total_pecas'] or 0, row['total_servicos'] or 0)


class OSHistoricoRepository:
    """Repositório de Histórico da OS"""

    def __init__(self):
        self.db = get_db()

    def registrar(self, historico: OSHistorico) -> int:
        cursor = self.db.execute("""
            INSERT INTO os_historico (os_id, status_anterior, status_novo, descricao, usuario)
            VALUES (?, ?, ?, ?, ?)
        """, (historico.os_id, historico.status_anterior, historico.status_novo,
              historico.descricao, historico.usuario))
        return cursor.lastrowid

    def buscar_por_os(self, os_id: int) -> List[OSHistorico]:
        rows = self.db.fetch_all(
            "SELECT * FROM os_historico WHERE os_id = ? ORDER BY data_movimentacao DESC",
            (os_id,)
        )
        return [OSHistorico.from_row(row) for row in rows]


class OrdemServicoRepository:
    """Repositório de Ordens de Serviço"""

    def __init__(self):
        self.db = get_db()
        self.itens_repo = OSItemRepository()
        self.historico_repo = OSHistoricoRepository()

    def _proximo_numero_os(self) -> str:
        """Gera próximo número de OS sequencial"""
        now = datetime.now()
        prefix = f"OS{now.strftime('%Y%m%d')}"
        row = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM ordens_servico WHERE numero_os LIKE ?",
            (f"{prefix}%",)
        )
        count = (row['count'] if row else 0) + 1
        return f"{prefix}{count:04d}"

    def criar(self, os: OrdemServico, usuario: str = "Sistema") -> int:
        # Gera número se não tiver
        if not os.numero_os:
            os.numero_os = self._proximo_numero_os()

        # Calcula totais a partir dos itens
        os.valor_pecas = sum(i.valor_total for i in os.itens if i.tipo == 'PECA')
        os.valor_mao_obra = sum(i.valor_total for i in os.itens if i.tipo == 'SERVICO')
        os.valor_total = os.valor_pecas + os.valor_mao_obra

        cursor = self.db.execute("""
            INSERT INTO ordens_servico (
                numero_os, cliente_id, equipamento_id, status, prioridade,
                tecnico_responsavel, descricao_servico, diagnostico, solucao_aplicada,
                valor_pecas, valor_mao_obra, valor_total, data_previsao_entrega, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            os.numero_os, os.cliente_id, os.equipamento_id, os.status, os.prioridade,
            os.tecnico_responsavel, os.descricao_servico, os.diagnostico, os.solucao_aplicada,
            os.valor_pecas, os.valor_mao_obra, os.valor_total,
            os.data_previsao_entrega.isoformat() if os.data_previsao_entrega else None,
            os.observacoes
        ))
        os_id = cursor.lastrowid
        os.id = os_id

        # Salva itens
        for item in os.itens:
            item.os_id = os_id
            self.itens_repo.criar(item)

        # Registra no histórico
        self.historico_repo.registrar(OSHistorico(
            os_id=os_id,
            status_anterior="",
            status_novo=os.status,
            descricao="Ordem de serviço criada",
            usuario=usuario
        ))

        return os_id

    def atualizar(self, os: OrdemServico, usuario: str = "Sistema") -> bool:
        # Busca status anterior para histórico
        os_antiga = self.buscar_por_id(os.id)
        status_anterior = os_antiga.status if os_antiga else ""

        os.valor_total = os.valor_pecas + os.valor_mao_obra

        cursor = self.db.execute("""
            UPDATE ordens_servico SET
                cliente_id=?, equipamento_id=?, status=?, prioridade=?,
                tecnico_responsavel=?, descricao_servico=?, diagnostico=?,
                solucao_aplicada=?, valor_pecas=?, valor_mao_obra=?, valor_total=?,
                data_previsao_entrega=?, observacoes=?
            WHERE id=?
        """, (
            os.cliente_id, os.equipamento_id, os.status, os.prioridade,
            os.tecnico_responsavel, os.descricao_servico, os.diagnostico,
            os.solucao_aplicada, os.valor_pecas, os.valor_mao_obra, os.valor_total,
            os.data_previsao_entrega.isoformat() if os.data_previsao_entrega else None,
            os.observacoes, os.id
        ))

        # Atualiza itens
        self.itens_repo.excluir_por_os(os.id)
        for item in os.itens:
            item.os_id = os.id
            self.itens_repo.criar(item)

        # Registra mudança de status no histórico
        if status_anterior and status_anterior != os.status:
            self.historico_repo.registrar(OSHistorico(
                os_id=os.id,
                status_anterior=status_anterior,
                status_novo=os.status,
                descricao=f"Status alterado de {status_anterior} para {os.status}",
                usuario=usuario
            ))

        return cursor.rowcount > 0

    def buscar_por_id(self, id: int) -> Optional[OrdemServico]:
        row = self.db.fetch_one("""
            SELECT os.*, c.nome as cliente_nome, 
                   e.tipo || ' - ' || COALESCE(e.marca, '') || ' ' || COALESCE(e.modelo, '') as equipamento_descricao
            FROM ordens_servico os
            JOIN clientes c ON os.cliente_id = c.id
            JOIN equipamentos e ON os.equipamento_id = e.id
            WHERE os.id = ?
        """, (id,))

        if not row:
            return None

        os = OrdemServico.from_row(row)
        os.itens = self.itens_repo.buscar_por_os(id)
        return os

    def buscar_por_numero(self, numero_os: str) -> Optional[OrdemServico]:
        row = self.db.fetch_one("SELECT * FROM ordens_servico WHERE numero_os = ?", (numero_os,))
        if row:
            return self.buscar_por_id(row['id'])
        return None

    def listar(self,
               status: str = None,
               cliente_id: int = None,
               data_inicio: date = None,
               data_fim: date = None,
               termo_busca: str = "",
               pagina: int = 1,
               por_pagina: int = 50) -> Tuple[List[OrdemServico], int]:
        """Lista OS com paginação e filtros"""
        conditions = []
        params = []

        if status:
            conditions.append("os.status = ?")
            params.append(status)

        if cliente_id:
            conditions.append("os.cliente_id = ?")
            params.append(cliente_id)

        if data_inicio:
            conditions.append("date(os.data_abertura) >= ?")
            params.append(data_inicio.isoformat())

        if data_fim:
            conditions.append("date(os.data_abertura) <= ?")
            params.append(data_fim.isoformat())

        if termo_busca:
            conditions.append("""
                (os.numero_os LIKE ? OR c.nome LIKE ? OR os.descricao_servico LIKE ? 
                 OR os.tecnico_responsavel LIKE ?)
            """)
            params.extend([f"%{termo_busca}%"] * 4)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # Conta total
        count_query = f"""
            SELECT COUNT(*) as total 
            FROM ordens_servico os
            JOIN clientes c ON os.cliente_id = c.id
            {where_clause}
        """
        count_row = self.db.fetch_one(count_query, tuple(params))
        total = count_row['total'] if count_row else 0

        # Busca paginada
        offset = (pagina - 1) * por_pagina
        query = f"""
            SELECT os.*, c.nome as cliente_nome,
                   e.tipo || ' - ' || COALESCE(e.marca, '') || ' ' || COALESCE(e.modelo, '') as equipamento_descricao
            FROM ordens_servico os
            JOIN clientes c ON os.cliente_id = c.id
            JOIN equipamentos e ON os.equipamento_id = e.id
            {where_clause}
            ORDER BY os.data_abertura DESC
            LIMIT ? OFFSET ?
        """
        params.extend([por_pagina, offset])

        rows = self.db.fetch_all(query, tuple(params))
        ordens = [OrdemServico.from_row(row) for row in rows]

        # Carrega itens para cada OS
        for os in ordens:
            os.itens = self.itens_repo.buscar_por_os(os.id)

        return ordens, total

    def alterar_status(self, os_id: int, novo_status: str, usuario: str = "Sistema", descricao: str = "") -> bool:
        """Altera apenas o status da OS"""
        os_atual = self.buscar_por_id(os_id)
        if not os_atual:
            return False

        status_anterior = os_atual.status
        if status_anterior == novo_status:
            return True

        # Atualiza data de conclusão/entrega conforme status
        data_conclusao = None
        data_entrega = None
        if novo_status == 'CONCLUIDA':
            data_conclusao = datetime.now()
        elif novo_status == 'ENTREGUE':
            data_conclusao = os_atual.data_conclusao or datetime.now()
            data_entrega = datetime.now()

        cursor = self.db.execute("""
            UPDATE ordens_servico SET status = ?, data_conclusao = ?, data_entrega = ?
            WHERE id = ?
        """, (novo_status,
              data_conclusao.isoformat() if data_conclusao else None,
              data_entrega.isoformat() if data_entrega else None,
              os_id))

        if cursor.rowcount > 0:
            self.historico_repo.registrar(OSHistorico(
                os_id=os_id,
                status_anterior=status_anterior,
                status_novo=novo_status,
                descricao=descricao or f"Status alterado de {status_anterior} para {novo_status}",
                usuario=usuario
            ))
            return True
        return False

    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas gerais"""
        stats = {}

        # Total por status
        rows = self.db.fetch_all("""
            SELECT status, COUNT(*) as total 
            FROM ordens_servico 
            GROUP BY status
        """)
        stats['por_status'] = {row['status']: row['total'] for row in rows}

        # Total geral
        row = self.db.fetch_one("SELECT COUNT(*) as total FROM ordens_servico")
        stats['total'] = row['total'] if row else 0

        # Valor total em aberto
        row = self.db.fetch_one("""
            SELECT SUM(valor_total) as total 
            FROM ordens_servico 
            WHERE status NOT IN ('ENTREGUE', 'CANCELADA')
        """)
        stats['valor_em_aberto'] = row['total'] or 0

        # OSs do mês atual
        row = self.db.fetch_one("""
            SELECT COUNT(*) as total 
            FROM ordens_servico 
            WHERE strftime('%Y-%m', data_abertura) = strftime('%Y-%m', 'now')
        """)
        stats['mes_atual'] = row['total'] if row else 0

        return stats

    def excluir(self, id: int) -> bool:
        """Exclui OS e seus itens/histórico (CASCADE)"""
        cursor = self.db.execute("DELETE FROM ordens_servico WHERE id = ?", (id,))
        return cursor.rowcount > 0

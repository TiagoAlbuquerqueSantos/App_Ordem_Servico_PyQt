#!/usr/bin/env python3
"""
Módulo de conexão com banco de dados SQLite
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional


class DatabaseConnection:
    """Gerenciador de conexão com banco de dados SQLite"""
    
    _instance: Optional['DatabaseConnection'] = None
    _db_path: Path
    
    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Define o caminho do banco na pasta do usuário
            if db_path is None:
                data_dir = Path.home() / ".ordem_servico"
                data_dir.mkdir(exist_ok=True)
                cls._db_path = data_dir / "ordens.db"
            else:
                cls._db_path = Path(db_path)
        return cls._instance
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexão com o banco"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Executa uma query e retorna o cursor"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Executa query e retorna uma linha"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()) -> list:
        """Executa query e retorna todas as linhas"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def execute_many(self, query: str, params_list: list) -> None:
        """Executa múltiplas queries"""
        with self.get_connection() as conn:
            conn.executemany(query, params_list)


def get_db() -> DatabaseConnection:
    """Retorna a instância singleton do banco de dados"""
    return DatabaseConnection()


def init_database(db_path: str = None) -> None:
    """Inicializa o banco de dados criando as tabelas necessárias"""
    db = DatabaseConnection(db_path)
    
    with db.get_connection() as conn:
        # Tabela de clientes
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf_cnpj TEXT,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                observacoes TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1
            )
        """)
        
        # Tabela de equipamentos
        conn.execute("""
            CREATE TABLE IF NOT EXISTS equipamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                marca TEXT,
                modelo TEXT,
                numero_serie TEXT,
                defeito_relatado TEXT,
                acessorios TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de ordens de serviço
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ordens_servico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_os TEXT UNIQUE NOT NULL,
                cliente_id INTEGER NOT NULL,
                equipamento_id INTEGER NOT NULL,
                status TEXT DEFAULT 'ABERTA',
                prioridade TEXT DEFAULT 'NORMAL',
                tecnico_responsavel TEXT,
                descricao_servico TEXT,
                diagnostico TEXT,
                solucao_aplicada TEXT,
                valor_pecas REAL DEFAULT 0,
                valor_mao_obra REAL DEFAULT 0,
                valor_total REAL DEFAULT 0,
                data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_previsao_entrega DATE,
                data_conclusao TIMESTAMP,
                data_entrega TIMESTAMP,
                observacoes TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
                FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id) ON DELETE RESTRICT
            )
        """)
        
        # Tabela de itens da OS (peças/serviços)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS os_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                os_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,  -- 'PECA' ou 'SERVICO'
                descricao TEXT NOT NULL,
                quantidade INTEGER DEFAULT 1,
                valor_unitario REAL DEFAULT 0,
                valor_total REAL DEFAULT 0,
                FOREIGN KEY (os_id) REFERENCES ordens_servico(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de histórico/movimentações da OS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS os_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                os_id INTEGER NOT NULL,
                status_anterior TEXT,
                status_novo TEXT NOT NULL,
                descricao TEXT,
                usuario TEXT,
                data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (os_id) REFERENCES ordens_servico(id) ON DELETE CASCADE
            )
        """)
        
        # Índices para performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_os_cliente ON ordens_servico(cliente_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_os_status ON ordens_servico(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_os_data_abertura ON ordens_servico(data_abertura)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_equip_cliente ON equipamentos(cliente_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes(nome)")
        
        conn.commit()


if __name__ == "__main__":
    init_database()
    print("Banco de dados inicializado com sucesso!")
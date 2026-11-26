# Sistema de Ordem de Serviço

Aplicação desktop para gestão de ordens de serviço, desenvolvida em Python com PyQt6.

## Funcionalidades

- **Gestão de Clientes**: Cadastro, edição, listagem e busca de clientes
- **Gestão de Equipamentos**: Vinculo equipamentos aos clientes
- **Ordens de Serviço**: 
  - Criação, edição, duplicação e exclusão
  - Controle de status (Aberta, Em Andamento, Aguardando Peças, Aguardando Aprovação, Concluída, Entregue, Cancelada)
  - Prioridades (Baixa, Normal, Alta, Urgente)
  - Atribuição de técnico responsável
  - Data de previsão de entrega
- **Itens da OS**: 
  - Peças (com quantidade e valor)
  - Serviços/Mão de Obra
  - Cálculo automático de totais
- **Histórico**: Rastreamento completo de mudanças de status
- **Filtros e Busca**: Por status, prioridade, data, texto livre
- **Paginação**: Navegação em grandes volumes de dados
- **Relatórios**: Base para relatórios (em desenvolvimento)
- **Impressão**: Visualização e impressão da OS formatada

## Requisitos

- Python 3.9+
- PyQt6

## Instalação

```bash
# Clone ou baixe o projeto
cd ordem_servico

# Crie um ambiente virtual (opcional mas recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

## Estrutura do Projeto

```
ordem_servico/
├── main.py                 # Ponto de entrada
├── requirements.txt        # Dependências
├── database/
│   ├── __init__.py
│   └── connection.py       # Conexão SQLite e schema
├── models/
│   └── __init__.py         # Dataclasses (Cliente, Equipamento, OS, etc.)
├── repositories/
│   └── __init__.py         # Camada de acesso a dados
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # Janela principal
│   ├── dialogs.py          # Dialogs (Cliente, Equipamento, OS, Itens, etc.)
│   └── widgets.py          # Widgets customizados (Badges, MoneyEdit)
└── resources/
    └── style.qss           # Estilos QSS
```

## Banco de Dados

O banco SQLite é criado automaticamente na primeira execução em:
- Linux: `~/.ordem_servico/ordens.db`
- Windows: `%USERPROFILE%\.ordem_servico\ordens.db`

### Tabelas

- `clientes` - Dados dos clientes
- `equipamentos` - Equipamentos vinculados aos clientes
- `ordens_servico` - Ordens de serviço principais
- `os_itens` - Itens (peças/serviços) de cada OS
- `os_historico` - Histórico de mudanças de status

## Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl+N` | Nova OS |
| `Ctrl+Shift+C` | Novo Cliente |
| `Ctrl+Shift+E` | Novo Equipamento |
| `Ctrl+E` | Editar OS selecionada |
| `Delete` | Excluir OS selecionada |
| `F5` | Atualizar lista |
| `Escape` | Limpar seleção |
| `Enter` | Editar OS selecionada |
| `Ctrl+P` | Imprimir OS |

## Personalização

### Temas

Edite `resources/style.qss` para personalizar cores, fontes e estilos.

### Campos Adicionais

Para adicionar campos:
1. Adicione ao modelo em `models/__init__.py`
2. Atualize o schema em `database/connection.py`
3. Atualize o repository correspondente
4. Adicione nos dialogs em `ui/dialogs.py`
5. Atualize a tabela em `ui/main_window.py`

## Licença

Projeto de exemplo para fins educacionais.
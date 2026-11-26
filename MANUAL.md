# Manual do Usuário - Sistema de Ordem de Serviço

## Índice
1. [Visão Geral](#visão-geral)
2. [Instalação e Execução](#instalação-e-execução)
3. [Interface Principal](#interface-principal)
4. [Gerenciamento de Clientes](#gerenciamento-de-clientes)
5. [Gerenciamento de Equipamentos](#gerenciamento-de-equipamentos)
6. [Ordens de Serviço](#ordens-de-serviço)
7. [Filtros e Busca](#filtros-e-busca)
8. [Temas (Claro/Escuro)](#temas-claroescuro)
9. [Atalhos de Teclado](#atalhos-de-teclado)
10. [Relatórios e Impressão](#relatórios-e-impressão)
11. [Configurações](#configurações)
12. [Backup e Dados](#backup-e-dados)
13. [Solução de Problemas](#solução-de-problemas)

---

## Visão Geral

O **Sistema de Ordem de Serviço** é uma aplicação desktop desenvolvida em Python com PyQt6 para gestão completa de ordens de serviço de assistência técnica. 

### Principais Funcionalidades
- ✅ Cadastro e gestão de clientes
- ✅ Cadastro de equipamentos por cliente
- ✅ Criação, edição e acompanhamento de ordens de serviço
- ✅ Controle de peças e serviços (mão de obra) com cálculo automático de totais
- ✅ Histórico completo de mudanças de status
- ✅ Filtros avançados e paginação
- ✅ Temas claro/escuro com persistência
- ✅ Impressão de ordens de serviço
- ✅ Banco de dados local SQLite (sem necessidade de servidor)

---

## Instalação e Execução

### Pré-requisitos
- Python 3.10 ou superior
- PyQt6

### Linux/macOS
```bash
# Navegue até a pasta do programa
cd /caminho/para/ordem_servico

# Torne o script executável (apenas na primeira vez)
chmod +x run.sh

# Execute
./run.sh
```

### Windows
```cmd
# Duplo clique no arquivo run.bat
# Ou via terminal:
run.bat
```

### Execução Direta (Qualquer SO)
```bash
python main.py
# Ou especificando o Python:
python3.11 main.py
```

### Primeira Execução
Na primeira execução, o sistema criará automaticamente:
- Banco de dados SQLite em `~/.ordem_servico/ordens.db` (Linux/macOS) ou `%USERPROFILE%\.ordem_servico\ordens.db` (Windows)
- Tabelas necessárias (clientes, equipamentos, ordens, itens, histórico)

---

## Interface Principal

A janela principal é dividida em duas áreas principais:

### Área Superior - Lista de Ordens de Serviço
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔍 Busca: [________________]  Status: [▼]  Prioridade: [▼]  De: [📅] Até: [📅] [Limpar]  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Nº OS    │ Cliente           │ Equipamento        │ Status      │ Prior. │ ... │
├──────────┼───────────────────┼────────────────────┼─────────────┼────────┼─────┤
│ OS2024...│ João Silva        │ Notebook - Dell    │ 🔵 ABERTA   │ 🟡 NOR │ ... │
│ OS2024...│ Maria Santos      │ Impressora - HP    │ 🟠 EM_ANDAM │ 🔴 ALT │ ... │
└──────────┴───────────────────┴────────────────────┴─────────────┴────────┴─────┘
│ [« Primeira] [‹ Anterior]  Página 1 de 5 (47 registros)  [Próxima ›] [Última »]  Por página: [50 ▼] │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Área Inferior - Detalhes da OS Selecionada (Abas)
| Aba | Descrição |
|-----|-----------|
| **📋 Informações** | Dados completos da OS, cliente, equipamento, valores, descrições |
| **📦 Itens** | Lista de peças e serviços com valores |
| **📜 Histórico** | Linha do tempo de mudanças de status |

### Barra de Ferramentas Superior
| Botão/Ação | Função | Atalho |
|------------|--------|--------|
| ➕ Nova OS | Cria nova ordem de serviço | `Ctrl+N` |
| 👤 Novo Cliente | Cadastra novo cliente | `Ctrl+Shift+C` |
| 💻 Novo Equipamento | Cadastra novo equipamento | `Ctrl+Shift+E` |
| ✏️ Editar OS | Edita OS selecionada | `Ctrl+E` |
| 📋 Duplicar | Duplica OS selecionada | - |
| 🗑️ Excluir | Exclui OS selecionada | `Delete` |
| 🔄 Alterar Status | Menu rápido de mudança de status | - |
| 🖨️ Imprimir OS | Abre visualização de impressão | `Ctrl+P` |
| 📊 Exportar | Exporta dados (em desenvolvimento) | - |
| 📈 Relatórios | Abre tela de relatórios | - |
| ⚙️ Configurações | Abre configurações do sistema | - |
| 🔄 Atualizar | Recarrega lista de OS | `F5` |
| 🌙/☀️ Tema | Alterna tema escuro/claro | - |

### Barra de Status
- **Mensagens do sistema** (lado esquerdo)
- **Total de registros** (lado direito)
- **Versão do sistema** (lado direito)

---

## Gerenciamento de Clientes

### Novo Cliente
1. Clique em **👤 Novo Cliente** (ou `Ctrl+Shift+C`)
2. Preencha os campos:
   - **Nome** * (obrigatório): Nome completo ou razão social
   - **CPF/CNPJ**: Apenas números
   - **Telefone**: Formato livre
   - **E-mail**: Para contato
   - **Endereço, Cidade, Estado, CEP**: Endereço completo
   - **Observações**: Informações adicionais
   - **Cliente Ativo**: Marque para clientes ativos
3. Clique em **Salvar**

### Editar Cliente
- Através da OS: Ao criar/editar uma OS, o combo de clientes permite busca
- Não há lista direta de clientes na interface principal (use a busca no combo)

### Busca de Clientes
No combo de seleção de cliente (ao criar/editar OS):
- Digite parte do nome, CPF/CNPJ ou telefone
- O sistema filtra automaticamente (autocomplete)

---

## Gerenciamento de Equipamentos

### Novo Equipamento
1. Clique em **💻 Novo Equipamento** (ou `Ctrl+Shift+E`)
2. **Selecione o cliente** (obrigatório)
3. Preencha:
   - **Tipo** *: Notebook, Desktop, Monitor, Impressora, Celular, Tablet, Servidor, Roteador, Switch, Outro
   - **Marca**: Ex: Dell, HP, Samsung
   - **Modelo**: Ex: Inspiron 15, LaserJet Pro
   - **Nº Série/IMEI**: Identificador único
   - **Defeito Relatado**: Descrição do problema informado pelo cliente
   - **Acessórios**: Carregador, mouse, capa, fonte, etc.
4. Clique em **Salvar**

### Equipamentos do Cliente
Ao selecionar um cliente na OS, apenas os equipamentos desse cliente aparecem no combo.

---

## Ordens de Serviço

### Status da OS
| Status | Cor | Descrição |
|--------|-----|-----------|
| **ABERTA** | 🔵 Azul | OS recém-criada, aguardando início |
| **EM_ANDAMENTO** | 🟠 Laranja | Serviço em execução |
| **AGUARDANDO_PECAS** | 🔴 Vermelho | Parada aguardando chegada de peças |
| **AGUARDANDO_APROVACAO** | 🟣 Roxo | Aguardando aprovação do orçamento pelo cliente |
| **CONCLUIDA** | 🟢 Verde | Serviço finalizado, pronto para entrega |
| **ENTREGUE** | ⚫ Cinza escuro | Equipamento entregue ao cliente |
| **CANCELADA** | ⚪ Cinza | OS cancelada |

### Prioridades
| Prioridade | Cor | Uso |
|------------|-----|-----|
| **BAIXA** | 🟢 Verde | Sem urgência |
| **NORMAL** | 🟡 Amarelo | Padrão |
| **ALTA** | 🟠 Laranja | Urgente |
| **URGENTE** | 🔴 Vermelho | Emergência |

### Criar Nova OS
1. Clique em **➕ Nova OS** (ou `Ctrl+N`)
2. **Aba Dados Principais**:
   - Selecione **Cliente** (busca por nome/CPF)
   - Selecione **Equipamento** (filtrado pelo cliente)
   - **Status**: Deixe como ABERTA
   - **Prioridade**: Escolha conforme urgência
   - **Técnico Responsável**: Nome do técnico
   - **Previsão de Entrega**: Data estimada
   - **Descrição do Serviço**: O que será feito
3. **Aba Itens (Peças/Serviços)**:
   - Clique **➕ Adicionar Peça** ou **⚙️ Adicionar Serviço**
   - Preencha: Descrição, Quantidade, Valor Unitário
   - O **Total** é calculado automaticamente
   - Adicione quantos itens precisar
4. **Aba Observações**: Informações extras
5. Clique **Salvar**

### Editar OS
1. Selecione a OS na lista (clique na linha)
2. Clique **✏️ Editar OS** (ou `Ctrl+E` ou duplo clique)
3. Modifique os campos necessários
4. Na aba **Itens**, pode adicionar/editar/remover peças e serviços
5. Clique **Salvar**

### Duplicar OS
1. Selecione a OS
2. Clique **📋 Duplicar**
3. Cria nova OS com mesmo cliente, equipamento, prioridade, técnico, descrição e itens
4. Status volta para **ABERTA**, diagnóstico e solução são limpos

### Alterar Status Rapidamente
1. Selecione a OS
2. Clique em **🔄 Alterar Status ▼**
3. Escolha o novo status no menu
4. O sistema atualiza automaticamente:
   - **CONCLUIDA** → Define data de conclusão
   - **ENTREGUE** → Define data de entrega

### Excluir OS
1. Selecione a OS
2. Clique **🗑️ Excluir** (ou `Delete`)
3. Confirme na caixa de diálogo
4. **Atenção**: Exclusão permanente (itens e histórico também são removidos)

---

## Filtros e Busca

### Barra de Filtros (Acima da Tabela)
| Filtro | Descrição |
|--------|-----------|
| **Busca** | Texto livre: busca em nº OS, nome do cliente, descrição, técnico |
| **Status** | Filtra por um status específico |
| **Prioridade** | Filtra por prioridade |
| **De / Até** | Intervalo de data de abertura |
| **Limpar** | Remove todos os filtros |

### Paginação
- **« Primeira** / **‹ Anterior** / **Próxima ›** / **Última »**: Navegação entre páginas
- **Por página**: 25, 50, 100 ou 200 registros por página
- Contador: "Página X de Y (Z registros)"

### Dicas de Busca
- Use a busca textual para encontrar OS por termo parcial
- Combine filtros: ex: Status "ABERTA" + Prioridade "URGENTE"
- A busca é case-insensitive (não diferencia maiúsculas/minúsculas)

---

## Temas (Claro/Escuro)

### Alternar Tema
Clique no botão **🌙 Tema Escuro** / **☀️ Tema Claro** na barra de ferramentas.

### Características
- **Padrão**: Tema escuro (Catppuccin Mocha) - melhor para uso prolongado
- **Persistência**: Preferência salva automaticamente
- **Aplicação Imediata**: Mudança instantânea sem reiniciar

### Tema Escuro (Padrão)
- Fundo escuro (#1e1e2e)
- Texto claro (#cdd6f4)
- Acentos em azul (#89b4fa)
- Reduz fadiga ocular

### Tema Claro
- Fundo claro (#f5f6fa)
- Texto escuro (#2c3e50)
- Acentos em azul (#3498db)
- Aspecto tradicional

---

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

---

## Relatórios e Impressão

### Imprimir OS
1. Selecione a OS desejada
2. Clique **🖨️ Imprimir OS** (ou `Ctrl+P`)
3. Na janela de detalhes, clique **🖨️ Imprimir**
4. Escolha a impressora e configure:
   - Orientação: Retrato
   - Margens: Padrão
5. Clique **Imprimir**

### Conteúdo da Impressão
- Cabeçalho com nº OS e status
- Dados do cliente e equipamento
- Descrição do serviço, diagnóstico, solução
- Tabela de itens (peças e serviços) com valores
- Totais: Peças, Mão de Obra, Total Geral
- Observações (se houver)

### Relatórios (Em Desenvolvimento)
Menu **📈 Relatórios** oferece:
- OS por Status
- Faturamento por Período
- OS por Cliente
- OS por Técnico
- Peças mais Utilizadas

---

## Configurações

Acesse via **⚙️ Configurações** na barra de ferramentas.

### Aba Geral
- **Empresa**: Nome da assistência técnica
- **CNPJ**: CNPJ da empresa
- **Endereço**: Endereço completo
- **Telefone**: Telefone de contato
- **E-mail**: E-mail da empresa

### Aba Ordens de Serviço
- **Dias de Garantia**: Prazo de garantia padrão (padrão: 90 dias)
- **Backup Automático Diário**: Ativa backup automático (padrão: ligado)

### Aba Aparência
- **Tema**: Claro / Escuro / Sistema (mesmo do botão na toolbar)

---

## Backup e Dados

### Local do Banco de Dados
| Sistema | Caminho |
|---------|---------|
| Linux | `~/.ordem_servico/ordens.db` |
| macOS | `~/.ordem_servico/ordens.db` |
| Windows | `%USERPROFILE%\.ordem_servico\ordens.db` |

### Backup Manual
```bash
# Linux/macOS
cp ~/.ordem_servico/ordens.db ~/backup_ordens_$(date +%Y%m%d).db

# Windows (PowerShell)
Copy-Item "$env:USERPROFILE\.ordem_servico\ordens.db" "$env:USERPROFILE\backup_ordens_$(Get-Date -Format 'yyyyMMdd').db"
```

### Restaurar Backup
```bash
# Linux/macOS
cp ~/backup_ordens_20240115.db ~/.ordem_servico/ordens.db

# Windows
Copy-Item "backup_ordens_20240115.db" "$env:USERPROFILE\.ordem_servico\ordens.db"
```

### Estrutura das Tabelas
| Tabela | Descrição |
|--------|-----------|
| `clientes` | Dados dos clientes |
| `equipamentos` | Equipamentos vinculados a clientes |
| `ordens_servico` | Ordens de serviço principais |
| `os_itens` | Peças e serviços de cada OS |
| `os_historico` | Histórico de mudanças de status |

---

## Solução de Problemas

### O programa não abre
1. Verifique se Python 3.10+ está instalado: `python --version`
2. Instale dependências: `pip install PyQt6`
3. Execute via terminal para ver mensagens de erro: `python main.py`

### Erro "ModuleNotFoundError: PyQt6"
```bash
pip install PyQt6
# Ou no Linux:
python3.11 -m pip install PyQt6
```

### Banco de dados corrompido / não abre
1. Feche o programa
2. Renomeie o banco antigo: `mv ~/.ordem_servico/ordens.db ~/.ordem_servico/ordens.db.backup`
3. Reinicie o programa (criará banco novo)
4. Restaure do backup se necessário

### Tema não aplica / interface estranha
1. Vá em **Configurações > Aparência** e selecione o tema desejado
2. Ou clique no botão de tema na toolbar
3. Reinicie o programa se persistir

### Lentidão na lista de OS
- Reduza "Por página" para 25
- Use filtros de data para limitar resultados
- O sistema usa paginação - apenas 50 registros carregados por vez

### Impressão não funciona
- Verifique se há impressora configurada no sistema
- No Linux: `systemctl status cups`
- Tente "Microsoft Print to PDF" ou "Salvar como PDF"

### Dados não salvam
- Verifique permissões de escrita na pasta `~/.ordem_servico/`
- No Linux: `chmod 755 ~/.ordem_servico`
- Verifique espaço em disco: `df -h`

---

## Suporte e Contato

Para dúvidas, sugestões ou relatório de bugs:
- Consulte este manual
- Verifique logs no terminal ao executar `python main.py`
- O banco SQLite pode ser inspecionado com ferramentas como **DB Browser for SQLite**

---

## Versão e Histórico

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0.0 | 2024 | Versão inicial: CRUD completo, temas, impressão, filtros |

---

*Manual do Sistema de Ordem de Serviço v1.0.0*
*Desenvolvido com Python 3.11 + PyQt6*
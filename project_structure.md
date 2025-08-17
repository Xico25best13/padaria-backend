# Estrutura do Projeto Padaria Platform

## Estrutura de Pastas

```
padaria_platform/
├── venv/                           # Ambiente virtual Python
├── src/                            # Código fonte da aplicação
│   ├── __init__.py
│   ├── main.py                     # Ponto de entrada da aplicação Flask
│   ├── models/                     # Modelos da base de dados
│   │   ├── __init__.py
│   │   ├── user.py                 # Modelo de utilizador (template)
│   │   ├── boss.py                 # Modelo do patrão
│   │   ├── seller.py               # Modelo do vendedor
│   │   ├── product.py              # Modelo do produto
│   │   ├── customer.py             # Modelo do cliente
│   │   ├── sale.py                 # Modelo da venda
│   │   ├── credit.py               # Modelo do crédito
│   │   └── sync.py                 # Modelos para sincronização offline
│   ├── routes/                     # Rotas da API REST
│   │   ├── __init__.py
│   │   ├── user.py                 # Rotas de utilizador (template)
│   │   ├── auth.py                 # Rotas de autenticação
│   │   ├── boss.py                 # Rotas do patrão
│   │   ├── seller.py               # Rotas do vendedor
│   │   ├── product.py              # Rotas de produtos
│   │   ├── customer.py             # Rotas de clientes
│   │   ├── sale.py                 # Rotas de vendas
│   │   ├── credit.py               # Rotas de créditos
│   │   └── sync.py                 # Rotas de sincronização
│   ├── services/                   # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── auth_service.py         # Serviços de autenticação
│   │   ├── sale_service.py         # Serviços de vendas
│   │   ├── credit_service.py       # Serviços de créditos
│   │   └── sync_service.py         # Serviços de sincronização
│   ├── utils/                      # Utilitários
│   │   ├── __init__.py
│   │   ├── validators.py           # Validadores
│   │   └── helpers.py              # Funções auxiliares
│   ├── static/                     # Ficheiros estáticos (Frontend)
│   │   ├── index.html              # Página principal
│   │   ├── css/                    # Estilos CSS
│   │   ├── js/                     # JavaScript
│   │   │   ├── app.js              # Aplicação principal
│   │   │   ├── offline.js          # Funcionalidade offline
│   │   │   └── sync.js             # Sincronização
│   │   ├── sw.js                   # Service Worker
│   │   └── manifest.json           # Manifesto PWA
│   └── database/                   # Base de dados
│       └── app.db                  # Ficheiro SQLite
└── requirements.txt                # Dependências Python
```

## Módulos Principais

### Backend (Flask)
- **main.py**: Configuração e inicialização da aplicação Flask
- **models/**: Definição dos modelos de dados usando SQLAlchemy
- **routes/**: Endpoints da API REST organizados por funcionalidade
- **services/**: Lógica de negócio separada das rotas
- **utils/**: Funções utilitárias e validadores

### Frontend (PWA)
- **static/**: Aplicação web progressiva com funcionalidade offline
- **sw.js**: Service Worker para cache e sincronização offline
- **manifest.json**: Configuração da PWA

### Base de Dados
- **SQLite**: Para desenvolvimento local
- **PostgreSQL**: Para produção (configuração a ser adicionada)


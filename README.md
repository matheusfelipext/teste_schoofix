# SchoolFix — Backend (Flask + SQLAlchemy)

Substitui a versão anterior (Firebase). Banco relacional via SQLAlchemy — SQLite em desenvolvimento, PostgreSQL em produção, sem mudar nenhuma linha de código, só a variável `DATABASE_URL`.

## Estrutura

```
schoolfix-flask/
├── app/
│   ├── __init__.py         # app factory — registra tudo
│   ├── config.py           # lê variáveis de ambiente
│   ├── extensions.py       # db, migrate, jwt, cors
│   ├── auth.py             # decorators @login_requerido e @perfil_requerido
│   ├── models.py           # Usuario, Area, Chamado, Resposta, Canal, Conversa, Notificacao...
│   └── routes/
│       ├── auth_routes.py         # /api/auth/register, /login, /me
│       ├── chamados_routes.py     # /api/chamados — com roteamento automático por área
│       ├── usuarios_routes.py     # /api/usuarios — exclusivo diretor
│       ├── areas_routes.py        # /api/areas
│       ├── chat_routes.py         # /api/canais, /api/conversas
│       └── notificacoes_routes.py # /api/notificacoes
├── instance/                # onde o schoolfix.db (SQLite) é criado
├── seed.py                  # popula áreas + usuários de teste
├── run.py                   # ponto de entrada
├── requirements.txt
└── .env.example
```

## Como rodar

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Copiar as variáveis de ambiente
cp .env.example .env

# 4. Popular o banco com dados de teste (cria as tabelas automaticamente)
python seed.py

# 5. Rodar o servidor
python run.py
```

O servidor sobe em `http://127.0.0.1:5000`. Teste rápido:
```bash
curl http://127.0.0.1:5000/api/health
```

## Testando o login

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"diretora@schoolfix.com","senha":"123456"}'
```
Isso retorna um `access_token` — use nas próximas chamadas assim:
```bash
curl http://127.0.0.1:5000/api/chamados \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## Usando migrações (quando alterar os models.py no futuro)

```bash
flask db init        # só na primeira vez
flask db migrate -m "descrição da mudança"
flask db upgrade
```

## Indo pra produção (pro dia da defesa)

Serviços com plano gratuito que aceitam Flask direto (sem precisar deixar seu computador ligado):
- **Render** (mais simples de configurar)
- **Railway**
- **PythonAnywhere** (tem plano free específico pra Flask/Django)

Em qualquer um deles: defina `DATABASE_URL` apontando pro PostgreSQL gerenciado que o próprio serviço oferece, e as duas chaves secretas (`SECRET_KEY`, `JWT_SECRET_KEY`) nas variáveis de ambiente do painel — nunca deixe essas chaves reais dentro do `.env` versionado no GitHub.

## Conectando com o front-end (HTML/JS que já está pronto)

O `Flask-Cors` já está habilitado, então o `public/diretor/*.html` pode chamar essa API mesmo rodando de outra origem (ex: abrir com Live Server em outra porta). Próximo passo: trocar os dados fixos do `script.js` por chamadas `fetch()` pra esses endpoints — posso te ajudar nisso na sequência.

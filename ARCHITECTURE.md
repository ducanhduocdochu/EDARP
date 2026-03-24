# Platform RAG — System Architecture

## 1. Tổng quan hệ thống

Platform RAG là hệ thống **Retrieval-Augmented Generation** đa tenant, cho phép nhiều tổ chức (tenant) tạo project, upload tài liệu, index vào vector database và truy vấn bằng ngôn ngữ tự nhiên thông qua LLM.

Hệ thống được thiết kế theo kiến trúc **microservices**, mỗi service chạy độc lập, giao tiếp qua REST API và chia sẻ JWT secret để xác thực.

```
┌──────────────────────────────────────────────────────────────────┐
│                        UI Service (3000)                         │
│                    React + Ant Design + Vite                     │
└──────┬──────────┬──────────────┬──────────────┬─────────────────┘
       │          │              │              │
       ▼          ▼              ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│   Auth   │ │ Project  │ │ Indexing │ │    Query     │
│  (5001)  │ │  (5002)  │ │  (5004)  │ │   (5005)     │
│  Flask   │ │  Flask   │ │ FastAPI  │ │  FastAPI     │
└────┬─────┘ └──┬───┬───┘ └──┬──┬───┘ └──┬──┬───┬───┘
     │          │   │        │  │        │  │   │
     ▼          ▼   │        │  │        │  │   ▼
┌─────────┐ ┌──────┐│        │  │        │  │ ┌─────────┐
│ auth_db │ │proj_ ││        │  │        │  │ │   LLM   │
│ Postgres│ │db    ││        │  │        │  │ │ (Ollama) │
│  (5433) │ │(5434)││        │  │        │  │ │ (11434) │
└─────────┘ └──────┘│        │  │        │  │ └─────────┘
                    ▼        ▼  │        ▼  │
              ┌──────────────────┐  ┌───────────┐
              │   Embedding      │  │ Weaviate  │
              │   Service (5003) │  │  (8080)   │
              │   FastAPI+HF     │  │ VectorDB  │
              └──────────────────┘  └───────────┘
```

---

## 2. Danh sách Services

| Service | Framework | Port | Chức năng chính |
|---------|-----------|------|-----------------|
| **Auth Service** | Flask | 5001 | Quản lý tenant, user, đăng nhập, JWT token |
| **Project Service** | Flask | 5002 | Quản lý project, API key, document metadata |
| **Embedding Service** | FastAPI | 5003 | Text embedding với HuggingFace models |
| **Indexing Service** | FastAPI | 5004 | Tokenize, vectorize, index vào Weaviate |
| **Query Service** | FastAPI | 5005 | RAG pipeline: retrieve + prompt + LLM |
| **UI Service** | React/Vite | 3000 | Giao diện web quản lý toàn bộ hệ thống |

### Infrastructure

| Component | Image | Port | Chức năng |
|-----------|-------|------|-----------|
| **auth_db** | postgres:16-alpine | 5433 | PostgreSQL cho Auth Service |
| **project_db** | postgres:16-alpine | 5434 | PostgreSQL cho Project Service |
| **Weaviate** | weaviate:1.28.4 | 8080 | Vector database cho indexing/search |
| **LLM** (external) | Ollama | 11434 | Large Language Model cho RAG generation |

---

## 3. Chi tiết từng Service

### 3.1 Auth Service (port 5001)

**Mô tả:** Quản lý multi-tenant authentication. Mỗi tenant có admin riêng, có thể tạo thêm member. Sử dụng JWT access token + refresh token.

**Tech:** Flask, SQLAlchemy, Flask-Migrate, PyJWT, Werkzeug

#### Database Tables

**tenants**

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| admin_email | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | DEFAULT now() |
| status | VARCHAR(50) | DEFAULT 'active' |

**users**

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PRIMARY KEY |
| tenant_id | UUID | FK → tenants.id |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | TEXT | NOT NULL |
| role | VARCHAR(20) | CHECK ('admin', 'member') |
| created_at | TIMESTAMP | DEFAULT now() |
| status | VARCHAR(50) | DEFAULT 'active' |

**refresh_tokens**

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FK → users.id |
| token_hash | TEXT | NOT NULL |
| expires_at | TIMESTAMP | NOT NULL |
| created_at | TIMESTAMP | DEFAULT now() |

#### Quan hệ

```
tenant 1 ──── N users
user   1 ──── N refresh_tokens
```

#### API Endpoints

| Method | Path | Auth | Mô tả |
|--------|------|------|-------|
| GET | `/health` | — | Health check |
| POST | `/auth/register` | — | Tạo tenant mới + admin user |
| POST | `/auth/login` | — | Đăng nhập, trả access + refresh token |
| POST | `/auth/refresh` | — | Đổi refresh token, trả token mới |
| GET | `/auth/me` | Bearer | Thông tin user hiện tại |
| POST | `/users` | Bearer (admin) | Tạo user trong tenant |
| GET | `/users` | Bearer | List users trong tenant |

#### Cấu trúc file

```
auth_service/
├── __init__.py
├── app.py                 # Flask factory, register blueprints
├── config.py              # DATABASE_URL, JWT_SECRET, token expiry
├── models.py              # Tenant, User, RefreshToken
├── utils.py               # JWT create/decode, login_required, admin_required
├── wsgi.py                # WSGI entry point
├── routes/
│   ├── __init__.py
│   ├── auth.py            # /auth/register, login, refresh, me
│   └── users.py           # /users CRUD
├── requirements.txt
├── Dockerfile
├── .env
└── .env.sample
```

---

### 3.2 Project Service (port 5002)

**Mô tả:** Quản lý project, API key và document metadata. Mỗi project có cấu hình embedding model và LLM model riêng. Gọi Embedding Service khi cần embed text.

**Tech:** Flask, SQLAlchemy, Flask-Migrate, PyJWT, Requests

#### Database Tables

**projects**

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PRIMARY KEY |
| tenant_id | UUID | NOT NULL, INDEX |
| name | VARCHAR(255) | NOT NULL |
| embedding_model | VARCHAR(100) | NOT NULL, DEFAULT 'vietnamese-embedding' |
| llm_model | VARCHAR(100) | NOT NULL, DEFAULT 'gpt-4o-mini' |
| created_by | UUID | NOT NULL |
| created_at | TIMESTAMP | DEFAULT now() |
| status | VARCHAR(50) | DEFAULT 'active' |

**api_keys**

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PRIMARY KEY |
| project_id | UUID | FK → projects.id |
| key_hash | TEXT | NOT NULL |
| created_at | TIMESTAMP | DEFAULT now() |
| status | VARCHAR(50) | DEFAULT 'active' |

**documents**

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PRIMARY KEY |
| project_id | UUID | FK → projects.id |
| file_name | VARCHAR(255) | NOT NULL |
| s3_path | TEXT | NULLABLE |
| status | VARCHAR(50) | CHECK ('uploaded','processing','indexed','failed') |
| created_at | TIMESTAMP | DEFAULT now() |

#### Quan hệ

```
tenant  1 ──── N projects
project 1 ──── N api_keys
project 1 ──── N documents
```

#### Embedding Model Registry

| Key | Mô tả |
|-----|-------|
| vietnamese-embedding | dangvantuan/vietnamese-embedding |
| bge-large-en-v1.5 | BAAI/bge-large-en-v1.5 |
| bge-base-en-v1.5 | BAAI/bge-base-en-v1.5 |
| bge-small-en-v1.5 | BAAI/bge-small-en-v1.5 |
| multilingual-e5-large | intfloat/multilingual-e5-large |
| multilingual-e5-base | intfloat/multilingual-e5-base |

#### LLM Model Registry

gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo, claude-3.5-sonnet, claude-3-haiku, gemini-1.5-pro, gemini-1.5-flash

#### API Endpoints

| Method | Path | Auth | Mô tả |
|--------|------|------|-------|
| GET | `/health` | — | Health check |
| GET | `/projects/models` | Bearer | Danh sách embedding + LLM models |
| POST | `/projects` | Bearer | Tạo project (chọn embedding + LLM model) |
| GET | `/projects` | Bearer | List projects của tenant |
| GET | `/projects/{id}` | Bearer | Chi tiết project |
| PUT | `/projects/{id}` | Bearer | Sửa project (name, models) |
| POST | `/projects/{id}/api-keys` | Bearer | Tạo API key |
| GET | `/projects/{id}/api-keys` | Bearer | List API keys |
| POST | `/projects/{id}/documents` | Bearer | Tạo document metadata |
| GET | `/projects/{id}/documents` | Bearer | List documents |
| DELETE | `/documents/{id}` | Bearer | Xóa document |
| POST | `/projects/{id}/documents/embed` | Bearer | Embed 1 text |
| POST | `/projects/{id}/documents/embed-batch` | Bearer | Embed batch texts |

#### Kết nối

- **PostgreSQL** (`project_db`)
- **Embedding Service** (`EMBEDDING_SERVICE_URL`) — gọi `/vectorize`, `/vectorize/batch`, `/models`

#### Cấu trúc file

```
project_service/
├── __init__.py
├── app.py                    # Flask factory
├── config.py                 # DB, JWT, EMBEDDING_SERVICE_URL
├── models.py                 # Project, ApiKey, Document + model lists
├── utils.py                  # JWT validation, key hashing
├── embedding_client.py       # HTTP client → Embedding Service
├── wsgi.py
├── routes/
│   ├── __init__.py
│   ├── projects.py           # CRUD projects + /models
│   ├── api_keys.py           # API key management
│   └── documents.py          # Documents + embed endpoints
├── requirements.txt
├── Dockerfile
├── .env
└── .env.sample
```

---

### 3.3 Embedding Service (port 5003)

**Mô tả:** Service stateless chuyên embed text thành vector. Hỗ trợ nhiều HuggingFace models, lazy-load và cache trong memory. Không cần authentication.

**Tech:** FastAPI, PyTorch, Transformers, SentencePiece

#### Model Registry

| Key (alias) | HuggingFace Model ID |
|-------------|---------------------|
| vietnamese-embedding (default) | dangvantuan/vietnamese-embedding |
| bge-large-en-v1.5 | BAAI/bge-large-en-v1.5 |
| bge-base-en-v1.5 | BAAI/bge-base-en-v1.5 |
| bge-small-en-v1.5 | BAAI/bge-small-en-v1.5 |
| multilingual-e5-large | intfloat/multilingual-e5-large |
| multilingual-e5-base | intfloat/multilingual-e5-base |

Models được **lazy-load** khi có request đầu tiên sử dụng model đó, sau đó cache trong memory.

#### API Endpoints

| Method | Path | Auth | Mô tả |
|--------|------|------|-------|
| GET | `/health` | — | Status + danh sách models đã load |
| GET | `/models` | — | Registry, default, loaded models |
| POST | `/vectorize` | — | Embed 1 text → vector |
| POST | `/vectorize/batch` | — | Embed nhiều texts → vectors |

#### Request/Response

```json
// POST /vectorize
{ "text": "Xin chào", "model": "vietnamese-embedding" }

// Response
{ "vector": [0.01, -0.03, ...], "model": "vietnamese-embedding", "dimension": 768 }
```

#### Cấu trúc file

```
embedding_service/
├── __init__.py
├── app.py                 # FastAPI app + lifespan (preload default model)
├── config.py              # MODEL_REGISTRY, DEFAULT_MODEL, DEVICE, PORT
├── model_manager.py       # ModelManager: lazy-load, cache, encode/encode_batch
├── schemas.py             # Pydantic: TextRequest, BatchTextRequest, responses
├── main.py                # uvicorn entry
├── requirements.txt
├── Dockerfile
├── .env
└── .env.sample
```

---

### 3.4 Indexing Service (port 5004)

**Mô tả:** Pipeline xử lý tài liệu: nhận JSON/text → tokenize tiếng Việt (pyvi) → vectorize qua Embedding Service → import vào Weaviate. Mỗi project có Weaviate collection riêng (`Project_{id}`).

**Tech:** FastAPI, Weaviate Client, pyvi, Requests, PyJWT

#### Weaviate Schema (per project)

Mỗi project tạo 1 Weaviate class riêng: `Project_{sanitized_project_id}`

| Property | Data Type | Mô tả |
|----------|-----------|-------|
| content | text | Nội dung document |
| title | text | Tiêu đề |
| doc_metadata | text | Metadata dạng string |
| (vector) | float[] | Supplied externally (vectorizer: none) |

#### API Endpoints

| Method | Path | Auth | Mô tả |
|--------|------|------|-------|
| GET | `/healthz` | — | Health check |
| GET | `/readyz` | — | Check Weaviate + Embedding reachable |
| POST | `/index/{project_id}/text` | Bearer | Index 1 đoạn text |
| POST | `/index/{project_id}/json` | Bearer | Upload JSON file → tokenize → vectorize → import |
| POST | `/index/{project_id}/batch` | Bearer | Index batch documents (JSON body) |
| POST | `/index/{project_id}/search` | Bearer | Vector similarity search (không qua LLM) |
| GET | `/index/{project_id}/status` | Bearer | Số documents đã index |
| DELETE | `/index/{project_id}` | Bearer | Xóa toàn bộ index của project |

#### Pipeline Flow (JSON file)

```
Upload JSON file
  → Parse JSON array [{title, context, ...}]
  → Tokenize tiếng Việt (pyvi ViTokenizer)
  → Vectorize batch qua Embedding Service (model theo project config)
  → Import documents + vectors vào Weaviate collection
```

#### Kết nối

- **Weaviate** (`WEAVIATE_URL`) — vector storage
- **Embedding Service** (`VECTORIZE_URL`) — vectorize text
- **Project Service** (`PROJECT_SERVICE_URL`) — lấy `embedding_model` của project

#### Cấu trúc file

```
indexing_service/
├── __init__.py
├── app.py                    # FastAPI routes
├── config.py                 # Weaviate, Vectorize, Project URLs, JWT
├── auth.py                   # JWT Bearer validation
├── schemas.py                # IndexTextRequest, SearchRequest, responses
├── pipeline.py               # get_project_info, vectorize, tokenize_vi
├── weaviate_manager.py       # Weaviate CRUD: ensure/delete collection, import, search, count
├── main.py                   # uvicorn entry
├── requirements.txt
├── Dockerfile
├── .env
└── .env.sample
```

---

### 3.5 Query Service (port 5005)

**Mô tả:** RAG query pipeline hoàn chỉnh: nhận câu hỏi → tokenize → vectorize → search Weaviate → build prompt với context → gọi LLM → trả answer + sources.

**Tech:** FastAPI, Weaviate Client, pyvi, Requests, PyJWT

#### RAG Pipeline Flow

```
User question
  │
  ▼
① Lấy project config (embedding_model, llm_model) từ Project Service
  │
  ▼
② Tokenize tiếng Việt (pyvi)
  │
  ▼
③ Vectorize query qua Embedding Service
  │
  ▼
④ Near-vector search trong Weaviate (top_k results)
  │
  ▼
⑤ Build prompt:
   "Context information:
    [retrieved documents]
    Question: {user query}"
  │
  ▼
⑥ Gọi LLM API (Ollama/OpenAI compatible)
  │
  ▼
⑦ Return answer + context sources + model info
```

#### Prompt Template

```
We have provided context information below.
---------------------
[title] (score: 0.95)
Content of document...

[title] (score: 0.89)
Content of document...
---------------------
Given this information, please answer the question: {user query}
```

#### API Endpoints

| Method | Path | Auth | Mô tả |
|--------|------|------|-------|
| GET | `/healthz` | — | Health check |
| GET | `/readyz` | — | Check Weaviate + Embedding (LLM optional) |
| POST | `/query/{project_id}` | Bearer | Full RAG query |

#### Request/Response

```json
// POST /query/{project_id}
{
  "query": "Kiến trúc microservice là gì?",
  "top_k": 3,
  "max_new_tokens": 512,
  "temperature": 0.7
}

// Response
{
  "answer": "Kiến trúc microservice là một phương pháp...",
  "query": "Kiến trúc microservice là gì?",
  "context": [
    {
      "content": "Trích dẫn ở: Chương 1...",
      "title": "Chương 1",
      "score": 0.9512
    }
  ],
  "llm_model": "gpt-4o-mini",
  "embedding_model": "vietnamese-embedding"
}
```

#### LLM Integration

- Mặc định gọi **Ollama API** (`/api/generate`) chạy local
- Hỗ trợ cả Ollama-compatible và OpenAI-compatible response format
- Graceful fallback nếu LLM không reachable
- Configurable qua `LLM_API_URL`

#### Kết nối

- **Weaviate** (`WEAVIATE_URL`) — vector search
- **Embedding Service** (`VECTORIZE_URL`) — vectorize query
- **Project Service** (`PROJECT_SERVICE_URL`) — lấy project config
- **LLM API** (`LLM_API_URL`) — generate answer

#### Cấu trúc file

```
query_service/
├── __init__.py
├── app.py                    # FastAPI routes
├── config.py                 # All URLs, JWT, LLM defaults
├── auth.py                   # JWT + token forwarding
├── schemas.py                # QueryRequest, QueryResponse, ContextChunk
├── rag_pipeline.py           # Full RAG: tokenize → vectorize → search → prompt → LLM
├── weaviate_client.py        # Weaviate near-vector search
├── main.py                   # uvicorn entry
├── requirements.txt
├── Dockerfile
├── .env
└── .env.sample
```

---

### 3.6 UI Service (port 3000)

**Mô tả:** Single Page Application cung cấp giao diện quản lý toàn bộ hệ thống. Giao tiếp với backend services thông qua Vite dev proxy.

**Tech:** React 19, Ant Design 5, React Router 7, Axios, Vite

#### Pages & Chức năng

| Route | Page | Chức năng |
|-------|------|-----------|
| `/login` | Login | Đăng nhập, auto refresh token |
| `/register` | Register | Đăng ký tenant + admin user |
| `/` | Dashboard | Danh sách projects, tạo project (chọn models) |
| `/projects/:id` | ProjectDetail | Chi tiết project với 6 tabs |
| `/users` | Users | Quản lý users, admin tạo user mới |

#### ProjectDetail Tabs

| Tab | Chức năng |
|-----|-----------|
| **RAG Chat** | Chat interface — hỏi đáp trên documents đã index, hiện sources |
| **API Keys** | Tạo và xem API keys |
| **Documents** | CRUD document metadata |
| **Indexing** | Upload JSON, index text, xem status, clear index |
| **Search** | Semantic search trên Weaviate (không qua LLM) |
| **Embedding Playground** | Test embed text, xem vector + dimension |

#### Vite Proxy Configuration

| Frontend Path | Backend Target | Rewrite |
|---------------|----------------|---------|
| `/api/auth/*` | `localhost:5001` | → `/auth/*` |
| `/api/users/*` | `localhost:5001` | → `/users/*` |
| `/api/projects/*` | `localhost:5002` | → `/projects/*` |
| `/api/documents/*` | `localhost:5002` | → `/documents/*` |
| `/api/index/*` | `localhost:5004` | → `/index/*` |
| `/api/query/*` | `localhost:5005` | → `/query/*` |

#### Cấu trúc file

```
ui_service/
├── index.html
├── package.json
├── vite.config.js              # Port 3000, proxy rules
├── Dockerfile
├── .env
├── .env.sample
└── src/
    ├── main.jsx                # React bootstrap
    ├── App.jsx                 # Routes + Ant Design theme (primary: #6366f1)
    ├── contexts/
    │   └── AuthContext.jsx      # Auth state, token management
    ├── components/
    │   └── PrivateRoute.jsx     # Route guard
    ├── layouts/
    │   └── MainLayout.jsx       # Sidebar + Header + Content
    ├── api/
    │   ├── axios.js             # Axios instance, Bearer token, auto refresh
    │   ├── auth.js              # register, login, getMe, getUsers, createUser
    │   ├── project.js           # CRUD projects, api-keys, documents, embed
    │   ├── indexing.js          # index JSON/text, search, status, clear
    │   └── query.js             # RAG query
    └── pages/
        ├── Login.jsx
        ├── Register.jsx
        ├── Dashboard.jsx        # Projects list + create (with model selection)
        ├── ProjectDetail.jsx    # 6 tabs: Chat, Keys, Docs, Indexing, Search, Embed
        └── Users.jsx            # User management
```

---

## 4. Luồng dữ liệu chính

### 4.1 Authentication Flow

```
Client → POST /auth/register → Tạo Tenant + Admin User
Client → POST /auth/login    → Nhận access_token + refresh_token
Client → GET /auth/me        → (Bearer token) → User info
Client → POST /auth/refresh  → (refresh_token) → New access + refresh token
```

### 4.2 Project Setup Flow

```
Client → POST /projects (name, embedding_model, llm_model)
       → Project created in project_db
       → POST /projects/{id}/api-keys → Generate API key
```

### 4.3 Document Indexing Flow

```
Client → POST /index/{project_id}/json (upload file)
       │
       ├─→ Indexing Service: Parse JSON
       ├─→ Indexing Service: Tokenize (pyvi Vietnamese)
       ├─→ Indexing Service → Embedding Service: Vectorize batch
       ├─→ Indexing Service → Weaviate: Import documents + vectors
       │
       └─→ Response: { imported: N, model: "..." }
```

### 4.4 RAG Query Flow

```
Client → POST /query/{project_id} { query: "..." }
       │
       ├─→ Query Service → Project Service: Get project config
       ├─→ Query Service: Tokenize query (pyvi)
       ├─→ Query Service → Embedding Service: Vectorize query
       ├─→ Query Service → Weaviate: Near-vector search (top_k)
       ├─→ Query Service: Build prompt (context + question)
       ├─→ Query Service → LLM API: Generate answer
       │
       └─→ Response: { answer, context[], llm_model, embedding_model }
```

---

## 5. Authentication & Security

### JWT Token Flow

- **Auth Service** tạo JWT access token (15 min) + refresh token (7 ngày)
- Tất cả services share cùng **`JWT_SECRET`**
- **Project, Indexing, Query Services** decode JWT để xác thực user + tenant
- Refresh token được hash (SHA-256) trước khi lưu DB

### Token Payload

```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "role": "admin|member",
  "exp": 1234567890,
  "type": "access"
}
```

### Multi-tenancy

- Mọi query đều scoped theo `tenant_id` từ JWT
- Projects, users, documents chỉ visible trong cùng tenant
- Weaviate collections isolated theo `project_id`

---

## 6. Quan hệ toàn hệ thống

```
tenant
   │
   ├── users (admin, member)
   │
   └── projects
          │
          ├── embedding_model  ──→  Embedding Service
          ├── llm_model        ──→  LLM API
          │
          ├── api_keys
          │
          ├── documents (metadata in PostgreSQL)
          │
          └── Weaviate Collection: Project_{id}
                 │
                 ├── content (text)
                 ├── title (text)
                 ├── doc_metadata (text)
                 └── vector (float[])
```

---

## 7. Deployment

### Docker Compose

```bash
cd services
docker-compose up --build
```

### Database Migration

```bash
# Auth Service
docker-compose exec auth_service flask --app app:create_app db init
docker-compose exec auth_service flask --app app:create_app db migrate -m "init"
docker-compose exec auth_service flask --app app:create_app db upgrade

# Project Service
docker-compose exec project_service flask --app app:create_app db init
docker-compose exec project_service flask --app app:create_app db migrate -m "init"
docker-compose exec project_service flask --app app:create_app db upgrade
```

### Environment Setup

```bash
# Copy .env.sample → .env cho mỗi service
cp services/auth_service/.env.sample services/auth_service/.env
cp services/project_service/.env.sample services/project_service/.env
cp services/embedding_service/.env.sample services/embedding_service/.env
cp services/indexing_service/.env.sample services/indexing_service/.env
cp services/query_service/.env.sample services/query_service/.env
cp services/ui_service/.env.sample services/ui_service/.env
```

### Port Map

| Port | Service |
|------|---------|
| 3000 | UI Service (React) |
| 5001 | Auth Service (Flask) |
| 5002 | Project Service (Flask) |
| 5003 | Embedding Service (FastAPI) |
| 5004 | Indexing Service (FastAPI) |
| 5005 | Query Service (FastAPI) |
| 5433 | PostgreSQL (auth_db) |
| 5434 | PostgreSQL (project_db) |
| 8080 | Weaviate |
| 11434 | LLM / Ollama (external) |

---

## 8. Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, Ant Design 5, Vite, Axios |
| **Backend (Auth, Project)** | Python, Flask, SQLAlchemy, Flask-Migrate |
| **Backend (Embedding, Indexing, Query)** | Python, FastAPI, Uvicorn |
| **Database** | PostgreSQL 16 |
| **Vector Database** | Weaviate 1.28.4 |
| **Embedding Models** | HuggingFace Transformers, PyTorch |
| **NLP** | pyvi (Vietnamese tokenization) |
| **Authentication** | JWT (PyJWT) |
| **LLM** | Ollama (local) / OpenAI-compatible API |
| **Container** | Docker, Docker Compose |

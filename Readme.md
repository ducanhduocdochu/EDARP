# 📚 RAG Platform on AWS (EKS-based Microservices Architecture)

<img width="1611" height="1072" alt="image" src="https://github.com/user-attachments/assets/909110a8-37ce-4714-ac3f-3c5ba062cfd4" />

## 1. Introduction

This project implements a **production-grade Retrieval-Augmented Generation (RAG) platform** on AWS using a **microservices architecture deployed on Amazon EKS**.

The system enables:
- Document ingestion and indexing
- Semantic search using vector embeddings
- AI-powered question answering via LLMs

It is designed for **scalability, security, and extensibility**, following cloud-native and GitOps principles.

---

## 2. High-Level Architecture

The platform is composed of the following layers:

- **Networking Layer** (VPC, Subnets, NAT, Endpoints)
- **Ingress Layer** (ALB)
- **Compute Layer** (Amazon EKS - Microservices)
- **Data Layer** (RDS, Vector DB)
- **Event-driven Ingestion Pipeline** (S3, Lambda, SQS)
- **AI/LLM Layer**
- **CI/CD Pipeline** (GitHub Actions, Harbor, ArgoCD)

---

## 3. Networking & Security

### VPC Design

| Component        | Description |
|-----------------|------------|
| VPC             | Isolated AWS network |
| Public Subnet   | Hosts ALB |
| Private Subnet  | Hosts EKS, RDS, Vector DB |
| NAT Gateway     | Enables outbound internet access for private workloads |
| VPC Endpoint    | Private access to S3 |

### Security Principles

- No direct public access to backend services
- Application and data layers are deployed in **private subnets**
- ALB is the **only public entry point**
- Secure outbound traffic via NAT Gateway
- Optional integration:
  - IAM Roles for Service Accounts (IRSA)
  - AWS Secrets Manager / HashiCorp Vault

---

## 4. Compute Layer (Amazon EKS)

All services are containerized and deployed as Kubernetes workloads.

### Core Services

#### 4.1 Indexing Service
Responsible for document ingestion pipeline:
- Chunking
- Preprocessing
- Embedding generation
- Indexing into vector database

#### 4.2 Embedding Service
- Converts text into vector embeddings
- Shared by indexing and query flows

#### 4.3 Query Service
Handles user queries:
- Generate query embeddings
- Retrieve relevant documents (top-k)
- Invoke LLM for answer generation

---

### Application Services

| Service           | Responsibility |
|------------------|---------------|
| Platform Service | Core business logic |
| UI Service       | API / frontend gateway |
| Auth Service     | Authentication & authorization |

---

## 5. Data Layer

### Amazon RDS
- Stores relational data:
  - Users
  - Metadata
  - Application state

### Vector Database (Weaviate)
- Stores embeddings
- Supports semantic similarity search

---

## 6. Data Ingestion Pipeline

The ingestion pipeline follows an **event-driven architecture**:


S3 → Lambda → SQS → Indexing Service


### Flow Description

1. User uploads file to **Amazon S3**
2. S3 triggers **Lambda function**
3. Lambda pushes message to **Amazon SQS**
4. Indexing Service consumes messages from SQS
5. Data is processed and stored in Vector DB

### Benefits

- Asynchronous processing
- High scalability
- Fault tolerance with retry mechanism

---

## 7. Query Flow


User → ALB → Query Service → Embedding → Vector DB → LLM → Response


### Steps

1. User sends query via UI
2. Request routed through **ALB → EKS**
3. Query Service:
   - Generates embedding
   - Retrieves top-k relevant chunks
4. Context sent to LLM
5. LLM generates final answer
6. Response returned to user

---

## 8. AI / LLM Integration

- External LLM is used for answer generation
- Supports:
  - Context-aware responses
  - Natural language reasoning

The system separates:
- Retrieval (Vector DB)
- Reasoning (LLM)

---

## 9. CI/CD Pipeline (GitOps)

### Workflow


Developer → GitHub → GitHub Actions → Harbor → ArgoCD → EKS


### Components

| Tool             | Purpose |
|------------------|--------|
| GitHub           | Source control |
| GitHub Actions   | CI pipeline (build & push image) |
| Harbor           | Container registry |
| ArgoCD           | GitOps deployment |
| Helm             | Kubernetes packaging |

### Deployment Strategy

- Declarative deployment via Git
- Automatic sync with ArgoCD
- Rolling updates supported

---

## 10. Key Design Decisions

### Microservices Architecture
- Independent scaling
- Service isolation

### Event-Driven Ingestion
- Decoupled pipeline
- Reliable processing via SQS

### Private Networking
- Improved security posture
- No public exposure of internal services

### Vector Search + LLM
- Accurate retrieval
- Context-aware responses

---

## 11. Scalability & Reliability

- Horizontal scaling via Kubernetes
- Message queue buffering (SQS)
- Stateless services
- Fault isolation between services

---

## 12. Observability (Recommended)

To enhance production readiness, integrate:

- Prometheus (metrics)
- Grafana (dashboard)
- Loki (logging)

---

## 13. Future Enhancements

- Redis caching layer
- API Gateway + WAF
- Multi-region deployment
- Streaming ingestion pipeline
- Fine-tuned LLM integration

---

## 14. Conclusion

This architecture provides a **robust, scalable, and secure foundation** for building enterprise-grade RAG systems.

It aligns with modern best practices:
- Cloud-native design
- Microservices architecture
- Event-driven processing
- GitOps deployment

# ADR-0001: Use PostgreSQL and pgvector as the primary data store

- Status: Accepted
- Date: 2026-08-25
- Decision owners: Project maintainer
- Related modules: Modules 2, 5, 6, 8, and 10

## Context

The system must store application records, document metadata, versioned chunks,
embeddings, evaluation records, and approved analytics data. It must support
transactional operations, metadata filtering, lexical retrieval, vector retrieval,
read-only Text-to-SQL, and reproducible local development.

## Requirements

- Relational storage for application and analytics records.
- Vector storage and similarity search.
- PostgreSQL full-text search.
- Transactions, constraints, indexes, and migrations.
- Read-only roles and column-level permissions.
- Local execution through Docker Compose.
- A practical mapping to managed cloud PostgreSQL.
- Minimal infrastructure for a portfolio-scale corpus.

## Options considered

### PostgreSQL with pgvector

Provides relational storage, full-text search, vector search, transactions, mature
permissions, and SQL analytics in one system.

Trade-offs include less specialized vector-search scaling than dedicated distributed
vector databases and the need to tune PostgreSQL as the corpus grows.

### Dedicated vector database with separate PostgreSQL

Products such as Qdrant, Pinecone, Milvus, or Weaviate provide specialized vector
retrieval features and independent vector scaling.

This option adds another service, synchronization requirements, additional failure
modes, and more operational work.

### FAISS with separate metadata storage

FAISS provides efficient in-process vector search and is useful for experimentation.

It does not provide application persistence, SQL analytics, database permissions,
transactions, or straightforward multi-process durability by itself.

### OpenSearch or Elasticsearch

These systems provide strong lexical and hybrid-search capabilities at scale.

They require additional operational resources and would overlap with the separate
Search and Ranking portfolio project.

## Decision

Use PostgreSQL as the primary relational, analytics, metadata, lexical-search, and
vector store. Use pgvector for exact and HNSW vector retrieval.

Begin with exact vector search and PostgreSQL full-text search. Add HNSW only after
the baseline works and can be evaluated.

## Rationale

PostgreSQL satisfies the milestone requirements while keeping the local architecture
small enough to understand and operate. It allows retrieval filters, application
records, analytics data, and security permissions to share one transactional system.

Using one primary database reduces synchronization problems while preserving the
ability to move vector or search workloads to specialized systems if measured
requirements justify it.

## Consequences

### Positive

- One primary storage system for the portfolio milestone.
- Transactional consistency between documents, chunks, and processing records.
- SQLAlchemy and Alembic support.
- Native PostgreSQL full-text search.
- Exact and approximate vector search through pgvector.
- Database-enforced read-only analytics permissions.
- Straightforward local Docker and Amazon RDS mapping.

### Negative

- PostgreSQL is not an unlimited-scale distributed vector-search platform.
- Vector indexes consume database memory and storage.
- Heavy retrieval workloads can compete with transactional and analytics queries.
- Specialized search features may require additional implementation.

### Neutral

- Embedding dimension and HNSW parameters remain undecided until retrieval
  experiments are performed.
- A future architecture may separate operational, analytics, and retrieval workloads.

## Security and privacy considerations

- Text-to-SQL uses a restricted analytics role.
- The role receives no write permissions.
- Sensitive employee columns are excluded through column-level grants.
- Future SQL validation will enforce approved schemas, tables, and columns.
- All current records are synthetic.
- Secrets remain outside Git.

## Evaluation and validation

The decision will be evaluated using:

- Exact retrieval quality and latency.
- HNSW recall and latency.
- Lexical, dense, hybrid, and reranked retrieval metrics.
- Database P50 and P95 latency.
- Index size and build time.
- Connection-pool behavior.
- Permission and migration tests.

## Reconsider when

Reconsider this decision if measured evidence shows:

- Retrieval traffic materially harms transactional workloads.
- Required corpus size exceeds practical PostgreSQL index capacity.
- Search functionality requires features PostgreSQL cannot provide adequately.
- Independent vector scaling becomes operationally necessary.
- Multi-region or high-availability requirements exceed the chosen deployment design.

## Cloud mapping

The local pgvector-enabled PostgreSQL container maps to Amazon RDS for PostgreSQL with
pgvector in a production AWS design. Docker volumes map conceptually to managed
database storage and backups, while credentials map to AWS Secrets Manager.
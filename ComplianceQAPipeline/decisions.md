# Architecture Decision Record — Audit Agent

## 1. Why LangGraph over a simple chain?

A linear LangChain chain cannot handle the stateful, multi-step nature of this pipeline. The indexer and auditor nodes need to share a typed state object (`VideoAuditState`) where fields like `compliance_results` and `errors` accumulate across nodes using `operator.add`. LangGraph's `StateGraph` provides exactly this — explicit state management, node isolation, and a compiled DAG that is inspectable via LangSmith traces.

## 2. Why Azure Video Indexer over Whisper?

Azure Video Indexer extracts both speech-to-text (transcript) and OCR (on-screen text) in a single API call. A self-hosted Whisper setup only handles audio — it cannot detect on-screen text like product claims, pricing overlays, or disclosure banners. Since brand compliance auditing requires both channels, Video Indexer was the correct choice despite the higher operational complexity.

## 3. Why Azure AI Search over FAISS or Chroma?

FAISS and Chroma are in-memory vector stores — they require the index to be rebuilt on every cold start and cannot persist across deployments without additional infrastructure. Azure AI Search is a managed, persistent vector store with hybrid search (vector + keyword) built in. For a production compliance system where the knowledge base is static (PDF rulebooks), a managed store with no cold-start penalty is the correct trade-off.

## 4. Why RAG over fine-tuning?

The compliance rules (FTC guidelines, YouTube ad specs) change periodically. A fine-tuned model encodes rules into weights — updating it requires retraining. A RAG pipeline decouples the knowledge base from the model: updating rules means re-running `index_documents.py`, not retraining. This is the correct architecture for any domain where the knowledge base is mutable.

## 5. Why DefaultAzureCredential over API key auth for Video Indexer?

The Azure Video Indexer API requires an ARM-scoped access token, not a simple API key. `DefaultAzureCredential` provides a credential chain that works across local development (Azure CLI), CI/CD (environment variables), and production (Managed Identity) without code changes. Hardcoding an API key would require different auth logic per environment.

## 6. Why chunk size 1000 with overlap 200?

The compliance PDFs contain dense regulatory text. A chunk size of 1000 characters captures enough context for a rule to be semantically complete (typically one regulatory clause). The 200-character overlap prevents a rule from being split across two chunks and losing context at the boundary. This is a standard starting point — further tuning would require evaluating retrieval precision against a labelled test set.

## 7. Why FastAPI over Flask?

FastAPI provides automatic request/response validation via Pydantic models, auto-generated Swagger UI, and async support out of the box. The `AuditRequest` and `AuditResponse` models catch schema mismatches at the API boundary before they propagate into the pipeline. Flask requires manual validation and has no built-in OpenAPI generation.

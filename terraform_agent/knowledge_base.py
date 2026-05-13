import logging
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

from .config import Config
from .model_router import ModelRouter

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Manages a ChromaDB vector store for semantic search of Terraform best practices.

    Loads documentation files from disk, chunks them into smaller pieces,
    embeds them using an embedding model, and stores them in ChromaDB
    for efficient semantic similarity search.

    Attributes:
        config: Configuration object with paths and model names
        vectorstore: ChromaDB vector store instance for similarity search
    """

    VECTORSTORE_DIR : str = ".vectorstore"

    config: Config
    vectorstore: Chroma | None
    model_router: ModelRouter | None

    def __init__(self, config: Config, model_router: ModelRouter | None = None) -> None:
        """Initialize the knowledge base and load documents.

        Loads all markdown files from the docs directory, splits them into
        chunks, creates embeddings, and indexes them in ChromaDB. If the
        vectorstore already exists, reuses it.

        Args:
            config: Configuration object containing paths and model names
        """
        self.config = config
        self.model_router = model_router
        self.vectorstore = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize and populate the ChromaDB vectorstore.

        Performs the following steps:
        1. Loads all markdown files from the docs directory
        2. Splits documents into overlapping chunks (1000 chars with 100 char overlap)
        3. Creates embeddings using OllamaEmbeddings
        4. Creates or reuses a ChromaDB collection
        5. Clears existing documents and indexes new ones
        """
        print("📚 Loading knowledge base...")

        # Load documents from docs directory
        loader = DirectoryLoader(
            str(self.config.RULES_DIR),
            glob="**/*.md",
            loader_cls=TextLoader,
            recursive=True,
        )
        documents = loader.load()
        print(f"  ✓ Loaded {len(documents)} document(s) from {self.config.RULES_DIR}")

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )
        docs = text_splitter.split_documents(documents)
        print(f"  ✓ Split into {len(docs)} chunks")

        # Initialize embedding function
        embedding_function = OllamaEmbeddings(model=self.config.EMBEDDING_MODEL)

        vectorstore_path = self.config.PROJECT_ROOT / self.VECTORSTORE_DIR

        print(f"  Creating new vectorstore database...")
        self.vectorstore = Chroma(
            collection_name="terraform_docs",
            embedding_function=embedding_function,
            persist_directory=str(vectorstore_path),
        )

        # Clear existing documents and index new ones
        try:
            existing_ids = self.vectorstore.get()["ids"]
            if existing_ids:
                print(f"  🗑️ Clearing {len(existing_ids)} existing documents...")
                logger.info(f"Clearing {len(existing_ids)} existing documents from vectorstore")
                self.vectorstore.delete(ids=existing_ids)
        except (KeyError, ValueError) as e:
            logger.debug(f"No existing documents to clear (collection empty or new): {e}")
            print(f"  ℹ️  Starting with empty vectorstore")

        print(f"  Indexing {len(docs)} documents...")
        self.vectorstore.add_documents(docs)
        print(f"  ✓ Vectorstore created and indexed")

    def search(self, query: str, k: int = 5, summarize: bool = True) -> str:
        """Search the knowledge base for relevant documents using semantic similarity.

        Performs a similarity search in the ChromaDB vectorstore and returns
        the top k most relevant document chunks matching the query.

        Args:
            query: Search query string (e.g., "Terraform best practices security")
            k: Number of top results to return (default: 3)
            summarize: If True and model_router available, summarize results with LLM

        Returns:
            Concatenated content of the top k matching documents, separated by '---'
            If summarize=True, returns condensed summary instead of raw chunks
        """
        if self.vectorstore is None:
            raise RuntimeError("Vectorstore not initialized")

        logger.info(f"Searching vectorstore for: '{query}' (k={k})")
        results = self.vectorstore.similarity_search(query, k=k)
        raw_content = "\n---\n".join([res.page_content for res in results])
        preview = raw_content[:50].replace('\n', ' ') if raw_content else '(empty)'
        logger.info(f"Found {len(results)} results ({len(raw_content)} chars) - preview: {preview}...")

        # If summarization disabled or no model router, return raw content
        if not summarize or self.model_router is None:
            return raw_content

        # Summarize with LLM (Ollama or Claude depending on config)
        try:
            logger.info(f"Summarizing {len(results)} knowledge base results for query: {query}")

            prompt = f"""Summarize the query: "{query}"

# Rule Summary Prompt

You are a senior Cloud Security and Infrastructure analyst.

Your task is to summarize the following rule definition while preserving all critical technical, security, operational, and implementation information.

## Objectives
- Keep the summary concise but information-dense.
- Preserve:
  - security intent,
  - technical risks,
  - remediation guidance,
  - infrastructure patterns,
  - implementation constraints,
  - operational recommendations.
- Retain important:
  - configuration values,
  - code semantics,
  - cloud provider terminology,
  - security principles,
  - compliance implications.
- Do not remove meaningful distinctions between:
  - correct patterns,
  - anti-patterns,
  - exceptions,
  - recommended use cases.
- Do not invent information not present in the rule.

## Required Output Format

Produce the summary using the following structure:

# [RULE TITLE]

## Purpose
Short explanation of what the rule enforces.

## Risk
Key security or operational risks caused by non-compliance.

## Correct Configuration
Summarize approved/recommended configurations and when to use them.

## Incorrect Configuration
Summarize dangerous or non-compliant configurations.

## Key Security Principles
List the important security concepts behind the rule.

## Recommended Usage
Explain when each configuration option should be used.

## Implementation Checklist
Condense the checklist into actionable bullet points.

## Important Notes
Include:
- exceptions,
- edge cases,
- compliance considerations,
- operational caveats.

## Related Rules
List related controls/rules if present.

## References
Keep official documentation links.

## Compression Rules
- Target ~25–40% of original length.
- Preserve technical precision over readability simplification.
- Keep cloud-specific configuration values exactly as written.
- Keep important examples concise rather than removing them entirely.

---

# Rule Definition

{raw_content}

Summary:"""

            summary = self.model_router.invoke("summarization", prompt)
            summary_preview = summary[:50].replace('\n', ' ') if summary else '(empty)'
            logger.info(f"Summarization completed: {len(raw_content)} → {len(summary)} chars - preview: {summary_preview}...")
            return summary

        except Exception as e:
            logger.warning(f"Summarization failed: {e}, returning raw content")
            return raw_content

import logging
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

from .config import Config

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

    def __init__(self, config: Config) -> None:
        """Initialize the knowledge base and load documents.

        Loads all markdown files from the docs directory, splits them into
        chunks, creates embeddings, and indexes them in ChromaDB. If the
        vectorstore already exists, reuses it.

        Args:
            config: Configuration object containing paths and model names
        """
        self.config = config
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

    def search(self, query: str, k: int = 3) -> str:
        """Search the knowledge base for relevant documents using semantic similarity.

        Performs a similarity search in the ChromaDB vectorstore and returns
        the top k most relevant document chunks matching the query.

        Args:
            query: Search query string (e.g., "Terraform best practices security")
            k: Number of top results to return (default: 3)

        Returns:
            Concatenated content of the top k matching documents, separated by '---'
        """
        if self.vectorstore is None:
            raise RuntimeError("Vectorstore not initialized")
        results = self.vectorstore.similarity_search(query, k=k)
        return "\n---\n".join([res.page_content for res in results])

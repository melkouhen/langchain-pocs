from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.tools import tool

from .config import Config


class KnowledgeBase:
    """Manages a ChromaDB vector store for semantic search of Terraform best practices.

    Loads documentation files from disk, chunks them into smaller pieces,
    embeds them using an embedding model, and stores them in ChromaDB
    for efficient semantic similarity search.

    Attributes:
        config: Configuration object with paths and model names
        vectorstore: ChromaDB vector store instance for similarity search
    """

    config: Config
    vectorstore: Chroma

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
        5. Adds documents to the vectorstore if not already indexed
        """
        print("📚 Loading knowledge base...")

        # Load documents from docs directory
        loader = DirectoryLoader(
            str(self.config.DOCS_DIR),
            glob="**/*.md",
            loader_cls=TextLoader,
            recursive=True,
        )
        documents = loader.load()
        print(f"  ✓ Loaded {len(documents)} document(s) from {self.config.DOCS_DIR}")

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        docs = text_splitter.split_documents(documents)
        print(f"  ✓ Split into {len(docs)} chunks")

        # Initialize embedding function
        embedding_function = OllamaEmbeddings(model=self.config.EMBEDDING_MODEL)

        # Check if vectorstore already exists
        vectorstore_path = (
            self.config.PROJECT_ROOT / "notebooks" / ".vectorstore"
        )

        if vectorstore_path.exists():
            print(f"  ✓ Vectorstore found, loading existing database...")
            self.vectorstore = Chroma(
                collection_name="terraform_docs",
                embedding_function=embedding_function,
                persist_directory=str(vectorstore_path),
            )
        else:
            print(f"  Creating new vectorstore database...")
            self.vectorstore = Chroma(
                collection_name="terraform_docs",
                embedding_function=embedding_function,
                persist_directory=str(vectorstore_path),
            )

        # Check if documents already indexed
        try:
            existing_count = len(self.vectorstore.get()["ids"])
            if existing_count == 0:
                print(f"  Indexing {len(docs)} documents...")
                self.vectorstore.add_documents(docs)
            else:
                print(
                    f"  ✓ Vectorstore already indexed with {existing_count} documents"
                )
        except (KeyError, ValueError):
            # Collection doesn't exist, create and add documents
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
        results = self.vectorstore.similarity_search(query, k=k)
        return "\n---\n".join([res.page_content for res in results])

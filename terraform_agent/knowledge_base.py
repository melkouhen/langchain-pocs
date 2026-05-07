from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

from .config import Config


class KnowledgeBase:
    def __init__(self, config: Config):
        self.config = config
        self.vectorstore = None
        self._initialize()

    def _initialize(self):
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

        # Create vectorstore
        vectorstore_path = (
            self.config.PROJECT_ROOT / "notebooks" / ".vectorstore2"
        )
        print(f"  Creating vectorstore database...")
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
        except Exception:
            # Collection doesn't exist, create and add documents
            print(f"  Indexing {len(docs)} documents...")
            self.vectorstore.add_documents(docs)

        print(f"  ✓ Vectorstore created and indexed")

    def search(self, query: str, k: int = 3) -> str:
        results = self.vectorstore.similarity_search(query, k=k)
        return "\n---\n".join([res.page_content for res in results])

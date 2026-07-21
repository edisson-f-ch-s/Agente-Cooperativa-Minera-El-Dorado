"""
Construcción y carga del índice vectorial FAISS sobre los PDFs de la Cooperativa.
Implementado como singleton para reutilizarse en todas las invocaciones de buscar_en_documentos.
"""
import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# Rutas
PDF_DIR = Path(__file__).parent.parent / "data" / "documentos"
FAISS_INDEX_DIR = Path(__file__).parent.parent / "faiss_index"
EMBEDDING_MODEL = "models/gemini-embedding-001"

# Singleton en memoria del proceso
_vectorstore: FAISS | None = None


def _build_vectorstore() -> FAISS:
    """
    Carga los 5 PDFs, los divide en chunks y construye el índice FAISS.
    Omite PDFs no encontrados con un warning (no detiene la inicialización).
    """
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    all_docs = []
    pdf_files = list(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        logger.warning("No se encontraron PDFs en %s. El RAG estará vacío.", PDF_DIR)

    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()
            chunks = splitter.split_documents(pages)
            all_docs.extend(chunks)
            logger.info("PDF cargado: %s (%d chunks)", pdf_path.name, len(chunks))
        except Exception as exc:
            logger.warning("No se pudo cargar %s: %s", pdf_path.name, exc)

    if not all_docs:
        logger.warning("Sin documentos disponibles. El índice FAISS estará vacío.")
        # Crear índice vacío con un documento placeholder para evitar errores
        from langchain_core.documents import Document
        all_docs = [Document(page_content="Sin documentos disponibles.", metadata={"source": "vacio"})]

    vs = FAISS.from_documents(all_docs, embeddings)
    vs.save_local(str(FAISS_INDEX_DIR))
    logger.info("Índice FAISS guardado en %s", FAISS_INDEX_DIR)
    return vs


def get_vectorstore() -> FAISS:
    """
    Devuelve el singleton del vectorstore FAISS.
    - Si el índice existe en disco, lo carga.
    - Si no existe o está corrupto, lo reconstruye desde los PDFs.
    """
    global _vectorstore

    if _vectorstore is not None:
        return _vectorstore

    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    if FAISS_INDEX_DIR.exists():
        try:
            _vectorstore = FAISS.load_local(
                str(FAISS_INDEX_DIR),
                embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info("Índice FAISS cargado desde disco.")
            return _vectorstore
        except Exception as exc:
            logger.warning("No se pudo cargar el índice FAISS desde disco (%s). Reconstruyendo...", exc)

    # Construir desde cero
    _vectorstore = _build_vectorstore()
    return _vectorstore

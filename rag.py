import os
from dotenv import load_dotenv

from typing import Optional
from rich.prompt import Prompt

from phi.agent import Agent
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.vectordb.lancedb import LanceDb
from phi.vectordb.search import SearchType

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# LanceDB Vector DB
vector_db = LanceDb(
    table_name="breach",
    uri="data",
    search_type=SearchType.hybrid,
)

pdf_knowledge_base = PDFKnowledgeBase(
    path="data/pdfs",
    # Table name: ai.pdf_documents
    vector_db=vector_db,
    reader=PDFReader(chunk=True),
)


# Comment out after first run
pdf_knowledge_base.load(recreate=True)

def get_rag_knowledge():
    return pdf_knowledge_base




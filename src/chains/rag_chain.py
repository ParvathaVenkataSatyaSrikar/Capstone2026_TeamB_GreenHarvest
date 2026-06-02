"""LangChain RAG helpers — retrieval and LCEL-style context formatting."""
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

from src.rag.retriever import retrieve, ingest_knowledge_base


def search_knowledge_base(query: str, crop: str = "", top_k: int = 4) -> list[dict]:
    return retrieve(query, crop=crop, top_k=top_k)


def format_chunks_for_prompt(chunks: list[dict]) -> str:
    if not chunks:
        return "No matching documents found."
    lines = []
    for chunk in chunks:
        source = chunk.get("metadata", {}).get("source", chunk.get("id", "doc"))
        lines.append(f"[{source}] (score {chunk.get('score', 0)})\n{chunk['text']}")
    return "\n\n".join(lines)


def _retrieve_context(inputs: dict) -> str:
    chunks = search_knowledge_base(
        inputs["question"],
        crop=inputs.get("crop", ""),
        top_k=inputs.get("top_k", 4),
    )
    return format_chunks_for_prompt(chunks)


def build_rag_context_runnable():
    """
    RunnableParallel: parallel pass-through of question + retrieved context string.
    """
    return RunnableParallel({
        "question": RunnablePassthrough(),
        "context": RunnableLambda(_retrieve_context),
        "crop": RunnablePassthrough(),
    })

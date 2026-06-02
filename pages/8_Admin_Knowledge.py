"""Admin portal — knowledge base."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from config.settings import KB_DIR
from src.ui.theme import bootstrap_app
from src.ui.components import apply_global_styles, page_header
from src.ui.portal import render_role_sidebar
from src.auth.session import require_permission
from src.rag.retriever import ingest_knowledge_base, retrieve, load_kb_documents

bootstrap_app()
apply_global_styles()
require_permission("pages/8_Admin_Knowledge.py")
role, _ = render_role_sidebar("Knowledge")

page_header("Knowledge Base (RAG)", "Manage trusted agriculture documents for Gen AI retrieval", role=role)

docs = list(KB_DIR.rglob("*.md"))
st.metric("Documents", len(docs))
st.metric("Chunks", len(load_kb_documents()))

for d in sorted(docs):
    st.caption(str(d.relative_to(KB_DIR)))

if st.button("Re-ingest into vector database", type="primary"):
    n = ingest_knowledge_base()
    st.success(f"Ingested {n} chunks")

st.markdown("### Test retrieval")
q = st.text_input("Test query", "cotton pest yellow leaves")
crop = st.selectbox("Crop filter", ["", "cotton", "paddy", "wheat", "tomato", "soybean"])
if st.button("Search"):
    for ch in retrieve(q, crop=crop, top_k=5):
        st.markdown(f"**{ch['metadata'].get('source')}** — score {ch['score']}")
        st.write(ch["text"][:400])

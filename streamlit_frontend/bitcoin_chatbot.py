"""
bitcoin_chatbot.py (updated)
===========================
A single‑file Streamlit project that reproduces the Langflow export.

Changes vs. first draft
-----------------------
• **Imports gehärtet** → neue Namespaces `langchain_openai` und `langchain_community`, um Deprecation‑Warnings ab LangChain 0.2+ zu vermeiden.  
• **Requirements** ergänzt: `langchain-openai`, `langchain-community`.
"""

from __future__ import annotations

import argparse
import os
import textwrap
from pathlib import Path
from typing import List

import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain_astradb import AstraDBVectorStore

# ──────────────────────────────────────────────────────────────────────────
# Shared helpers
# ──────────────────────────────────────────────────────────────────────────

def _astra_vs(token: str, api_endpoint: str, database: str, collection: str, embedding_model: OpenAIEmbeddings) -> AstraDBVectorStore:
    """Return (and create if missing) a vector‑store backed by Astra DB."""
    return AstraDBVectorStore(
        token=token,
        api_endpoint=api_endpoint,
        namespace=database,
        collection_name=collection,
        embedding=embedding_model,
    )


def _load_docs(paths: List[Path]):
    """Load documents from arbitrary file paths (PDF & text)."""
    docs = []
    for p in paths:
        p = Path(p)
        if p.suffix.lower() == ".pdf":
            docs.extend(PyPDFLoader(str(p)).load())
        else:
            docs.extend(TextLoader(str(p)).load())
    return docs

# ──────────────────────────────────────────────────────────────────────────
# Ingestion (CLI)
# ──────────────────────────────────────────────────────────────────────────

def ingest(files: List[str], token: str, api_endpoint: str, database: str, collection: str):
    """Read, split and embed files, mirroring SplitText(1000/200) ➜ AstraDB"""
    embeds = OpenAIEmbeddings()
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(
        _load_docs(files)
    )
    vs = _astra_vs(token, api_endpoint, database, collection, embeds)
    vs.add_documents(chunks)
    print(f"✅ Ingested {len(chunks):,} chunks into collection '{collection}'.")

# ──────────────────────────────────────────────────────────────────────────
# Prompt (exact template from Langflow)
# ──────────────────────────────────────────────────────────────────────────

PROMPT_TEMPLATE = textwrap.dedent(
    """
    [Deine Rolle]
    Du bist ein freundlicher Lerncoach für Bitcoin. Antworte auf Deutsch, außer der User verwendet eine andere Sprache.

    [Wissensbasis]
    {context}

    [Fragenkatalog]
    {fragenkatalog}

    [Chatverlauf]
    {history}

    [Aktuelle Nutzeranfrage]
    {question}

    [Deine Aufgaben]
    1. Wenn {question} eine Frage über bitcoin ist:
       - Suche im {fragenkatalog} nach der passenden Antwort und gib ausschließlich die dort hinterlegte Antwort wieder.
       - Stelle anschließend ein Frage aus dem Fragenkatalog {fragenkatalog}: Stelle diese Frage höflich als Einladung ("Möchtest du, dass ich dir auch erkläre, [Frage aus dem Katalog]?")

    2. Wenn {question} eine kurze Antwort wie "Ja" oder "Nein" ist:
       - Wenn zuvor eine Einladung gestellt wurde (siehe {history}):
         - Bei "Ja": Gib ausschließlich die Antwort zur letzten angekündigten Folgefrage aus dem {fragenkatalog}.
         - Bei "Nein": Bestätige freundlich ("Alles klar, sag mir einfach, wenn du etwas anderes wissen möchtest.") und warte auf eine neue Nutzerfrage.
       - Wenn keine vorherige Einladung vorliegt:
         - Antworte freundlich, dass du auf eine neue Frage wartest.

    3. Wenn {question} unklar oder doppeldeutig ist:
       - Bitte höflich um eine Präzisierung ("Meinst du X oder Y?").

    [Strenge Regeln]
    - Keine eigenen Themen beginnen.
    - Keine spontanen Erklärungen aus {context} geben, wenn nicht ausdrücklich vom Nutzer danach gefragt.
    - Keine improvisierten Anschlussfragen.
    - Nur Fragen und Antworten aus dem {fragenkatalog} verwenden.
    - Antworten maximal 2–3 Sätze lang.
    - Freundlich, locker, kurze Sätze. Keine Fachbegriffe ohne Erklärung. Keine Listen.
    - Frage nach, ob du das genauer erklären sollst.
    - wenn möglich eine Frage stellen, die noch nicht beantwortet wurde oder schon lange nicht mehr beantwortet wurde. Verwende dafür {history}
    - Fragen nicht wiederholen, außer der User hat sie nicht verstanden

    {question}

    Antwort:
    """
)

FRAGENKATALOG = (
    """1. Frage: Was ist Bitcoin?\n1. Antwort: Bitcoin ist eine digitale Währung, ...\n2. Frage: Wer hat Bitcoin erfunden?\n2. Antwort: Bitcoin wurde 2008 ...\n... (gekürzt) ...\n22. Frage: Was passiert nach dem letzten Bitcoin?\n22. Antwort: Dann gibt es keine neuen Bitcoins mehr. Miner bekommen dann nur noch Gebühren für Transaktionen."""
)

# ──────────────────────────────────────────────────────────────────────────
# Retrieval + Chat chain
# ──────────────────────────────────────────────────────────────────────────

def build_chain(token: str, api_endpoint: str, database: str, collection: str):
    embeds = OpenAIEmbeddings()
    vs = _astra_vs(token, api_endpoint, database, collection, embeds)
    retriever = vs.as_retriever(search_kwargs={"k": 4})

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3, streaming=True)

    memory = ConversationBufferMemory(memory_key="history", return_messages=True)

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "fragenkatalog", "history", "question"],
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=False,
        verbose=False,
    )

# ──────────────────────────────────────────────────────────────────────────
# Streamlit UI
# ──────────────────────────────────────────────────────────────────────────

def chat_ui():
    st.set_page_config(page_title="Bitcoin Lerncoach", page_icon="₿")
    st.title("₿ Bitcoin Lerncoach – Dein Fragen‑und‑Antwort‑Coach")

    # Required secrets
    token = st.secrets["ASTRA_TOKEN"]
    api = st.secrets["ASTRA_API_ENDPOINT"]
    db = st.secrets["ASTRA_DB"]
    col = st.secrets["ASTRA_COLLECTION"]

    if "chain" not in st.session_state:
        st.session_state.chain = build_chain(token, api, db, col)
        st.session_state.messages = []

    # replay history
    for m in st.session_state.messages:
        st.chat_message(m["role"]).write(m["content"])

    if question := st.chat_input("Frag mich etwas über Bitcoin …"):
        st.session_state.messages.append({"role": "user", "content": question})
        st.chat_message("user").write(question)

        answer = st.session_state.chain(
            {"question": question, "fragenkatalog": FRAGENKATALOG}
        )["answer"]

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)

# ──────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Bitcoin chatbot – load or chat")
    sub = parser.add_subparsers(dest="cmd")

    load = sub.add_parser("load", help="Ingest docs into AstraDB")
    load.add_argument("--files", nargs="+", required=True)
    load.add_argument("--database", required=True)
    load.add_argument("--collection", required=True)

    args, _ = parser.parse_known_args()

    if args.cmd == "load":
        ingest(
            files=args.files,
            token=os.environ["ASTRA_TOKEN"],
            api_endpoint=os.environ["ASTRA_API_ENDPOINT"],
            database=args.database,
            collection=args.collection,
        )
    else:
        chat_ui()

if __name__ == "__main__":
    main()

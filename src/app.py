import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv(os.path.expanduser("~/ai-portfolio/.env"))

# ── Configuración de página ──────────────────────────────────────
st.set_page_config(
    page_title="Compliance Assistant",
    page_icon="🏦",
    layout="wide"
)

# ── Cargar o construir vector store ─────────────────────────────
@st.cache_resource
def init_rag():
    embeddings = OpenAIEmbeddings()

    if os.path.exists("chroma_db"):
        vectorstore = Chroma(
            persist_directory="chroma_db",
            embedding_function=embeddings
        )
    else:
        with st.spinner("📄 Indexando documentos por primera vez..."):
            loader = DirectoryLoader(
                "docs/",
                glob="**/*.pdf",
                loader_cls=PyPDFLoader,
                show_progress=False
            )
            documents = loader.load()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.split_documents(documents)
            vectorstore = Chroma.from_documents(
                chunks,
                embeddings,
                persist_directory="chroma_db"
            )
    return vectorstore

def build_chain(vectorstore):
    template = """You are an expert assistant in international banking and financial regulation.
Use ONLY the provided context to answer. If you cannot find the answer, say:
"No encontré información sobre eso en los documentos disponibles."
Always respond in Spanish, citing the source document when possible.

Context:
{context}

Question: {question}

Detailed answer with source:"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 20}
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever

# ── UI ───────────────────────────────────────────────────────────
st.title("🏦 Compliance Assistant")
st.caption("Basilea III · Inclusión Financiera · Regulación Bancaria Internacional")

with st.sidebar:
    st.header("📚 Documentos indexados")
    st.success("✅ Basilea III - Post Crisis Reforms (BIS)")
    st.success("✅ Payment Aspects of Financial Inclusion (BIS)")
    st.divider()
    st.metric("Chunks indexados", "1,054")
    st.metric("Modelo", "GPT-4o mini")
    st.metric("Vector DB", "ChromaDB")
    st.divider()
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()

# ── Historial de mensajes ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hola, soy tu asistente de compliance bancario. Puedo responder preguntas sobre regulación de Basilea III e inclusión financiera. ¿En qué te puedo ayudar?"
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input y respuesta ────────────────────────────────────────────
if question := st.chat_input("Ej: ¿Cuáles son los requerimientos de capital Tier 1?"):

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Buscando en documentos..."):
            vectorstore = init_rag()
            chain, retriever = build_chain(vectorstore)
            docs = retriever.invoke(question)
            answer = chain.invoke(question)
            sources = list(set([
                os.path.basename(doc.metadata.get('source', 'N/A'))
                for doc in docs
            ]))

        st.markdown(answer)
        st.caption(f"📄 Fuentes: {', '.join(sources)}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"{answer}\n\n📄 *Fuentes: {', '.join(sources)}*"
    })
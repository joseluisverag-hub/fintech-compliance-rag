import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from azure.storage.blob import BlobServiceClient
import tempfile
import pypdf

load_dotenv(os.path.expanduser("~/ai-portfolio/.env"))

st.set_page_config(
    page_title="Compliance Assistant Chile",
    page_icon="🏦",
    layout="wide"
)

def load_pdfs_from_azure():
    """Descarga PDFs desde Azure Blob Storage y extrae texto."""
    print("📥 Descargando PDFs desde Azure Blob Storage...")
    
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container = os.getenv("AZURE_STORAGE_CONTAINER")
    
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    container_client = blob_service.get_container_client(container)
    
    documents = []
    blobs = list(container_client.list_blobs())
    
    for blob in blobs:
        if not blob.name.endswith('.pdf'):
            continue
            
        print(f"  → Procesando: {blob.name}")
        blob_client = container_client.get_blob_client(blob.name)
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(blob_client.download_blob().readall())
            tmp_path = tmp.name
        
        # Extraer texto con pypdf
        reader = pypdf.PdfReader(tmp_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and len(text.strip()) > 50:
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "source": blob.name,
                        "page": i + 1,
                        "blob_url": f"https://storagecompliancejose.blob.core.windows.net/{container}/{blob.name}"
                    }
                ))
        
        os.unlink(tmp_path)
    
    print(f"✅ {len(documents)} páginas cargadas desde Azure")
    return documents

@st.cache_resource
def init_rag():
    embeddings = OpenAIEmbeddings()
    
    vectorstore = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
        index_name=os.getenv("AZURE_SEARCH_INDEX"),
        embedding_function=embeddings.embed_query
    )
    
    # Verificar si ya hay documentos indexados
    try:
        results = vectorstore.similarity_search("test", k=1)
        already_indexed = len(results) > 0
    except:
        already_indexed = False
    
    if not already_indexed:
        with st.spinner("📥 Descargando PDFs desde Azure Blob Storage..."):
            documents = load_pdfs_from_azure()
        
        with st.spinner(f"✂️ Dividiendo {len(documents)} páginas en chunks..."):
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.split_documents(documents)
        
        with st.spinner(f"🔢 Indexando {len(chunks)} chunks en Azure AI Search..."):
            vectorstore.add_documents(chunks)
        
        st.success(f"✅ {len(chunks)} chunks indexados en Azure AI Search")
    
    return vectorstore

def build_chain(vectorstore):
    template = """You are an expert assistant in Chilean and international banking and financial regulation.
Use ONLY the provided context to answer. If you cannot find the answer, say:
"No encontré información sobre eso en los documentos disponibles."
Always respond in Spanish, citing the source document and page when possible.
When referencing Chilean documents (IEF, CMF), highlight their relevance to the local financial system.
Be specific with data, percentages, and dates when available in the context.

Context:
{context}

Question: {question}

Detailed answer with source and page:"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    retriever = vectorstore.as_retriever(k=6)

    def format_docs(docs):
        return "\n\n".join(
            f"[{doc.metadata.get('source', 'N/A')} - Página {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
            for doc in docs
        )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever

# ── UI ───────────────────────────────────────────────────────────
st.title("🏦 Compliance Assistant — Banca Chile")
st.caption("Banco Central · CMF · Basilea III · Regulación Bancaria Internacional")

with st.sidebar:
    st.header("☁️ Infraestructura Azure")
    st.success("✅ Azure Blob Storage")
    st.success("✅ Azure AI Search")
    st.divider()
    st.header("📚 Documentos")
    st.info("📄 IEF 2do Semestre 2025 — BCCh")
    st.info("📄 IEF 1er Semestre 2025 — BCCh")
    st.info("📄 Plan Regulación CMF 2025-2026")
    st.info("📄 Basilea III Post-Crisis Reforms")
    st.info("📄 Financial Inclusion Fintech Era")
    st.divider()
    st.metric("Vector Store", "Azure AI Search")
    st.metric("Storage", "Azure Blob")
    st.metric("LLM", "GPT-4o mini")
    st.metric("Región", "East US")
    st.divider()
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hola, soy tu asistente de compliance bancario para Chile. Tengo acceso a los últimos informes del Banco Central 2025, normativas CMF y estándares internacionales de Basilea III, todos almacenados en Azure. ¿En qué te puedo ayudar?"
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ej: ¿Cuáles son los principales riesgos del sistema financiero chileno en 2025?"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Buscando en Azure AI Search..."):
            vectorstore = init_rag()
            chain, retriever = build_chain(vectorstore)
            docs = retriever.invoke(question)
            answer = chain.invoke(question)
            sources = list(set([
                f"{doc.metadata.get('source', 'N/A')} p.{doc.metadata.get('page', 'N/A')}"
                for doc in docs
            ]))

        st.markdown(answer)
        st.caption(f"📄 Fuentes: {', '.join(sources)}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"{answer}\n\n📄 *Fuentes: {', '.join(sources)}*"
    })
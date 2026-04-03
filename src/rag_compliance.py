import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv(os.path.expanduser("~/ai-portfolio/.env"))

def build_vectorstore():
    print("📄 Cargando documentos...")
    loader = DirectoryLoader(
        "../docs/",
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True
    )
    documents = loader.load()
    print(f"✅ {len(documents)} páginas cargadas")

    print("✂️  Dividiendo en chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ {len(chunks)} chunks creados")

    print("🔢 Generando embeddings y guardando en ChromaDB...")
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="../chroma_db"
    )
    print("✅ Vector store listo")
    return vectorstore

def load_vectorstore():
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        persist_directory="../chroma_db",
        embedding_function=embeddings
    )
    return vectorstore

def build_qa_chain(vectorstore):
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

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

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

if __name__ == "__main__":
    if os.path.exists("../chroma_db"):
        print("🔄 Cargando vector store existente...")
        vectorstore = load_vectorstore()
    else:
        vectorstore = build_vectorstore()

    chain, retriever = build_qa_chain(vectorstore)

    print("\n🏦 Compliance Assistant listo. Escribe 'salir' para terminar.\n")
    while True:
        question = input("Tu pregunta: ")
        if question.lower() == "salir":
            break
        docs = retriever.invoke(question)
        answer = chain.invoke(question)
        print(f"\n📋 Respuesta:\n{answer}")
        sources = [doc.metadata.get('source', 'N/A') for doc in docs]
        print(f"\n📄 Fuentes: {', '.join(set(sources))}\n")
        print("-" * 60)
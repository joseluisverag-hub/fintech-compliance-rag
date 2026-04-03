# 🏦 Compliance Assistant — RAG Financiero

Asistente inteligente de regulación bancaria construido con RAG (Retrieval-Augmented Generation). Responde preguntas sobre normativas financieras internacionales citando fuentes específicas.

## 🎯 Problema de negocio
Los equipos de compliance en bancos y fintechs gastan cientos de horas buscando información en regulaciones dispersas. Este sistema reduce ese tiempo a segundos, con respuestas precisas y trazables.

## 🏗️ Arquitectura
## 🛠️ Tech Stack
- **LLM:** GPT-4o mini (OpenAI)
- **RAG Framework:** LangChain + LangGraph
- **Vector DB:** ChromaDB
- **Embeddings:** text-embedding-ada-002
- **UI:** Streamlit
- **Chunking:** Recursive Character Text Splitter (1000 chars, 200 overlap)
- **Retrieval:** MMR (Maximum Marginal Relevance)

## 📚 Documentos indexados
- Basilea III: Finalising post-crisis reforms (BIS, 162 páginas)
- Payment aspects of financial inclusion in the fintech era (BIS, 80 páginas)
- Total: 1,054 chunks indexados

## 🚀 Instalación
```bash
git clone https://github.com/TU_USUARIO/fintech-compliance-rag
cd fintech-compliance-rag
pip install -r requirements.txt
cp .env.example .env  # agregar tu OPENAI_API_KEY
streamlit run src/app.py
```

## 💼 Casos de uso empresariales
- Bancos: consulta rápida de normativas de capital y liquidez
- Fintechs: verificación de requisitos regulatorios
- Equipos de compliance: onboarding de nuevos analistas
- Consultoras: due diligence regulatorio

## 👤 Autor
José Luis Vera — IT Operations Senior & AI Engineer

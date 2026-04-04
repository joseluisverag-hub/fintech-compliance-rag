# 🏦 Compliance Assistant — Banca Chile

Asistente inteligente de regulación bancaria construido con RAG (Retrieval-Augmented Generation) sobre infraestructura Azure enterprise. Responde preguntas sobre normativas financieras chilenas e internacionales citando fuentes y páginas específicas.

🌐 **Demo en vivo:** https://fintech-compliance-rag-123.streamlit.app

## 🎯 Problema de negocio
Los equipos de compliance en bancos y fintechs gastan cientos de horas buscando información en regulaciones dispersas. Este sistema reduce ese tiempo a segundos, con respuestas precisas, trazables y basadas en documentos oficiales vigentes.

## 🏗️ Arquitectura
```
┌─────────────────────────────────────────────────────┐
│                    AZURE (East US)                  │
│                                                     │
│  ┌─────────────────┐      ┌──────────────────────┐  │
│  │ Blob Storage    │─────►│ Azure AI Search      │  │
│  │                 │      │                      │  │
│  │ 📄 IEF 2S 2025  │      │ vectores + chunks    │  │
│  │ 📄 IEF 1S 2025  │      │ metadata + páginas   │  │
│  │ 📄 CMF 2025     │      │ búsqueda semántica   │  │
│  │ 📄 Basilea III  │      └──────────┬───────────┘  │
│  │ 📄 BIS FinTech  │                 │              │
│  └─────────────────┘                 │              │
└─────────────────────────────────────────────────────┘
                                       │
                                       ▼
                              OpenAI GPT-4o mini
                                       │
                                       ▼
                               Streamlit UI
                          (pregunta + respuesta
                           + fuente + página)
```
## 🛠️ Tech Stack

| Capa | Tecnología |
|---|---|
| Almacenamiento de documentos | Azure Blob Storage |
| Vector store | Azure AI Search |
| Embeddings | OpenAI text-embedding-ada-002 |
| LLM | GPT-4o mini |
| Orquestación RAG | LangChain |
| UI | Streamlit |
| Chunking | Recursive Character Text Splitter (1000 chars, 200 overlap) |

## 📚 Documentos indexados

| Documento | Fuente | Año |
|---|---|---|
| Informe de Estabilidad Financiera 2do Semestre | Banco Central de Chile | 2025 |
| Informe de Estabilidad Financiera 1er Semestre | Banco Central de Chile | 2025 |
| Plan de Regulación CMF | Comisión para el Mercado Financiero | 2025-2026 |
| Basel III: Finalising post-crisis reforms | BIS | 2017 |
| Payment aspects of financial inclusion | BIS | 2020 |

## 🚀 Instalación
```bash
git clone https://github.com/joseluisverag-hub/fintech-compliance-rag
cd fintech-compliance-rag
pip install -r requirements.txt
cp .env.example .env  # configurar variables de Azure y OpenAI
streamlit run src/app.py
```

## ⚙️ Variables de entorno
```env
OPENAI_API_KEY=sk-...
AZURE_SEARCH_ENDPOINT=https://search-compliance-jose.search.windows.net
AZURE_SEARCH_KEY=...
AZURE_SEARCH_INDEX=compliance-docs
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER=compliance-docs
```

## 💼 Casos de uso empresariales

- **Bancos:** consulta rápida de normativas de capital, liquidez y riesgo operacional
- **Fintechs:** verificación de requisitos regulatorios CMF vigentes
- **Equipos de compliance:** onboarding de nuevos analistas con base de conocimiento actualizada
- **Consultoras:** due diligence regulatorio con trazabilidad de fuentes
- **AFP y seguros:** consulta de normativas aplicables al mercado de capitales chileno

## 🔐 Seguridad enterprise

- Documentos almacenados en Azure Blob Storage con acceso privado
- Búsqueda vectorial en Azure AI Search con autenticación por API key
- Sin exposición de documentos originales al usuario final
- Arquitectura compatible con políticas de datos de instituciones financieras reguladas

## 👤 Autor
José Luis Vera — IT Operations Senior & AI Engineer  
[LinkedIn](www.linkedin.com/in/jose-luis-vera-gonzalez) | [GitHub](https://github.com/joseluisverag-hub)
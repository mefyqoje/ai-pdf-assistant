# 📄 AI PDF Assistant

AI PDF Assistant — это RAG-приложение для работы с PDF-документами.

Пользователь загружает PDF, система извлекает текст, разбивает его на чанки, строит эмбеддинги, сохраняет их в FAISS и позволяет задавать вопросы по содержимому документа.

Ответ генерируется локальной LLM через Ollama.

---

## Возможности

- загрузка PDF;
- извлечение текста из PDF;
- разбиение текста на чанки;
- создание эмбеддингов;
- семантический поиск по документу;
- FAISS-векторное хранилище;
- ответы на вопросы по PDF;
- указание страниц-источников;
- FastAPI backend;
- Streamlit web interface;
- локальная LLM через Ollama.

---

## Архитектура

```text
PDF
 ↓
PDF Loader
 ↓
Text Splitter
 ↓
Embedding Model
 ↓
FAISS Vector Store
 ↓
Retriever
 ↓
Prompt Builder
 ↓
Ollama LLM
 ↓
Answer + Sources
```

---

## Структура проекта

```text
ai-pdf-assistant/
├── app/
│   ├── api.py
│   └── streamlit_app.py
├── data/
│   ├── documents/
│   └── vector_store/
├── src/
│   └── pdf_assistant/
│       ├── embeddings/
│       │   └── embedding_model.py
│       ├── llm/
│       │   └── ollama_client.py
│       ├── loaders/
│       │   └── pdf_loader.py
│       ├── retriever/
│       │   └── vector_store.py
│       ├── services/
│       │   ├── indexing_service.py
│       │   ├── qa_service.py
│       │   └── retriever_service.py
│       ├── splitters/
│       │   └── text_splitter.py
│       └── config.py
├── tests/
├── run_api.py
├── run_streamlit.py
├── requirements.txt
└── README.md
```

---

## Стек

- Python 3.11
- FastAPI
- Streamlit
- PyMuPDF
- Sentence Transformers
- FAISS
- LangChain Text Splitters
- Ollama
- Llama 3.2
- Requests

---

## Быстрый запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/<username>/ai-pdf-assistant.git
cd ai-pdf-assistant
```

### 2. Создать виртуальное окружение

```bash
python -m venv venv
```

### 3. Активировать окружение

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Установить зависимости

```bash
pip install -r requirements.txt
```

---

## Ollama

Проект использует локальную LLM через Ollama.

### Установить Ollama

```powershell
irm https://ollama.com/install.ps1 | iex
```

### Скачать модель

```powershell
ollama pull llama3.2:3b
```

### Проверить

```powershell
ollama run llama3.2:3b
```

---

## Запуск приложения

### Терминал 1 — FastAPI

```powershell
python run_api.py
```

API будет доступен:

```text
http://127.0.0.1:8000/docs
```

### Терминал 2 — Streamlit

```powershell
python run_streamlit.py
```

Web UI будет доступен:

```text
http://localhost:8501
```

---

## API

### GET /

Проверка работы API.

Ответ:

```json
{
  "message": "AI PDF Assistant API запущен"
}
```

### POST /upload

Загрузка и индексация PDF.

### POST /ask

Вопрос по документу.

Пример запроса:

```json
{
  "question": "О чем говорится в документе?"
}
```

Пример ответа:

```json
{
  "answer": "В документе говорится о...",
  "sources": [
    {
      "page": 3,
      "score": 0.72,
      "text": "Фрагмент текста..."
    }
  ]
}
```

---

## Как работает RAG

Проект реализует Retrieval-Augmented Generation:

- PDF загружается пользователем.
- Из документа извлекается текст.
- Текст разбивается на чанки.
- Для чанков создаются эмбеддинги.
- Эмбеддинги сохраняются в FAISS.
- Вопрос пользователя преобразуется в эмбеддинг.
- FAISS находит наиболее релевантные фрагменты.
- Эти фрагменты передаются в LLM как контекст.
- LLM генерирует ответ только на основе найденного контекста.

---

## Что демонстрирует проект

Проект показывает навыки:

- RAG;
- LLM-интеграция;
- semantic search;
- embeddings;
- vector database;
- PDF processing;
- FastAPI;
- Streamlit;
- локальные LLM;
- архитектура AI-приложений.

---

## Планы развития

- поддержка нескольких PDF одновременно;
- сохранение имени файла в источниках;
- история чата;
- Docker;
- тесты;
- GitHub Actions;
- выбор модели через конфиг;
- поддержка OpenAI API;
- деплой.

---

## Автор

Проект создан как часть портфолио ML/AI Engineer.
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"
MAX_HISTORY_MESSAGES = 6
REQUEST_TIMEOUT = 600


st.set_page_config(
    page_title="AI PDF Assistant",
    page_icon="📄",
    layout="wide",
)


def initialize_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "indexed_documents" not in st.session_state:
        st.session_state.indexed_documents = []


def render_sources(
    sources: list[dict],
) -> None:
    if not sources:
        st.info("Источники не найдены.")
        return

    st.caption("Источники")

    for source in sources:
        document = source.get(
            "document",
            "Неизвестный документ",
        )
        page = source.get(
            "page",
            "неизвестна",
        )
        reranker_score = float(
            source.get(
                "score",
                0.0,
            )
        )
        retrieval_score = float(
            source.get(
                "retrieval_score",
                0.0,
            )
        )
        text = source.get(
            "text",
            "Текст источника отсутствует.",
        )

        title = (
            f"📄 {document} | "
            f"страница {page} | "
            f"rerank={reranker_score:.3f}"
        )

        with st.expander(title):
            st.caption(
                f"FAISS score: {retrieval_score:.3f}"
            )
            st.write(text)


def build_history_for_api() -> list[dict]:
    history = []

    for message in st.session_state.messages[:-1]:
        role = message.get("role")

        content = str(
            message.get(
                "content",
                "",
            )
        ).strip()

        if role in {"user", "assistant"} and content:
            history.append(
                {
                    "role": role,
                    "content": content,
                }
            )

    return history[-MAX_HISTORY_MESSAGES:]


def upload_documents(
    uploaded_files,
) -> None:
    successful_files = 0
    total_chunks = 0

    progress = st.progress(0)

    for index, uploaded_file in enumerate(uploaded_files):
        with st.spinner(
            f"Индексируем документ «{uploaded_file.name}»..."
        ):
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf",
                )
            }

            try:
                response = requests.post(
                    f"{API_URL}/upload",
                    files=files,
                    timeout=REQUEST_TIMEOUT,
                )
            except requests.RequestException as error:
                st.error(
                    f"Не удалось подключиться к API при загрузке "
                    f"«{uploaded_file.name}»: {error}"
                )

                progress.progress(
                    (index + 1) / len(uploaded_files)
                )
                continue

            if response.status_code == 200:
                data = response.json()

                filename = data.get(
                    "filename",
                    uploaded_file.name,
                )
                chunks_count = int(
                    data.get(
                        "chunks_count",
                        0,
                    )
                )

                successful_files += 1
                total_chunks += chunks_count

                if (
                    filename
                    not in st.session_state.indexed_documents
                ):
                    st.session_state.indexed_documents.append(
                        filename
                    )

                st.success(
                    f"«{filename}» проиндексирован: "
                    f"{chunks_count} чанков."
                )
            else:
                st.error(
                    f"Ошибка индексации «{uploaded_file.name}»: "
                    f"{response.text}"
                )

        progress.progress(
            (index + 1) / len(uploaded_files)
        )

    if successful_files:
        st.info(
            f"Успешно проиндексировано документов: "
            f"{successful_files}. "
            f"Всего добавлено чанков: {total_chunks}."
        )


def render_sidebar() -> None:
    with st.sidebar:
        st.header("База документов")

        uploaded_files = st.file_uploader(
            "Загрузите PDF-документы",
            type=["pdf"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            if st.button(
                "Проиндексировать документы",
                use_container_width=True,
            ):
                upload_documents(uploaded_files)

        if st.session_state.indexed_documents:
            st.subheader("Загруженные документы")

            for document in st.session_state.indexed_documents:
                st.write(f"- {document}")
        else:
            st.caption(
                "В текущей сессии документы еще не загружены."
            )

        st.divider()

        if st.button(
            "Очистить историю чата",
            use_container_width=True,
        ):
            st.session_state.messages = []
            st.rerun()


def render_chat_history() -> None:
    for message in st.session_state.messages:
        role = message.get(
            "role",
            "assistant",
        )
        content = message.get(
            "content",
            "",
        )

        with st.chat_message(role):
            st.markdown(content)

            search_query = message.get(
                "search_query",
            )

            if search_query:
                st.caption(
                    f"Поисковый запрос с учетом контекста: "
                    f"{search_query}"
                )

            sources = message.get(
                "sources",
            )

            if sources:
                render_sources(sources)


def request_answer(
    question: str,
) -> None:
    history_for_api = build_history_for_api()

    with st.chat_message("assistant"):
        with st.spinner(
            "Ищем информацию и формируем ответ..."
        ):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question,
                        "history": history_for_api,
                    },
                    timeout=REQUEST_TIMEOUT,
                )
            except requests.RequestException as error:
                error_message = (
                    f"Не удалось подключиться к API: {error}"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )
                return

            if response.status_code != 200:
                error_message = (
                    f"API вернул ошибку "
                    f"{response.status_code}: "
                    f"{response.text}"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )
                return

            result = response.json()

            answer = result.get(
                "answer",
                "Ответ отсутствует.",
            )
            sources = result.get(
                "sources",
                [],
            )
            search_query = result.get(
                "search_query",
            )

            st.markdown(answer)

            if (
                search_query
                and search_query.strip()
                != question.strip()
            ):
                st.caption(
                    f"Поисковый запрос с учетом контекста: "
                    f"{search_query}"
                )

            render_sources(sources)

            assistant_message = {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }

            if (
                search_query
                and search_query.strip()
                != question.strip()
            ):
                assistant_message["search_query"] = (
                    search_query
                )

            st.session_state.messages.append(
                assistant_message
            )


initialize_session_state()

st.title("📄 AI PDF Assistant")

st.write(
    "Загрузите один или несколько PDF-документов "
    "и задавайте вопросы по общей базе знаний."
)

render_sidebar()
render_chat_history()

question = st.chat_input(
    "Задайте вопрос по загруженным документам"
)

if question:
    clean_question = question.strip()

    if clean_question:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": clean_question,
            }
        )

        with st.chat_message("user"):
            st.markdown(clean_question)

        request_answer(clean_question)
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI PDF Assistant",
    page_icon="📄",
    layout="wide",
)

st.title("📄 AI PDF Assistant")
st.write(
    "Загрузите один или несколько PDF-документов, "
    "после чего задавайте вопросы по общей базе знаний."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "indexed_documents" not in st.session_state:
    st.session_state.indexed_documents = []


with st.sidebar:
    st.header("База документов")

    uploaded_files = st.file_uploader(
        "Загрузите PDF-документы",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files and st.button(
        "Проиндексировать документы",
        use_container_width=True,
    ):
        successful_files = 0
        total_chunks = 0

        progress = st.progress(0)

        for index, uploaded_file in enumerate(uploaded_files):
            with st.spinner(f"Индексируем {uploaded_file.name}..."):
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
                        timeout=600,
                    )

                    if response.status_code == 200:
                        data = response.json()

                        successful_files += 1
                        total_chunks += data["chunks_count"]

                        if data["filename"] not in st.session_state.indexed_documents:
                            st.session_state.indexed_documents.append(
                                data["filename"]
                            )

                        st.success(
                            f"{data['filename']}: "
                            f"{data['chunks_count']} чанков"
                        )
                    else:
                        st.error(
                            f"{uploaded_file.name}: "
                            f"{response.text}"
                        )

                except requests.RequestException as error:
                    st.error(
                        f"Не удалось подключиться к API: {error}"
                    )

            progress.progress((index + 1) / len(uploaded_files))

        if successful_files:
            st.info(
                f"Проиндексировано документов: {successful_files}. "
                f"Всего добавлено чанков: {total_chunks}."
            )

    if st.session_state.indexed_documents:
        st.subheader("Загруженные документы")

        for document in st.session_state.indexed_documents:
            st.write(f"- {document}")
    else:
        st.caption("Документы еще не загружены.")

    st.divider()

    if st.button(
        "Очистить историю чата",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            st.caption("Источники")

            for source in message["sources"]:
                document = source.get(
                    "document",
                    "Неизвестный документ",
                )
                page = source.get(
                    "page",
                    "неизвестна",
                )
                score = source.get(
                    "score",
                    0.0,
                )

                title = (
                    f"📄 {document} | "
                    f"страница {page} | "
                    f"score={score:.3f}"
                )

                with st.expander(title):
                    st.write(source["text"])


question = st.chat_input(
    "Задайте вопрос по загруженным документам"
)

if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Ищем информацию и формируем ответ..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=600,
                )

                if response.status_code == 200:
                    result = response.json()

                    answer = result["answer"]
                    sources = result["sources"]

                    st.markdown(answer)

                    if sources:
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
                            score = source.get(
                                "score",
                                0.0,
                            )

                            title = (
                                f"📄 {document} | "
                                f"страница {page} | "
                                f"score={score:.3f}"
                            )

                            with st.expander(title):
                                st.write(source["text"])

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )
                else:
                    error_message = response.text
                    st.error(error_message)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": (
                                "Не удалось получить ответ от API."
                            ),
                        }
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
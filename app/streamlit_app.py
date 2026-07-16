import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI PDF Assistant",
    page_icon="📄",
    layout="centered",
)

st.title("📄 AI PDF Assistant")

st.write(
    "Загрузите один или несколько PDF-документов, "
    "после чего задавайте вопросы по общей базе знаний."
)

uploaded_files = st.file_uploader(
    "Загрузите PDF-документы",
    type=["pdf"],
    accept_multiple_files=True,
)

if uploaded_files:
    if st.button("Проиндексировать документы"):
        successful_files = 0
        total_chunks = 0

        progress = st.progress(0)

        for index, uploaded_file in enumerate(uploaded_files):
            with st.spinner(
                f"Индексируем {uploaded_file.name}..."
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
                        timeout=600,
                    )

                    if response.status_code == 200:
                        data = response.json()

                        successful_files += 1
                        total_chunks += data["chunks_count"]

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

            progress.progress(
                (index + 1) / len(uploaded_files)
            )

        if successful_files:
            st.info(
                f"Проиндексировано документов: {successful_files}. "
                f"Всего добавлено чанков: {total_chunks}."
            )

st.divider()

question = st.text_area(
    "Ваш вопрос по документам",
    placeholder=(
        "Например: какие требования к безопасности "
        "указаны в загруженных документах?"
    ),
    height=120,
)

if st.button("Задать вопрос"):
    if not question.strip():
        st.warning("Введите вопрос.")
    else:
        with st.spinner("Ищем информацию и формируем ответ..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=600,
                )

                if response.status_code == 200:
                    result = response.json()

                    st.subheader("Ответ")
                    st.write(result["answer"])

                    st.subheader("Источники")

                    if not result["sources"]:
                        st.info("Источники не найдены.")

                    for source in result["sources"]:
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
                else:
                    st.error(response.text)

            except requests.RequestException as error:
                st.error(
                    f"Не удалось подключиться к API: {error}"
                )
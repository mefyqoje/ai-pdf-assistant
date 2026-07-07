import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI PDF Assistant",
    page_icon="📄",
    layout="centered",
)

st.title("📄 AI PDF Assistant")
st.write("Загрузите PDF-документ и задавайте вопросы по его содержанию.")

uploaded_file = st.file_uploader(
    "Загрузите PDF",
    type=["pdf"],
)

if uploaded_file is not None:
    if st.button("Проиндексировать документ"):
        with st.spinner("Загружаем и индексируем PDF..."):
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf",
                )
            }

            response = requests.post(
                f"{API_URL}/upload",
                files=files,
                timeout=300,
            )

            if response.status_code == 200:
                data = response.json()

                st.success(data["message"])
                st.write(f"Файл: {data['filename']}")
                st.write(f"Количество чанков: {data['chunks_count']}")
            else:
                st.error(response.text)

st.divider()

question = st.text_area(
    "Ваш вопрос по документу",
    placeholder="Например: какие основные выводы представлены в документе?",
    height=120,
)

if st.button("Задать вопрос"):
    if not question.strip():
        st.warning("Введите вопрос.")
    else:
        with st.spinner("Генерируем ответ..."):
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question},
                timeout=300,
            )

            if response.status_code == 200:
                result = response.json()

                st.subheader("Ответ")
                st.write(result["answer"])

                st.subheader("Источники")
                for source in result["sources"]:
                    with st.expander(
                        f"Страница {source['page']} | score={source['score']:.3f}"
                    ):
                        st.write(source["text"])
            else:
                st.error(response.text)
import streamlit as st
import requests

st.title("AI Scrap Bot Query UI")

API_URL = "http://localhost:8000/query"

st.markdown("Ask a question based on your crawled knowledge base:")

question = st.text_input("Your question:")

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Getting answer..."):
            response = requests.post(
                API_URL,
                json={"question": question}
            )
            if response.status_code == 200:
                data = response.json()
                st.success(data["answer"])
                if data["sources"]:
                    st.markdown("**Sources:**")
                    for src in data["sources"]:
                        st.write(src)
                else:
                    st.info("No sources returned.")
            else:
                st.error(f"Error: {response.text}")
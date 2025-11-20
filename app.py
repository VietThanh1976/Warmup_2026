import streamlit as st

st.write('Hello')
st.write(55)
st.divider()
file = st.file_uploader(
  "Upload your file",
  type=["pdf", "docx", "wav"]
)
if file:
  st.write(f"{file}")

import streamlit as st
from app.services.knowledge_base import KnowledgeBaseService

st.title("知识库更新服务")

uploader = st.file_uploader(
    "请上传TXT文件",
    type=['txt'],
    accept_multiple_files=False,
)

if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if uploader is not None:
    file_name = uploader.name
    file_type = uploader.type
    file_size = uploader.size / 1024  #KB

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | 大小：{file_size:2f} KB")

    #get value -> bytes need ->decode('utf-8')
    text = uploader.getvalue().decode("utf-8")

    with st.spinner("载入知识库中..."):
        result = st.session_state["service"].embedding_file(text,file_name)
        st.write(result)

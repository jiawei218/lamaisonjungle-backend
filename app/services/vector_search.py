from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings
from app.services.knowledge_base import project_path


class VectorSearchService(object):
    def __init__(self):
        self.vector_store = Chroma(
            collection_name= settings.chroma_collection_name,  #数据库表名
            embedding_function=OpenAIEmbeddings(
                model=settings.chroma_embedding_model,
                api_key=settings.dashscope_api_key,
                base_url=settings.dashscope_base_url,
                check_embedding_ctx_length=False,
                chunk_size=10,
            ),
            persist_directory=str(project_path(settings.chroma_persist_directory)), #本地存储路径
        )

    def get_retriever(self):
        """返回向量检索器"""
        return self.vector_store.as_retriever(search_kwargs={"k":settings.search_kwargs })

if __name__ == '__main__':
    retriever = VectorSearchService().get_retriever()
    res = retriever.invoke("公司售卖哪些植物？")
    print(res)
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.services.vector_search import VectorSearchService

def print_propmt(prompt):
    print("*"*20)
    print(prompt.to_string())
    print("*" * 20)
    return prompt


def format_document(docs: list[Document]):
    if not docs:
        return "无相关参考资料"
    formatted_str = ""
    for doc in docs:
        formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
    return formatted_str

class RAGService(object):

    def __init__(self):
        self.vector_service = VectorSearchService()
        self.prompt_template = ChatPromptTemplate(
            [
                ("system","以我提供的已知参考资料为主，"
                 "简洁并专业地回答用户问题。参考资料：{context}"),
                ("human","请回答用户问题：{input}"),
            ]
        )

        self.chat_model = ChatOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
            model=settings.dashscope_model,
        )
        self.chain = self.__get_chain()

    def __get_chain(self):
        retriever = self.vector_service.get_retriever()

        chain = (
            {
                "input":RunnablePassthrough(),
                "context": retriever | format_document
            } | self.prompt_template | print_propmt | self.chat_model | StrOutputParser()
        )

        return chain

if __name__ == '__main__':
    rag = RAGService()
    print(rag.chain.invoke("公司售卖物"))
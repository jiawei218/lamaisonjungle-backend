from pathlib import Path
from app.core.config import settings
import hashlib
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str) -> Path:
    configured_path = Path(path)
    if not configured_path.is_absolute():
        configured_path = PROJECT_ROOT / configured_path
    return configured_path.resolve()


def check_md5(md5_str:str):
    """检查传入的md5字符串是否已经被处理过了"""
    md5_file = project_path(settings.path_md5_file)
    md5_file.parent.mkdir(parents=True, exist_ok=True)
    if not md5_file.exists():
        md5_file.touch()
        return False
    else:
        for line in md5_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line == md5_str:
                return True

        return False

def save_md5(md5_str:str):
    """将传入的md5字符串记录到文件内保存"""
    md5_file = project_path(settings.path_md5_file)
    md5_file.parent.mkdir(parents=True, exist_ok=True)
    with md5_file.open("a", encoding="utf-8") as f:
        f.write(md5_str + '\n')

def get_string_md5(input_str:str, encode = 'utf-8'):
    """将传入的字符串转换为md5字符串"""
    # 将字符串转化成bytes类型
    str_bytes = input_str.encode(encoding=encode)
    #创建md5对象
    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes)
    md5_hex = md5_obj.hexdigest()

    return md5_hex


class KnowledgeBaseService(object):
    def __init__(self):
        # 确保地址存在，不存在就先新建
        chroma_directory = project_path(settings.chroma_persist_directory)
        chroma_directory.mkdir(parents=True, exist_ok=True)
        self.chroma = Chroma(
            collection_name= settings.chroma_collection_name,  #数据库表名
            embedding_function=OpenAIEmbeddings(
                model=settings.chroma_embedding_model,
                api_key=settings.dashscope_api_key,
                base_url=settings.dashscope_base_url,
                check_embedding_ctx_length=False,
                chunk_size=10,
            ),
            persist_directory=str(chroma_directory), #本地存储路径
        )  #向量存储的实例 Chroma向量库对象
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size= settings.chunk_size,
            chunk_overlap= settings.chunk_overlap,
            separators=settings.separators,
            length_function=len,        ) #文本分割器的对象

    def embedding_file(self,data, filename):
        """将传入的字符串进行向量化，存入向量数据库"""
        #先拿到md5值
        md5_hex = get_string_md5(data)

        #判断是否已处理
        if check_md5(md5_hex):
            return "[跳过]内容已经存在知识库中"

        metadata = {
            "source":filename,
            "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        if len(data) > settings.max_spliter_char_number:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]

        self.chroma.add_texts(
            knowledge_chunks,
            metadatas= [metadata for _ in knowledge_chunks]
        )

        save_md5(md5_hex)
        return "[成功]内容已经成功载入向量库"


if __name__ == '__main__':
    service = KnowledgeBaseService()
    r=service.embedding_file("La Mainson Jungle是由coco女士创建的一家网店","testfile")
    print(r)

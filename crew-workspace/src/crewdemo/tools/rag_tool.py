import os
from dotenv import load_dotenv
from chromadb.config import Settings
from crewai_tools import TXTSearchTool, CSVSearchTool


# 加载环境变量
load_dotenv()

# tools = CSVSearchTool(
tools = TXTSearchTool(
    config={
        "embedding_model": {
            "provider": "openai",
            "config": {
                "model": "text-embedding-005",
                # "task_type": "RETRIEVAL_DOCUMENT",
                # "api_key": os.getenv("GOOGLE_API_KEY"),
            },
        },
        # "vectordb": {
        #     "provider": "chroma",
        #     "config": {
        #         "settings": Settings(
        #             persist_directory="../chroma",
        #             allow_reset=True,
        #             is_persistent=True,
        #         ),
        #     },
        # },
    }
)


result = tools.run(
    # "../docs/converted.csv",
    "../docs/converted.txt",
    search_query="Please summarize the content of the file.",
)

print("result:", result)

from crewai.task import Task


import os
import yaml
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from tools.custom_tool import FileReadTool
from tools.custom_tool import FileTools

# 加载环境变量
load_dotenv()

# --- 1. 初始化模型和工具 (这些是运行时对象，保留在 Python 中) ---
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", api_key=os.getenv("GOOGLE_API_KEY"))
llm = ChatOpenAI(
    model="deepseek-chat",  # DeepSeek 模型名称
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0.7,  # 可选：控制创造性
    max_tokens=4096,  # 可选：最大输出长度
)
file_read_tool = FileReadTool(file_path="../docs/requirements.md")
write_file_tool = FileTools.write_file

# --- 2. 从 YAML 加载配置 ---
with open("./config/agents.yaml", "r", encoding="utf-8") as file:
    agent = yaml.safe_load(file)

with open("./config/tasks.yaml", "r", encoding="utf-8") as file:
    task = yaml.safe_load(file)

agent_configs = agent["agents"]
task_configs = task["tasks"]

# --- 3. 动态创建 Agent ---
agents = {}
for name, agent_config in agent_configs.items():
    # 为特定的 agent 分配工具
    agent_tools = []
    if name == "planner":
        agent_tools.append(file_read_tool)
    else:  # 其他 agent 都使用写文件工具
        agent_tools.append(write_file_tool)

    if name == "frontend_dev":
        agent_tools.append(file_read_tool)

    agents[name] = Agent(
        llm=llm,
        tools=agent_tools,
        **agent_config,  # 使用 YAML 中的配置
    )

# --- 4. 动态创建 Task ---
tasks = {}
for name, task_config in task_configs.items():
    # 解析 context，将其从 task key 字符串转换为实际的 Task 对象
    context_tasks = []
    if task_config.get("context"):
        for context_task_name in task_config["context"]:
            context_tasks.append(tasks[context_task_name])

    tasks[name] = Task(
        agent=agents[task_config["agent"]],  # 关联 Agent 对象
        context=context_tasks,
        **{
            k: v for k, v in task_config.items() if k not in ["agent", "context"]
        },  # 传入其他配置
    )

# --- 5. 组建并运行 Crew ---
project_crew = Crew(
    agents=list[Agent](agents.values()),
    tasks=list[Task](tasks.values()),
    process=Process.sequential,
    verbose=2,
)

if __name__ == "__main__":
    print("🚀 Starting the AI Development Team from YAML configuration...")
    result = project_crew.kickoff()
    print("\n\n✅ CrewAI has finished generating the project files.")
    print("Final result from the crew:", result)

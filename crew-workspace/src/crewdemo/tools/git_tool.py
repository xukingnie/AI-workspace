from crewai_tools import Tool
from tools.git_tools import GitTools  # 假设你将GitTools保存在tools/git_tools.py

# 初始化GitTools，指向你的项目根目录
git_tool_instance = GitTools("./your_project_root")  # 替换为实际项目路径

git_create_branch_tool = Tool(
    name="Git_Create_Branch",
    func=git_tool_instance.create_branch,
    description="Creates and checks out a new Git branch. Input: branch_name (string).",
)

git_checkout_branch_tool = Tool(
    name="Git_Checkout_Branch",
    func=git_tool_instance.checkout_branch,
    description="Checks out an existing Git branch. Input: branch_name (string).",
)

git_add_files_tool = Tool(
    name="Git_Add_Files",
    func=git_tool_instance.add_files,
    description="Adds specified files (or patterns like ['*']) to the Git staging area. Input: file_paths (list of strings).",
)

git_commit_changes_tool = Tool(
    name="Git_Commit_Changes",
    func=git_tool_instance.commit_changes,
    description="Commits staged changes with a given message. Input: message (string).",
)

git_push_branch_tool = Tool(
    name="Git_Push_Branch",
    func=git_tool_instance.push_branch,
    description="Pushes the current branch to the remote. Input: remote_name (string, default 'origin'), branch_name (string, default current branch).",
)

git_get_status_tool = Tool(
    name="Git_Get_Status",
    func=git_tool_instance.get_status,
    description="Returns the current Git status (untracked, modified, staged files).",
)

git_get_diff_tool = Tool(
    name="Git_Get_Diff",
    func=git_tool_instance.get_diff,
    description="Returns the diff of staged and unstaged changes.",
)

git_merge_branch_tool = Tool(
    name="Git_Merge_Branch",
    func=git_tool_instance.merge_branch,
    description="Merges a source branch into a target branch (which will be checked out first). Input: source_branch (string), target_branch (string), message (string).",
)

# 将这些工具传递给 GitManagerAgent
git_manager_agent_tools = [
    git_create_branch_tool,
    git_checkout_branch_tool,
    git_add_files_tool,
    git_commit_changes_tool,
    git_push_branch_tool,
    git_get_status_tool,
    git_get_diff_tool,
    git_merge_branch_tool,
]

from langchain.tools import tool
from crewai_tools import BaseTool
import os
import chardet
from pydantic import Field

class FileTools:
    @tool("Write File Tool")
    def write_file(file_path: str, content: str) -> str:
        """
        Writes content to a specified file. 
        It will create necessary directories if they don't exist.
        The file_path should be relative to the project's root directory.
        Example: 'backend/src/main/java/com/example/Main.java'
        """
        # The script runs from /crew, so we need to go up one level to the project root.
        project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        full_path = os.path.join(project_root_path, file_path)
        
        try:
            # Security check: ensure we are not writing outside the project
            if not os.path.abspath(full_path).startswith(project_root_path):
                return f"Error: Attempted to write outside of the project directory. Path: {file_path}"

            dir_name = os.path.dirname(full_path)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote content to {file_path}"
        except Exception as e:
            return f"Error writing to file {file_path}: {e}"



class FileReadTool(BaseTool):
    """智能文件读取工具，自动检测编码"""
    
    name: str = "Smart File Read Tool"
    description: str = "读取文件内容，自动处理各种编码格式（UTF-8、GBK、GB2312等）"
    file_path: str = Field(description="要读取的文件路径")
    
    def __init__(self, file_path: str):
        super().__init__(file_path=file_path)
        self.file_path = file_path
    
    def _detect_encoding(self) -> str:
        """检测文件编码"""
        try:
            with open(self.file_path, 'rb') as f:
                raw_data = f.read()
                # 如果文件太大，只读取前 10000 字节检测
                if len(raw_data) > 10000:
                    raw_data = raw_data[:10000]
                result = chardet.detect(raw_data)
                encoding = result['encoding'] if result['encoding'] else 'utf-8'
                confidence = result['confidence']
                print(f"检测到编码: {encoding} (置信度: {confidence:.2%})")
                return encoding
        except Exception as e:
            print(f"编码检测失败: {e}")
            return 'utf-8'
    
    def _read_with_encodings(self) -> str:
        """尝试多种编码读取文件"""
        # 常见编码列表
        encodings = [
            'utf-8',
            'gbk', 
            'gb2312',
            'gb18030',
            'big5',
            'utf-16',
            'latin-1',
            'ascii'
        ]
        
        # 先尝试检测编码
        detected_enc = self._detect_encoding()
        if detected_enc not in encodings:
            encodings.insert(0, detected_enc)
        
        # 尝试各种编码
        for encoding in encodings:
            try:
                with open(self.file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    print(f"✅ 成功使用 {encoding} 编码读取文件")
                    return content
            except (UnicodeDecodeError, LookupError):
                continue
            except Exception as e:
                print(f"使用 {encoding} 读取时出错: {e}")
                continue
        
        # 如果都失败，使用 errors='ignore' 忽略错误字符
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                print("⚠️ 使用 utf-8 (忽略错误) 读取文件")
                return content
        except Exception as e:
            raise Exception(f"无法读取文件 {self.file_path}: {e}")
    
    def _run(self) -> str:
        """CrewAI 工具需要的方法"""
        if not os.path.exists(self.file_path):
            return f"错误: 文件不存在 - {self.file_path}"
        
        try:
            content = self._read_with_encodings()
            return content
        except Exception as e:
            return f"读取文件失败: {str(e)}"
    
    async def _arun(self) -> str:
        """异步版本"""
        return self._run()
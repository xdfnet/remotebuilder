"""
cx_Freeze 构建器
实现基于 cx_Freeze 的构建逻辑
"""
import os
import sys
import shutil
import subprocess
from typing import Dict, Any, List
from .base import BaseBuilder, BuildError, BuildStatus

class CxFreezeBuilder(BaseBuilder):
    """cx_Freeze 构建器"""
    
    def __init__(self):
        super().__init__()
        self.supported_platforms = ["windows", "linux", "macos"]
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证构建配置"""
        required_fields = ["name", "version", "entry_script"]
        for field in required_fields:
            if field not in config:
                self.log_error(f"Missing required field: {field}")
                return False
        return True
        
    def prepare_environment(self, workspace: str) -> bool:
        """准备构建环境"""
        try:
            self.status = BuildStatus.PREPARING
            self.update_progress(10)
            
            # 检查 cx_Freeze 是否已安装
            try:
                import cx_Freeze
            except ImportError:
                self.log_output("Installing cx_Freeze...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "cx_Freeze"])
                
            # 创建构建目录
            build_dir = os.path.join(workspace, "build")
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
            os.makedirs(build_dir)
            
            self.update_progress(30)
            return True
            
        except Exception as e:
            self.fail(f"Failed to prepare environment: {str(e)}")
            return False
            
    def build(self, entry_script: str, config: Dict[str, Any]) -> bool:
        """执行构建"""
        try:
            self.status = BuildStatus.BUILDING
            self.update_progress(40)
            
            # 创建 setup.py
            setup_script = self._generate_setup_script(entry_script, config)
            setup_path = os.path.join(os.path.dirname(entry_script), "setup.py")
            with open(setup_path, "w") as f:
                f.write(setup_script)
                
            self.update_progress(60)
            
            # 执行构建
            self.log_output("Building with cx_Freeze...")
            subprocess.check_call([
                sys.executable,
                setup_path,
                "build"
            ])
            
            self.update_progress(80)
            return True
            
        except Exception as e:
            self.fail(f"Build failed: {str(e)}")
            return False
            
    def package(self, output_dir: str) -> bool:
        """打包"""
        try:
            self.status = BuildStatus.PACKAGING
            self.update_progress(90)
            
            # 移动构建结果到输出目录
            build_dir = os.path.join(os.path.dirname(self.current_task.entry_script), "build")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            for item in os.listdir(build_dir):
                src = os.path.join(build_dir, item)
                dst = os.path.join(output_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                    
            self.update_progress(100)
            return True
            
        except Exception as e:
            self.fail(f"Packaging failed: {str(e)}")
            return False
            
    def cleanup(self) -> bool:
        """清理"""
        try:
            self.status = BuildStatus.CLEANING
            
            # 删除临时文件
            build_dir = os.path.join(os.path.dirname(self.current_task.entry_script), "build")
            setup_path = os.path.join(os.path.dirname(self.current_task.entry_script), "setup.py")
            
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
            if os.path.exists(setup_path):
                os.remove(setup_path)
                
            return True
            
        except Exception as e:
            self.log_error(f"Cleanup failed: {str(e)}")
            return False
            
    def _generate_setup_script(self, entry_script: str, config: Dict[str, Any]) -> str:
        """生成 setup.py 脚本"""
        script = f"""
import sys
from cx_Freeze import setup, Executable

build_exe_options = {{
    "packages": [],
    "excludes": [],
    "include_files": []
}}

# 处理额外数据文件
if "extra_data" in {config}:
    build_exe_options["include_files"].extend({config}.get("extra_data", []))
    
# 处理依赖
if "requirements" in {config}:
    with open({config}["requirements"]) as f:
        packages = [line.strip() for line in f if line.strip()]
    build_exe_options["packages"].extend(packages)
    
base = None
if sys.platform == "win32":
    base = "Win32GUI" if not {config}.get("console", False) else "Console"

setup(
    name = "{config['name']}",
    version = "{config['version']}",
    description = "{config.get('description', '')}",
    options = {{"build_exe": build_exe_options}},
    executables = [
        Executable(
            "{entry_script}",
            base=base,
            target_name="{config['name']}",
            icon="{config.get('icon', '')}"
        )
    ]
)
"""
        return script 
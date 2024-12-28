"""
py2app 构建器
实现基于 py2app 的构建逻辑
"""
import os
import sys
import shutil
import subprocess
from typing import Dict, Any, List
from .base import BaseBuilder, BuildError, BuildStatus

class Py2AppBuilder(BaseBuilder):
    """py2app 构建器"""
    
    def __init__(self):
        super().__init__()
        self.supported_platforms = ["macos"]
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证构建配置"""
        if sys.platform != "darwin":
            self.log_error("py2app only supports macOS platform")
            return False
            
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
            
            # 检查 py2app 是否已安装
            try:
                import py2app
            except ImportError:
                self.log_output("Installing py2app...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "py2app"])
                
            # 创建构建目录
            build_dir = os.path.join(workspace, "build")
            dist_dir = os.path.join(workspace, "dist")
            
            for dir_path in [build_dir, dist_dir]:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                os.makedirs(dir_path)
                
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
            self.log_output("Building with py2app...")
            subprocess.check_call([
                sys.executable,
                setup_path,
                "py2app"
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
            dist_dir = os.path.join(os.path.dirname(self.current_task.entry_script), "dist")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            for item in os.listdir(dist_dir):
                src = os.path.join(dist_dir, item)
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
            dist_dir = os.path.join(os.path.dirname(self.current_task.entry_script), "dist")
            setup_path = os.path.join(os.path.dirname(self.current_task.entry_script), "setup.py")
            
            for path in [build_dir, dist_dir]:
                if os.path.exists(path):
                    shutil.rmtree(path)
                    
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
from setuptools import setup

# 处理依赖
packages = []
if "requirements" in {config}:
    with open({config}["requirements"]) as f:
        packages = [line.strip() for line in f if line.strip()]
        
# 处理数据文件
data_files = []
if "extra_data" in {config}:
    data_files.extend({config}.get("extra_data", []))
    
APP = ["{entry_script}"]
DATA_FILES = data_files
OPTIONS = {{
    "argv_emulation": True,
    "packages": packages,
    "includes": [],
    "excludes": [],
    "iconfile": "{config.get('icon', '')}",
    "plist": {{
        "CFBundleName": "{config['name']}",
        "CFBundleDisplayName": "{config['name']}",
        "CFBundleVersion": "{config['version']}",
        "CFBundleShortVersionString": "{config['version']}",
        "LSBackgroundOnly": {str(not config.get('console', False)).lower()}
    }}
}}

setup(
    name="{config['name']}",
    version="{config['version']}",
    description="{config.get('description', '')}",
    app=APP,
    data_files=DATA_FILES,
    options={{"py2app": OPTIONS}},
    setup_requires=["py2app"]
)
"""
        return script 
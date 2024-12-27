"""
PyInstaller 打包实现
"""
import os
import logging
from typing import Dict, Any
from .base import BaseBuilder, BuildResult

logger = logging.getLogger(__name__)

class PyInstallerBuilder(BaseBuilder):
    """PyInstaller 打包器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.result = BuildResult()
        
    def prepare(self) -> bool:
        """准备打包环境"""
        try:
            # 清理旧的构建文件
            os.system("rm -rf build dist *.spec")
            return True
        except Exception as e:
            logger.error(f"准备环境失败: {str(e)}")
            return False
            
    def build(self, entry_script: str, output_dir: str) -> bool:
        """执行打包"""
        try:
            cmd_parts = [
                "pyinstaller",
                "--clean",
                "--windowed",
                "--onedir",
                f"--name '{self.config.get('name', 'app')}'",
                "--noconfirm"
            ]
            
            # 添加图标
            if icon := self.config.get('icon'):
                cmd_parts.append(f"--icon '{icon}'")
                
            # 添加额外数据文件
            if data_files := self.config.get('data_files'):
                for src, dst in data_files.items():
                    cmd_parts.append(f"--add-data '{src}:{dst}'")
                    
            # 添加排除模块
            if exclude_modules := self.config.get('exclude_modules'):
                for module in exclude_modules:
                    cmd_parts.append(f"--exclude-module {module}")
                    
            # 添加平台特定选项
            if self.config.get('platform') == 'macos':
                cmd_parts.append("--osx-bundle-identifier 'com.example.app'")
                
            # 添加入口脚本
            cmd_parts.append(entry_script)
            
            # 执行命令
            cmd = " ".join(cmd_parts)
            logger.info(f"执行打包命令: {cmd}")
            
            if os.system(cmd) != 0:
                logger.error("打包命令执行失败")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"打包失败: {str(e)}")
            return False
            
    def verify(self, output_path: str) -> bool:
        """验证打包结果"""
        try:
            if not os.path.exists(output_path):
                logger.error(f"输出文件不存在: {output_path}")
                return False
                
            # TODO: 添加更多验证
            return True
            
        except Exception as e:
            logger.error(f"验证失败: {str(e)}")
            return False
            
    def cleanup(self) -> None:
        """清理临时文件"""
        try:
            os.system("rm -rf build *.spec")
        except Exception as e:
            logger.warning(f"清理失败: {str(e)}") 
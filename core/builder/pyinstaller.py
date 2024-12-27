"""
PyInstaller 打包器实现
"""
import os
import logging
from typing import List, Optional
from .base import BaseBuilder
from ..server.manager import BuildTask

logger = logging.getLogger(__name__)

class PyInstallerBuilder(BaseBuilder):
    """PyInstaller 打包器"""
    
    def build(self, task: BuildTask) -> bool:
        """
        执行打包
        
        Args:
            task: 打包任务
            
        Returns:
            bool: 是否打包成功
        """
        try:
            # 检查 PyInstaller
            if not self._check_pyinstaller(task):
                return False
                
            # 准备打包命令
            cmd = self._build_command(task)
            if not cmd:
                return False
                
            # 执行打包
            logger.info(f"正在执行打包命令: {cmd}")
            stdout, stderr = task.server.execute_command(cmd)
            
            if stderr:
                logger.error(f"打包失败: {stderr}")
                task.error = stderr
                return False
                
            # 检查打包结果
            if not self._check_output(task):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"打包失败: {str(e)}")
            task.error = str(e)
            return False
            
    def _check_pyinstaller(self, task: BuildTask) -> bool:
        """
        检查 PyInstaller 是否已安装
        
        Args:
            task: 打包任务
            
        Returns:
            bool: 是否已安装
        """
        try:
            stdout, stderr = task.server.execute_command("pip show pyinstaller")
            if stderr or "Version:" not in stdout:
                # 安装 PyInstaller
                logger.info("正在安装 PyInstaller")
                stdout, stderr = task.server.execute_command(
                    "pip install pyinstaller"
                )
                if stderr:
                    logger.error(f"安装 PyInstaller 失败: {stderr}")
                    task.error = stderr
                    return False
            return True
            
        except Exception as e:
            logger.error(f"检查 PyInstaller 失败: {str(e)}")
            task.error = str(e)
            return False
            
    def _build_command(self, task: BuildTask) -> Optional[str]:
        """
        构建打包命令
        
        Args:
            task: 打包任务
            
        Returns:
            Optional[str]: 打包命令
        """
        try:
            # 基本命令
            cmd_parts: List[str] = [
                "cd /tmp/workspace_" + task.task_id,
                "&&",
                "pyinstaller"
            ]
            
            # 添加配置选项
            config = task.config.get('pyinstaller', {})
            
            # 是否打包为单文件
            if config.get('onefile', True):
                cmd_parts.append("--onefile")
                
            # 是否显示控制台
            if not config.get('console', True):
                cmd_parts.append("--noconsole")
                
            # 图标
            if icon := config.get('icon'):
                cmd_parts.extend(["--icon", icon])
                
            # 程序名称
            if name := config.get('name'):
                cmd_parts.extend(["--name", name])
                
            # 额外数据文件
            if datas := config.get('datas', []):
                for src, dst in datas:
                    cmd_parts.extend(["--add-data", f"{src}:{dst}"])
                    
            # 额外二进制文件
            if binaries := config.get('binaries', []):
                for src, dst in binaries:
                    cmd_parts.extend(["--add-binary", f"{src}:{dst}"])
                    
            # 隐藏导入
            if hidden_imports := config.get('hidden_imports', []):
                for module in hidden_imports:
                    cmd_parts.extend(["--hidden-import", module])
                    
            # 排除模块
            if excludes := config.get('excludes', []):
                for module in excludes:
                    cmd_parts.extend(["--exclude-module", module])
                    
            # 运行时钩子
            if runtime_hooks := config.get('runtime_hooks', []):
                for hook in runtime_hooks:
                    cmd_parts.extend(["--runtime-hook", hook])
                    
            # 额外参数
            if extra_args := config.get('extra_args', []):
                cmd_parts.extend(extra_args)
                
            # 入口脚本
            cmd_parts.append(task.entry_script)
            
            # 输出目录
            cmd_parts.extend([
                "&&",
                "cp -r dist/* /tmp/output_" + task.task_id
            ])
            
            return " ".join(cmd_parts)
            
        except Exception as e:
            logger.error(f"构建打包命令失败: {str(e)}")
            task.error = str(e)
            return None
            
    def _check_output(self, task: BuildTask) -> bool:
        """
        检查打包输出
        
        Args:
            task: 打包任务
            
        Returns:
            bool: 是否成功
        """
        try:
            # 检查输出目录是否存在
            stdout, stderr = task.server.execute_command(
                f"ls -l /tmp/output_{task.task_id}"
            )
            if stderr or not stdout.strip():
                logger.error("打包输出目录为空")
                task.error = "打包输出目录为空"
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"检查打包输出失败: {str(e)}")
            task.error = str(e)
            return False 
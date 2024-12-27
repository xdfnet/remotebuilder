import os
import logging
import paramiko
from typing import Dict, Any, Optional
from .core import retry_operation

logger = logging.getLogger(__name__)

class RemoteManager:
    def __init__(self, server_config: Dict[str, Any]):
        self.server_config = server_config
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect()
        self.sftp = self.ssh.open_sftp()
    
    @retry_operation()
    def connect(self) -> None:
        self.ssh.connect(**self.server_config)
    
    def create_remote_directory(self, remote_path: str) -> None:
        try:
            self.sftp.stat(remote_path)
        except FileNotFoundError:
            logger.debug(f"Creating remote directory: {remote_path}")
            self.sftp.mkdir(remote_path)
    
    def check_conda_env(self) -> bool:
        try:
            conda_path = self.server_config['conda']['path']
            conda_env = self.server_config['conda']['env']
            
            check_cmd = (
                'cmd.exe /c "'
                f'"{conda_path}\\Scripts\\activate.bat" {conda_env} && '
                'conda --version && '
                'python --version'
                '"'
            )
            
            output, error = self.execute_command(check_cmd)
            if error:
                logger.error(f"Conda environment check failed: {error}")
                return False
                
            logger.info(f"Conda environment check passed: {output}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to check conda environment: {str(e)}")
            return False

    def execute_command(self, command: str) -> tuple[str, str]:
        """执行远程命令"""
        stdin, stdout, stderr = self.ssh.exec_command(command)
        output = stdout.read().decode('gbk', errors='replace')
        error = stderr.read().decode('gbk', errors='replace')
        return output, error

    def clean_remote_directory(self, remote_path: str) -> bool:
        """清理远程目录"""
        try:
            clean_cmd = (
                'cmd.exe /c "'
                f'cd /d {remote_path} && '
                'del /F /S /Q /A *.* && '
                'for /D %i in (*) do rd /s /q "%i"'
                '"'
            )
            output, error = self.execute_command(clean_cmd)
            if error:
                logger.error(f"Failed to clean remote directory: {error}")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to clean remote directory: {str(e)}")
            return False

class PackageManager:
    def __init__(self, remote_manager: RemoteManager, config: Dict[str, Any], workspace_path: str):
        self.remote_manager = remote_manager
        self.config = config
        self.workspace_path = workspace_path
    
    def _clean_build_files(self) -> None:
        try:
            os.system("rm -rf build dist *.spec")
            logger.debug("Build files cleaned")
        except Exception as e:
            logger.warning(f"Failed to clean build files: {str(e)}")
    
    def verify_resources(self, config: Dict[str, Any]) -> bool:
        required_files = []
        
        icon = config.get('icon')
        if icon:
            required_files.append(icon)
            
        info_plist = config.get('info_plist')
        if info_plist:
            required_files.append(info_plist)
            
        for data in config.get('additional_data', []):
            src = data.split(':')[0]
            required_files.append(src)
            
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(self.workspace_path, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
                
        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            return False
            
        return True

    def build_windows(self, entry_script: str) -> bool:
        """构建Windows程序"""
        try:
            if not self.remote_manager.clean_remote_directory(self.remote_manager.server_config['remote_path']):
                return False

            # 上传文件
            # TODO: 实现文件上传逻辑

            # 执行打包
            pack_cmd = (
                'cmd.exe /c "'
                f'"{self.remote_manager.server_config["conda"]["path"]}\\Scripts\\activate.bat" '
                f'{self.remote_manager.server_config["conda"]["env"]} && '
                f'cd /d {self.remote_manager.server_config["remote_path"]} && '
                'pyinstaller --clean --windowed --onefile '
                '--name CourseForgeMini --icon images/app.ico '
                '--exclude-module PyQt5 main.py'
                '"'
            )
            output, error = self.remote_manager.execute_command(pack_cmd)
            if error:
                logger.error(f"Windows build failed: {error}")
                return False

            return True
        except Exception as e:
            logger.error(f"Windows build failed: {str(e)}")
            return False

    @staticmethod
    def build_mac_package(entry_script: str, workspace_path: str) -> bool:
        """构建Mac程序"""
        try:
            os.chdir(workspace_path)
            os.system("rm -rf build dist *.spec")
            
            cmd = (
                "pyinstaller "
                "--clean "
                "--windowed "
                "--onedir "
                "--name 'CourseForgeMini' "
                "--noupx "
                "--noconfirm "
                "--osx-bundle-identifier 'com.courseforge.pro' "
                f"{entry_script}"
            )
            
            if os.system(cmd) != 0:
                return False
                
            mac_app_path = os.path.join(workspace_path, "dist", "CourseForgeMini.app")
            if not os.path.exists(mac_app_path):
                return False
                
            os.system(f"chmod -R 755 '{mac_app_path}'")
            os.system(f"xattr -cr '{mac_app_path}'")
            return True
            
        except Exception as e:
            logger.error(f"Mac build failed: {str(e)}")
            return False 
"""
Unix 远程服务器实现
"""
import os
import logging
import paramiko
from typing import Dict, Any, Tuple
from .base import BaseServer, ServerStatus

logger = logging.getLogger(__name__)

class UnixServer(BaseServer):
    """Unix 服务器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.ssh: paramiko.SSHClient = None
        self.sftp: paramiko.SFTPClient = None
        
    def connect(self) -> bool:
        """连接到服务器"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接参数
            connect_params = {
                'hostname': self.config['host'],
                'username': self.config['username'],
                'timeout': self.config.get('timeout', 30)
            }
            
            # 添加密码或密钥认证
            if 'password' in self.config:
                connect_params['password'] = self.config['password']
            elif 'key_file' in self.config:
                connect_params['key_filename'] = os.path.expanduser(self.config['key_file'])
                
            self.ssh.connect(**connect_params)
            self.sftp = self.ssh.open_sftp()
            self.status.connected = True
            return True
            
        except Exception as e:
            logger.error(f"连接失败: {str(e)}")
            self.status.connected = False
            return False
            
    def disconnect(self) -> None:
        """断开连接"""
        try:
            if self.sftp:
                self.sftp.close()
            if self.ssh:
                self.ssh.close()
        except Exception as e:
            logger.error(f"断开连接失败: {str(e)}")
        finally:
            self.status.connected = False
            
    def check_health(self) -> ServerStatus:
        """检查服务器健康状态"""
        try:
            # 检查 CPU 使用率
            stdout, _ = self.execute_command(
                "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'"
            )
            self.status.cpu_usage = float(stdout.strip())
            
            # 检查内存使用率
            stdout, _ = self.execute_command(
                "free | grep Mem | awk '{print $3/$2 * 100}'"
            )
            self.status.memory_usage = float(stdout.strip())
            
            # 检查磁盘使用率
            stdout, _ = self.execute_command(
                "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"
            )
            self.status.disk_usage = float(stdout.strip())
            
            # 检查 Python 版本
            if python_version := self.check_python():
                self.status.python_version = python_version
                
            return self.status
            
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            self.status.errors.append(str(e))
            return self.status
            
    def execute_command(self, command: str) -> Tuple[str, str]:
        """执行命令"""
        if not self.ssh:
            raise RuntimeError("未连接到服务器")
            
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return (
            stdout.read().decode('utf-8'),
            stderr.read().decode('utf-8')
        )
        
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """上传文件"""
        try:
            if not self.sftp:
                raise RuntimeError("未连接到服务器")
                
            self.sftp.put(local_path, remote_path)
            return True
        except Exception as e:
            logger.error(f"上传文件失败: {str(e)}")
            return False
            
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """下载文件"""
        try:
            if not self.sftp:
                raise RuntimeError("未连接到服务器")
                
            self.sftp.get(remote_path, local_path)
            return True
        except Exception as e:
            logger.error(f"下载文件失败: {str(e)}")
            return False
            
    def create_directory(self, path: str) -> bool:
        """创建目录"""
        try:
            if not self.sftp:
                raise RuntimeError("未连接到服务器")
                
            self.sftp.mkdir(path)
            return True
        except Exception as e:
            logger.error(f"创建目录失败: {str(e)}")
            return False
            
    def remove_directory(self, path: str) -> bool:
        """删除目录"""
        try:
            stdout, stderr = self.execute_command(f'rm -rf "{path}"')
            if stderr:
                logger.error(f"删除目录失败: {stderr}")
                return False
            return True
        except Exception as e:
            logger.error(f"删除目录失败: {str(e)}")
            return False 
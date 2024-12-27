"""
RemoteBuilder 核心模块
"""

__version__ = '1.0.0'
__author__ = 'Your Name'
__email__ = 'your.email@example.com'
__description__ = 'Remote Cross-Platform Python Application Builder'
__url__ = 'https://github.com/yourusername/remotebuilder'
__license__ = 'MIT'

def get_version() -> str:
    """获取版本号"""
    return __version__

def get_logo() -> str:
    """获取 logo"""
    try:
        with open('docs/logo.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return f"RemoteBuilder v{__version__}" 
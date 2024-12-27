"""
错误重试装饰器
"""
import logging
import time
import functools
from typing import Type, Tuple, Optional, Callable, Any

logger = logging.getLogger(__name__)

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    should_retry: Optional[Callable[[Exception], bool]] = None
) -> Callable:
    """
    错误重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟时间(秒)
        backoff: 延迟时间的增长倍数
        exceptions: 需要重试的异常类型
        should_retry: 自定义重试判断函数
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    
                    # 检查是否需要重试
                    if should_retry and not should_retry(e):
                        raise
                        
                    # 最后一次尝试失败,直接抛出异常
                    if attempt == max_attempts:
                        raise
                        
                    # 记录重试信息
                    logger.warning(
                        f"执行 {func.__name__} 失败 ({str(e)}), "
                        f"将在 {current_delay:.1f} 秒后进行第 {attempt + 1} 次重试"
                    )
                    
                    # 等待后重试
                    time.sleep(current_delay)
                    current_delay *= backoff
                    
        return wrapper
    return decorator
    
def should_retry_on_connection(e: Exception) -> bool:
    """
    判断连接相关错误是否需要重试
    
    Args:
        e: 异常实例
        
    Returns:
        bool: 是否需要重试
    """
    error_msg = str(e).lower()
    
    # 网络连接错误
    if any(msg in error_msg for msg in [
        'connection refused',
        'connection reset',
        'connection timed out',
        'no route to host',
        'network is unreachable'
    ]):
        return True
        
    # SSH 连接错误
    if any(msg in error_msg for msg in [
        'ssh exception',
        'authentication failed',
        'channel closed',
        'session closed'
    ]):
        return True
        
    # 其他可重试的错误
    if any(msg in error_msg for msg in [
        'temporary failure',
        'timeout',
        'too many connections'
    ]):
        return True
        
    return False 
from functools import wraps
import time
from datetime import datetime


def time_formatting(target):
    """
    递归将对象中所有为时间戳的值转化为格式化时间
    支持python的float格式时间戳和Java的int格式时间戳
    Args:
        target: 支持 list, dict对象
    """
    if isinstance(target, list):
        return [time_formatting(curTarget) for curTarget in target if curTarget is not None]
    elif isinstance(target, dict):
        return {key:time_formatting(value) for key, value in target.items() if value is not None}
    if is_timestamp(target):
        return timestamp2formattedtime(float(target))
    return target

def timestamp2formattedtime(target):
    """
    将int或float格式的时间戳转化为格式化时间字符串
    """
    ok = target < 3733510181
    while not ok:
        target = target / 10
        ok = target < 3733510181
    dt = datetime.fromtimestamp(target)
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')

def is_timestamp(target):
    try:
        target = float(target)
        return 567993600 < target < 10000000000000
    except (ValueError, OverflowError):
        return False     
    return False


def timeFormatting():
    """
    【修饰器】将时间戳转化为格式化时间
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return time_formatting(result)
        return wrapper
    return decorator

if __name__ == '__main__':
    target = {'uTime': '1733510181123'}
    result = time_formatting(target)
    print(result)
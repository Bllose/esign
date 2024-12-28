from datetime import datetime

def formatter(timestamp:int) -> str:
    """
    格式化时间戳
    格式化显示细粒度到秒，超过秒的部分将被抹除
    Args:
        timestamp(int): 时间戳
    Returns:
        formatted(str): 格式化的时间字符串
    """
    while timestamp > 1e10:
        timestamp /= 10
    dt_object = datetime.fromtimestamp(timestamp)
    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time


if __name__ == '__main__':
    print(formatter(1735016363000))
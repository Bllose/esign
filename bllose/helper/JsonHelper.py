import json

def deep_clean_null(target) -> object:
    """
    深度清理json报文中值为null的字段
    """
    if isinstance(target, dict):
        return {k: deep_clean_null(v) for k, v in target.items() if v is not None}
    elif isinstance(target, list):
        return [deep_clean_null(item) for item in target if item is not None and len(item) > 0]
    else :
        return target
    
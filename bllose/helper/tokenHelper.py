from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
import base64
from typing import Final
from datetime import datetime, timedelta
import os
from pathlib import Path


PUBLIC_KEY: Final[str] = '''
LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUFxbHhUR3p4dlBBOWhnb3JtcHloaQpGVzE5NUp5M3RUaTVnY1FUYVUyYnRMaGNjSld6djhrOUNjV2lLQmlvOU8zQ0hlRzBNemJIRDBvSG5VaXNMZ1VkCmJVQ0pFcHRidWd4TFowQW1STkJoclNhbGNOVk95dkZ2MFBQWnFKUEZsYlZOREpIS0NSZ0NQNXhwbWV3YTRTWmUKbjRyVkRjTnhoUGRraUI3Z2ZUVVBjdHJsQjY2bmphTS9yWndYMVZHY0Q1RkpDajl5UTI1eXM5R0ZRZ3JuaXBxdQpzRkpjQk12RU00clNDQlVDbUZnbkZHOTBGSVFKUDNEaFcwY1Nmb2tqeThiblhJYzV3c3NMRW9tWXh5RW15aFgyCmZsVDRsMHA3TXRRYTZ3M3RTbm1laEpLeFhxNG9qLzRRTTJDQnN0Ym5TdHo3S3BRU1Z0WXNGZVpVWlMwKzNLR1AKK1FJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg==
'''.strip()


def generate_key_pair():
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # 导出私钥
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # 导出公钥
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem

def generate_token(private_key_pem, info_string):
    # 加载私钥
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,
        backend=default_backend()
    )
    
    # 使用私钥签名
    signature = private_key.sign(
        info_string.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # 将原始信息和签名一起编码
    combined = info_string.encode() + b"|" + signature
    return base64.b64encode(combined).decode('utf-8')

def verify_token(public_key_pem, token):
    try:
        # Base64解码
        decoded_data = base64.b64decode(token)
        
        # 分离原始信息和签名
        info_bytes, signature = decoded_data.split(b"|", 1)
        info_string = info_bytes.decode()
        
        # 加载公钥
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
        
        # 验证签名
        try:
            public_key.verify(
                signature,
                info_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # 验证通过后，解析信息
            parts = info_string.split(',')
            if len(parts) != 5:
                return False, "Invalid token format"
                
            company, name, phone, id_card, expire_date = parts
            if company != "BLLOSE":
                return False, "Invalid company"
                
            # 可以添加更多验证逻辑，如过期时间检查等
            
            return True, info_string
            
        except Exception:
            return False, "Invalid signature"
            
    except Exception as e:
        return False, f"Token verification failed: {str(e)}"

def load_private_key_from_file(public_key_path=None):
    """从多个位置尝试加载私钥文件
    
    搜索顺序:
    1. 传入的具体路径（如果提供）
    2. 当前运行目录
    3. 用户主目录
    4. 系统根目录
    
    Args:
        public_key_path: 可选的具体私钥文件路径
        
    Returns:
        bytes: 私钥文件内容
        
    Raises:
        Exception: 在所有位置都找不到私钥文件时抛出异常
    """
    DEFAULT_KEY_NAME = "private_key.pem"
    search_paths = []
    
    # 1. 添加指定路径（如果提供）
    if public_key_path:
        search_paths.append(Path(public_key_path))
    
    # 2. 添加当前运行目录
    search_paths.append(Path.cwd() / DEFAULT_KEY_NAME)
    
    # 3. 添加用户主目录
    search_paths.append(Path.home() / DEFAULT_KEY_NAME)
    
    # 4. 添加系统根目录
    for drive in ['C:', 'D:', 'E:', 'F:']:
        if os.path.exists(drive):
            search_paths.append(Path(drive) / DEFAULT_KEY_NAME)
    
    # 遍历所有可能的路径
    errors = []
    for path in search_paths:
        try:
            if path.exists():
                with open(path, 'rb') as f:
                    content = f.read()
                    print(f"成功从 {path} 加载私钥文件")
                    return content
        except Exception as e:
            errors.append(f"尝试从 {path} 加载失败: {str(e)}")
            continue
    
    # 如果所有路径都失败，抛出异常并包含详细错误信息
    error_msg = "\n".join(errors) if errors else "未找到私钥文件"
    raise Exception(f"无法加载私钥文件:\n{error_msg}")

def load_public_key(public_key_source):
    """加载公钥，支持Base64编码的字符串
    
    Args:
        public_key_source: Base64编码的公钥字符串
        
    Returns:
        bytes: 公钥内容
        
    Raises:
        Exception: 无法加载公钥时抛出异常
    """  
    try:
        # 直接Base64解码
        return base64.b64decode(public_key_source)
    except Exception as e:
        raise Exception(f"加载公钥失败: {str(e)}")

def public_key_to_base64(public_key_path):
    """将公钥文件转换为Base64编码字符串"""
    try:
        with open(public_key_path, 'rb') as f:
            content = f.read()
            # 直接对整个PEM内容进行base64编码
            return base64.b64encode(content).decode('utf-8')
    except Exception as e:
        raise Exception(f"转换公钥文件失败: {str(e)}")

def generate_token_with_expiry(private_key_pem, company, name, phone, id_card, days):
    """生成一个带有指定有效期的token
    
    Args:
        private_key_pem: 私钥PEM格式内容
        company: 公司名称
        name: 用户名
        phone: 电话号码
        id_card: 身份证号
        days: token有效期天数
        
    Returns:
        str: 生成的token
    """
    # 计算过期时间
    expire_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    # 构造信息字符串
    info_string = f"{company},{name},{phone},{id_card},{expire_date}"
    
    # 使用现有的generate_token函数生成token
    return generate_token(private_key_pem, info_string)


if __name__ == "__main__":
    # 生成密钥对
    # private_pem, public_pem = generate_key_pair()
    
    # # 保存密钥对（请在安全的地方保存私钥）
    # with open("private_key.pem", "wb") as f:
    #     f.write(private_pem)
    # with open("public_key.pem", "wb") as f:
    #     f.write(public_pem)
    # public_pem = load_public_key_from_file('public_key.pem')

    # 1. 首先将您的公钥文件转换为Base64字符串
    # base64_key = public_key_to_base64("public_key.pem")
    # print("请保存这个Base64字符串:")
    # print(base64_key)
    # public_pem = load_public_key(base64_key)
    private_pem = load_private_key_from_file('private_key.pem')

    # 1. 将公钥文件转换为Base64字符串
    # base64_key = public_key_to_base64("public_key.pem")
    # print("请保存这个Base64字符串:")
    # print(base64_key)
    
    # 2. 测试加载Base64字符串
    public_pem = load_public_key(PUBLIC_KEY)
    # print("\n解码后的PEM格式公钥:")
    # print(public_pem.decode('utf-8'))

    # 生成token
    # info_string = "BLLOSE,张三,13800138000,370725199001011990,20250101"
    # token = generate_token(private_pem, info_string)
    token = generate_token_with_expiry(private_pem, "BLLOSE", "张三", "13800138000", "370725199001011990", 1)
    print("生成的token:")
    print(token)
    
    # 验证token
    is_valid, result = verify_token(public_pem, token)
    print("\n验证结果:", "成功" if is_valid else "失败")
    # print("详细信息:", result)
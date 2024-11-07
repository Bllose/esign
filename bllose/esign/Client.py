"""
e签宝补救措施
1、通过模版创建文件
2、创建角色账号
3、通过文件获取盖章位置
4、通过“文件”，“账号”，“盖章位置”组装成一个发起签约的请求报文，获取流水号
5、通过“流水号”获取到签约地址
"""

from datetime import datetime, timezone  
from bllose.config.Config import class_config
import hashlib  
import base64
import hmac
import http.client
import io
import gzip
import logging
import json
import urllib

@class_config
class eqb_sign():
    def __init__(self, env:str = 'test', config = {}) -> None:
        # 通过配置加载工具加载的配置内容
        # 后续逻辑直接使用保存下载的config对象, 获取对应的配置项
        self.config = config
        self.env = env

        # 通过环境参数加载当前e签宝执行环境
        eqb = self.config['eqb'][env]

        self.header = {
            'X-Tsign-Open-App-Id': eqb['appId'],
            'X-Tsign-Open-Auth-Mode': 'Signature',
            'Host': eqb['host'],
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': '*/*',
            'Content-Type': 'application/json; charset=UTF-8',
            'Connection': 'keep-alive'
        }
        self.host = eqb['host']
        self.app_key = eqb['appKey']
        self.type = 'POST'
        

    def fetchUpdateFileUrl(self, contentMd5: str, fileName: str, fileSize: int) -> tuple:
        """
        申请上传合同文件
        获取最终上传文件的地址
        """
        current_url = r'/v3/files/file-upload-url'
        request_dict = {
                        "contentMd5": contentMd5,
                        "contentType": "application/octet-stream",
                        "fileName": fileName,
                        "fileSize": fileSize
                    }
        bodyRaw = json.dumps(request_dict)
        self.establish_head_code(bodyRaw, current_url)
        response_json = self.getResponseJson(bodyRaw, current_url)
        if response_json['code'] == 0:
            return str(response_json['data']['fileId']), str(response_json['data']['fileUploadUrl'])
        else:
            logging.warning(f'获取上传文件地址失败,返回报文: {json.dumps(response_json)}')
            return '', ''

    def uploadFile(self, putUrl: str, md5: str, absPath: str):
        """
        上传选中的文件
        PUT请求，单独处理
        @param putUrl: 由 #fetchUpdateFileUrl 调用e签宝返回的上传地址
        ```
        file_path = r'\to\your\file\path'
        fileName = r'your_file_name.pdf'
        absPath = file_path + os.sep + fileName

        file_stat = os.stat(absPath)  
        file_size = file_stat.st_size 

        md5 = get_file_content_md5(absPath)

        fileId, fileUploadUrl = client.fetchUpdateFileUrl(md5, fileName, file_size)
        print(f'md5: {md5}')
        print(f'fileId: {fileId}')
        print(fileUploadUrl)

        code, reason = client.uploadFile(fileUploadUrl, md5, absPath)
        if code != 200:
            print(f'上传失败! 失败原因{code}: {reason}')
        ```
        """
        with open(absPath, 'rb') as file:  
            file_content = file.read()  

        host = self.config['eqb'][self.env]['upload']['host']

        headers = {
            'Content-MD5': md5,
            'Content-Type': 'application/octet-stream',
            'Accept': '*/*',
            'Host': host,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Content-Length': len(file_content)
        }
        conn = http.client.HTTPSConnection(host)

        if putUrl.startswith('http'):
            # https:// 最后一个 / 所在位置是7， 所以从第8个位置开始找 /，就是找到路径开头的位置
            putUrl = putUrl[putUrl.find('/', 8):]
        conn.request('PUT', putUrl, body=file_content, headers=headers)
        response = conn.getresponse()
        return response.code, response.reason

    def fetchFileByFileId(self, fileId: str) -> tuple:
        """
        通过制作合同文件(#uploadFile)所得的fileId， 得到下载合同文件的下载地址
        """
        current_path = f'/v3/files/{fileId}'
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(None, current_path)
        if response_json['code'] != 0:
            logging.warning(f'下载文件{fileId}失败，返回报文:{json.dumps(response_json)}')
            return '', ''
        data = response_json['data']
        fileName = data['fileName']
        fileDownloadUrl = data['fileDownloadUrl']
        return fileName, fileDownloadUrl
    

    def fetchSignUrl(self, flowId, mobile):
        current_path = f'/v3/sign-flow/{flowId}/sign-url'
        request_dict = {
                        "needLogin": True,
                        "urlType": 2,
                        "operator": {
                            "psnAccount": mobile
                        }
                    }
        bodyRaw = json.dumps(request_dict)
        self.establish_head_code(bodyRaw, current_path)
        response_json = self.getResponseJson(bodyRaw, current_path)
        if response_json['code'] == 0:
            data = response_json['data']
            return data['shortUrl']

    def getAccountId(self, name, idNumber, mobile) -> str:
        """
        <h1>通过自然人三要素，获取其在e签宝的个人编号</h1>
        Args:
            name(str): 个人姓名
            idNumber(str): 个人身份证
            mobile(str): 个人电话
        Returns:
            accountId(str): 个人用户ID
        """
        current_path = r'/v1/accounts/createByThirdPartyUserId'
        request_dict = {
                            "thirdPartyUserId": idNumber,
                            "name": name,
                            "idType": "CRED_PSN_CH_IDCARD",
                            "idNumber": idNumber,
                            "mobile": mobile
                        }
        bodyRaw = json.dumps(request_dict)
        self.establish_head_code(bodyRaw, current_path)
        response_json = self.getResponseJson(bodyRaw, current_path)
        if response_json['code'] == 0:
            data = response_json['data']
            return data['accountId']
        elif response_json['code'] == 53000000:
            data = response_json['data']
            return data['accountId']
        
    def createFlowOneStep(self, bodyRaw: str) -> str:
        """
        e签宝，一步发起签约流程
        Args:
            bodyRaw(st): json请求报文的字符串
        Returns:
            flowId(str): 签约流水号
        """
        current_path = r'/api/v2/signflows/createFlowOneStep'
        self.establish_head_code(bodyRaw, current_path)
        response_json = self.getResponseJson(bodyRaw, current_path)
        if response_json['code'] == 0:
            data = response_json['data']
            return data['flowId']

        
    def getSignFlowDetail(self, signFlowId):
        """
        获取签署流程详情
        """
        current_path = f'/v3/sign-flow/{signFlowId}/detail'
        self.establish_head_code(None, current_path, 'GET')
        conn = http.client.HTTPSConnection(self.host)
        conn.request(method='GET', url=current_path, headers=self.header)
        response = conn.getresponse()
        # 检查是否需要解压  
        if response.getheader('Content-Encoding') == 'gzip':  
            # 使用gzip解压  
            compressed_data = response.read()  
            compressed_stream = io.BytesIO(compressed_data)  
            gzipper = gzip.GzipFile(fileobj=compressed_stream)  
            decoded_data = gzipper.read().decode('utf-8')  # 假设解压后的数据是utf-8编码  
        else:  
            # 直接解码  
            decoded_data = response.read().decode('utf-8')  

        logging.debug(decoded_data)
        response_json = json.loads(decoded_data)
        return response_json
    
    def createFileByTemplate(self, bodyRaw: str) -> tuple:
        """
        通过 template_id 和相关的合同要素，制作合同文件

        返回 tuple(fileId, downloadUrl)
        """
        current_path = r'/v1/files/createByTemplate'
        self.establish_head_code(bodyRaw, current_path)
        response_json = self.getResponseJson(bodyRaw=bodyRaw, current_path=current_path)
        if response_json['code'] == 0:
            data = response_json['data']
            return data['fileId'], data['downloadUrl']
    
    def createByDocTemplate(self, req) -> tuple:
        """
        模版制作文件接口
        @param req: 组装好的请求报文，包含 fileName, docTemplateId, components
        返回 fileId, fileDownloadUrl
        """
        current_path = r'/v3/files/create-by-doc-template'
        self.establish_head_code(req, current_path)
        response_json = self.getResponseJson(bodyRaw=req, current_path=current_path)
        if response_json['code'] == 0:
            data = response_json['data']
            return data['fileId'], data['fileDownloadUrl']
        
    def createByFile(self, req: str) -> str:
        """
        （精简版）基于文件发起签署
        """
        current_path = r'/v3/sign-flow/create-by-file'
        self.establish_head_code(req, current_path)
        response_json = self.getResponseJson(bodyRaw=req, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']['signFlowId']
        else:
            return ''
        
    def getH5Url(self, psnAccount: str, thirdFlowId: str) -> str:
        """
        通过账号和流水号获取签约地址
        Args:
            psnAccount(str): 用户在e签宝的登录账号，一般为移动电话号码
            thirdFlowId(str): 当前账号参与的签约流程ID
        Returns:
            shortUrl(str): 合同签署流程
        """
        req = {
                    "needLogin": True,
                    "urlType": 2,
                    "operator": {
                        "psnAccount": psnAccount
                    }
                }
        current_path = f'/v3/sign-flow/{thirdFlowId}/sign-url'
        bodyRaw = json.dumps(req, ensure_ascii=False)
        self.establish_head_code(bodyRaw, current_path)
        response_json = self.getResponseJson(bodyRaw=bodyRaw, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']['shortUrl']
        else:
            return ''

    def searchWordsPosition(self, fileId:str, keyword: str) -> list:
        """
        查询单个关键词位置
        直接返回这个关键词的所属位置列表
        否则返回空列表
        """
        query_string = urllib.parse.urlencode({'keywords': keyword})
        current_path = f'/v1/documents/{fileId}/searchWordsPosition?{query_string}'
        self.establish_head_code(None, current_path, 'GET')

        response_json = self.getResponseJson(bodyRaw=None, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data'][0]['positionList']
        else:
            logging.error(f'查询关键词位置失败,返回报文:{response_json}')
            return []

    def getOrganizationInfo(self, orgIdCard: str) -> dict:
        """
        通过社会统一信用代码
        获取项目公司在e签宝上的相关信息
        TODO 当前401，待解决
        """
        query_string = urllib.parse.urlencode({'orgIDCardType': 'CRED_ORG_USCC', 'orgIDCardNum': orgIdCard})
        current_path = f'/v3/organizations/identity-info?{query_string}'
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(bodyRaw=None, current_path=current_path)
        if response_json['code'] == 0:
            return response_json
        
    def fetchSealInfoByOrgId(self, orgId: str) -> list:
        """
        通过e签宝中注册的企业ID
        获取该企业下的印章ID信息
        若查询成功， 则返回印章信息列表
        否则返回空列表
        """
        current_path = f'/v1/organizations/{orgId}/seals'
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(bodyRaw=None, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']['seals']
        else:
            return []
        
    def getResponseJson(self, bodyRaw, current_path) -> json:
        """
        通过请求地址和请求参数
        获取返回报文
        """
        conn = http.client.HTTPSConnection(self.host)
        if bodyRaw is not None:
            bodyRaw = bodyRaw.encode("utf-8").decode("latin1")
        conn.request(self.type, current_path, bodyRaw, self.header)
        response = conn.getresponse()

        match response.code:
            case 403:
                logging.warning(f'拒绝访问!')
                return json.loads({'code': 999})
            case 401:
                logging.warning('未授权!')
                return json.loads({'code': 999})
            case 404:
                logging.warning(f'请求路径不存在!{current_path}')
                return json.loads({'code': 999})
            # case _:
                # logging.info(f'返回报文:{response}')


        # 检查是否需要解压  
        if response.getheader('Content-Encoding') == 'gzip':  
            # 使用gzip解压  
            compressed_data = response.read()  
            compressed_stream = io.BytesIO(compressed_data)  
            gzipper = gzip.GzipFile(fileobj=compressed_stream)  
            decoded_data = gzipper.read().decode('utf-8')  # 假设解压后的数据是utf-8编码  
        else:  
            # 直接解码  
            decoded_data = response.read().decode('utf-8')  

        logging.debug(decoded_data)
        response_json = json.loads(decoded_data)
        return response_json

    def establish_head_code(self, bodyRaw, pathAndQuery, method = 'POST'):
        """
        组装e签宝请求报文头中关键的几个编码
        """
        contentMd5 = ''
        if method == 'POST':
            contentMd5 = md5_base64_encode(bodyRaw)
            self.type = 'POST'
        elif method == 'GET':
            self.type = 'GET'
        else:
            logging.error(f"不支持的请求类型: {method}")
        self.header['Content-MD5'] = contentMd5
        accept = self.header['Accept']
        contentType = self.header['Content-Type']

        # 获取当前UTC时间 
        the_time = datetime.now(timezone.utc)
        date_format = the_time.strftime('%a, %d %b %Y %H:%M:%S GMT')  

        beforeSignature = method + '\n'\
                        + accept + '\n'\
                        + contentMd5 + '\n'\
                        + contentType + '\n'\
                        + date_format + '\n'\
                        + pathAndQuery
        signature = hmacSHA_base64_encode(self.app_key, beforeSignature)
        self.header['X-Tsign-Open-Ca-Signature'] = signature
        self.header['X-Tsign-Open-Ca-Timestamp'] = str(int(the_time.timestamp()*1000))
        self.header['Date'] = date_format

        # print("appKey: " + appKey)
        # print("beforeSignature: ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\n" + beforeSignature)
        # print("↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑")
        # print("signature: " + signature)
 
def hmacSHA_base64_encode(app_key, before_signature):
    # 将app_key转换为bytes，如果它是字符串的话  
    if isinstance(app_key, str):  
        app_key = app_key.encode('utf-8')  
    # 同样，如果before_signature是字符串，也转换为bytes  
    if isinstance(before_signature, str):  
        before_signature = before_signature.encode('utf-8')  
      
    # 使用hmac和sha256创建新的hmac对象  
    signature = hmac.new(app_key, before_signature, hashlib.sha256)  
      
    # 返回十六进制格式的哈希值  
    return base64.b64encode(signature.digest()).decode('utf-8')

def md5_base64_encode(body_raw):
    """
    将纯字符转化为MD5，然后再将MD5转化为Base64编码
    """
    # 计算 MD5 哈希  
    md5_hash = hashlib.md5(body_raw.encode('utf-8')).digest()  
    # 将 MD5 哈希的字节串进行 Base64 编码  
    base64_encoded = base64.b64encode(md5_hash).decode('utf-8')  
    return base64_encoded  

def md5_base64_file(absPath: str) -> str:
    """
    获取文件的MD5值，并转化为base64编码返回
    """
    md5_hash = file2md5(absPath)
    base64_content = base64.b64encode(md5_hash).decode('utf-8')
    return base64_content


def file2md5(absPath: str) -> str:
    """
    计算文件的md5
    """
    with open(absPath, 'rb') as f:
        content = f.read()
    md5_tool = hashlib.md5()
    md5_tool.update(content)
    md5_hash = md5_tool.digest()
    return md5_hash



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    client: eqb_sign = eqb_sign(env='test')


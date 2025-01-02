"""
e签宝补救措施
1、通过模版创建文件
2、创建角色账号
3、通过文件获取盖章位置
4、通过“文件”，“账号”，“盖章位置”组装成一个发起签约的请求报文，获取流水号
5、通过“流水号”获取到签约地址
"""

from datetime import datetime, timezone  
from bllose.config.Config import bConfig
from bllose.esign.esign_enums.env_enum import EqbEnum
import hashlib  
import base64
import hmac
import http.client
import io
import gzip
import logging
import json
import urllib
from urllib.parse import quote, quote_plus, urlencode
import requests

class eqb_sign():
    @bConfig()
    def __init__(self, env:str = 'test', config = {}) -> None:
        # 通过配置加载工具加载的配置内容
        # 后续逻辑直接使用保存下载的config对象, 获取对应的配置项
        self.config = config
        self.env = EqbEnum.of(env.lower())

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
        self.web_host = eqb['web']['host']
        self.upload_host = eqb['upload']['host']
        self.app_key = eqb['appKey']
        self.type = 'POST'

    def person_info_v1_accountId(self, accountId):
        current_path = f'/v1/accounts/{accountId}'
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(bodyRaw=None, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']
        else:
            logging.error(f'获取个人信息失败，请求路径{current_path} 返回报文{response_json}')
            return []
        
    def person_info_v1(self, thirdPartyUserId):
        current_path=f'/v1/accounts/getByThirdId?thirdPartyUserId={thirdPartyUserId}'
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(bodyRaw=None, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']
        else:
            logging.error(f'获取个人信息失败，请求路径{current_path} 返回报文{response_json}')
            return []

    def person_info_v3(self, psnId:str = None, 
                    psnAccount:str = None, 
                    psnIDCardNum:str = None, 
                    psnIDCardType:str = 'CRED_PSN_CH_IDCARD'):
        """
        V3查询个人认证信息
        Args:
            psnId(str): 个人账号ID
            psnAccount(str): 个人账号标识（手机号或邮箱）
            psnIDCardNum(str): 个人用户的证件号
            psnIDCardType(str): 个人证件号类型
            - CRED_PSN_CH_IDCARD: 中国大陆居民身份证
            - CRED_PSN_CH_HONGKONG: 香港来往大陆通行证
            - CRED_PSN_CH_MACAO: 澳门来往大陆通行证
            - CRED_PSN_CH_TWCARD: 台湾来往大陆通行证
            - CRED_PSN_PASSPORT: 护照

        """
        current_path = r'/v3/persons/identity-info?'
        if psnId is not None and len(psnId) > 1:
            current_path = current_path + 'psnId=' + psnId
        elif psnAccount is not None and len(psnAccount) > 1:
            current_path = current_path + 'psnAccount=' + psnAccount
        elif psnIDCardNum is not None and len(psnIDCardNum) > 1:
            current_path = current_path + 'psnIDCardNum=' + psnIDCardNum\
                        + '&psnIDCardType=' + psnIDCardType
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(bodyRaw=None, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']
        else:
            logging.error(f'获取个人信息失败，请求路径{current_path} 返回报文{response_json}')
            return []

    def psn_auth_url_v3(self, psnId:str = None):
        """
        获取个人认证&授权页面链接
        """
        current_path=r'/v3/psn-auth-url'

        body = {
            "psnAuthConfig": {
                "psnId": psnId
            }
        }

        self.establish_head_code(None, current_path)
        response_json = self.getResponseJson(bodyRaw=json.dumps(body), 
                                             current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']
        else:
            logging.error(f'获取个人信息失败, 返回报文{response_json}')
            return []

        
    def downloadContractByFlowId(self, flowId: str) -> list:
        """
        通过流水号ID，获取合同下载地址
        Args:
            flowId(str): e签宝流水号
        Returns:
            downloadInfo(list): 合同下载地址信息
                - fileId(str): 文件ID
                - fileName(str): 文件名字
                - fileUrl(str): 文件下载地址
        """
        current_path = f'/v1/signflows/{flowId}/documents'
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(bodyRaw=None, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']['docs']
        else:
            logging.error(f'下载流水号{flowId}的合同文件失败，返回报文{response_json}')
            return []

    def fetchUpdateFileUrl(self, contentMd5: str, fileName: str, fileSize: int, 
                           convertToHTML: bool = False) -> tuple:
        """
        申请上传合同文件
        获取最终上传文件的地址
        Args:
            contentMd5(str): 文件MD5编码的base64格式字符串
            fileName(str): 文件名称
            fileSize(long): 文件大小
            convertToHTML(bool): 是否转化为 html （动态模版、可变长字符串等需要转化才行）
        Returns:
            fileUploadInfo(tuple): 包含两个元素的元组
                - fileId(str): 文件ID
                - fileUploadUrl(str): 文件上传路径
        """
        current_url = r'/v3/files/file-upload-url'
        request_dict = {
                        "contentMd5": contentMd5,
                        "contentType": "application/octet-stream",
                        "fileName": fileName,
                        "fileSize": fileSize,
                        "convertToHTML": convertToHTML
                    }
        bodyRaw = json.dumps(request_dict)
        self.establish_head_code(bodyRaw, current_url)
        response_json = self.getResponseJson(bodyRaw, current_url)
        if response_json['code'] == 0:
            return str(response_json['data']['fileId']), str(response_json['data']['fileUploadUrl'])
        else:
            logging.warning(f'获取上传文件地址失败,返回报文: {json.dumps(response_json, ensure_ascii=False)}')
            return '', ''

    def uploadFile(self, putUrl: str, md5: str, absPath: str):
        """
        上传选中的文件
        PUT请求，单独处理
        Args:
            putUrl(str): 由 #fetchUpdateFileUrl 调用e签宝返回的上传地址
            md5(str): 文件的MD5值，base64格式
            absPath(str): 文件的绝对路径
        Returns:
            result(tuple): 返回结果
                - code(str): 返回编码
                - reason(str): 返回信息
        ```
        file_path = r'\to\\your\file\\path'
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
        <h1>查询文件上传状态</h1>
        <p>可以用于下载合同文件</p>
        Args:
            fileId(str): 文件ID
        Returns:
            fileInfo(tuple): 文件相关信息
                - fileName(str): 文件名字
                - fileDownloadUrl(str): 文件下载地址，如果有的话
                - fileStatus(int): 文件转化状态
        ```
        fileStatus 枚举：
        0 - 文件未上传
        1 - 文件上传中
        2 - 文件上传已完成 或 文件已转换（HTML）
        3 - 文件上传失败
        4 - 文件等待转换（PDF）
        5 - 文件已转换（PDF）
        6 - 加水印中
        7 - 加水印完毕
        8 - 文件转化中（PDF）
        9 - 文件转换失败（PDF）
        10 - 文件等待转换（HTML）
        11 - 文件转换中（HTML）
        12 - 文件转换失败（HTML）
        ```
        """
        current_path = f'/v3/files/{fileId}'
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(None, current_path)
        if response_json['code'] != 0:
            logging.warning(f'下载文件{fileId}失败，返回报文:{json.dumps(response_json)}')
            return '', '', ''
        data = response_json['data']
        fileName = data['fileName']
        fileDownloadUrl = data['fileDownloadUrl']
        fileStatus = data['fileStatus']
        return fileName, fileDownloadUrl, fileStatus
    
    def docTemplateCreateUrl(self, fileId, docTemplateName, docTemplateType) -> tuple:
        """
        <h1>获取制作合同模板页面</h1>
        Args:
            fileId(str): 文件Id
            docTemplateName(str): 模版名称
            docTemplateType(int): 模版类型
        ```
        docTemplateType 模版类型枚举
        0 - PDF模板
        1 - HTML模板（适用动态增加表格行并填充内容场景）
        ```
        Returns:
            templateInfo(tuple): 模版相关信息
                - docTemplateId(str): 模版ID
                - docTemplateCreateUrl(str): 模版创建URL地址
        """
        current_path = r'/v3/doc-templates/doc-template-create-url'
        request_dict = {
            'fileId': fileId,
            'docTemplateType': docTemplateType,
            'docTemplateName': docTemplateName
        }
        bodyRaw = json.dumps(request_dict)
        self.establish_head_code(bodyRaw, current_path)
        response_json = self.getResponseJson(bodyRaw, current_path)
        if response_json['code'] == 0:
            data = response_json['data']
            return data['docTemplateId'], data['docTemplateCreateUrl']
        else:
            logging.warning(f'由文件{fileId}创建合同模版失败,返回报文 -> {response_json}')
            return '', ''
        
    def docTemplateEditUrl(self, templateId:str) -> str:
        """
        获取编辑合同模板页面(短连接)
        Args:
            templateId(str): 模版ID
        Returns:
            url(str): 编辑url (短连接，24小时有效)
        """
        shortUrl, _ = self.docTemplateEditUrlAll(templateId)
        return shortUrl
    
    def docTemplateEditUrlAll(self, templateId:str) -> tuple:
        """
        获取编辑合同模板页面
        Args:
            templateId(str): 模版ID
        Returns:
            url(tuple): 编辑url 24小时有效
                - shortUrl(str): 短连接
                - longUrl(str): 长连接
        """
        current_path = f'/v3/doc-templates/{templateId}/doc-template-edit-url'
        request_dict = {
        }
        bodyRaw = json.dumps(request_dict)
        self.establish_head_code(bodyRaw, current_path)
        response_json = self.getResponseJson(bodyRaw, current_path)
        if response_json['code'] == 0:
            data = response_json['data']
            return data['docTemplateEditUrl'], data['docTemplateEditLongUrl']
        else:
            logging.debug(f'获取模版{templateId}编辑地址失败,返回报文:{response_json}')
            return '', ''

        
    def getEncryptionByTemplateId(self, templateId:str) -> str:
        """
        获取请求的秘钥
        Args:
            templateId(str): 模版ID
        Returns:
            encryption(str): 用于网页请求的秘钥
        """
        current_path = f'/v3/doc-templates/{templateId}/doc-template-edit-url'
        request_dict = {
        }
        bodyRaw = json.dumps(request_dict)
        self.establish_head_code(bodyRaw, current_path)
        response_json = self.getResponseJson(bodyRaw, current_path)
        if response_json['code'] == 0:
            docTemplateEditLongUrl = response_json['data']['docTemplateEditLongUrl']
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(docTemplateEditLongUrl)
            query_params = parse_qs(parsed_url.query)
            return query_params.get('encryption')[0]
        
    def getDocTemplateDetails(self, templateId:str, encryption:str) -> dict:
        """
        获取模版的详细信息
        Args:
            templateId(str): 模版ID
            encryption(str): 网页访问秘钥
        Returns:
            templateDetail(dict): 模版详情
        """
        
        current_path = f'/webserver/v3/api/doc-templates/{templateId}/detail?encryption={quote(encryption, safe='')}'
        response = requests.get('http://' + self.web_host + current_path)

        if response.status_code != 200:
            logging.warning(f'请求失败, code:{response.status_code} reason:{response.reason}')
        
        response_json = json.loads(response.text)
        if response_json['code'] == 0 :
            return response_json['data']
        else:
            logging.error(f'获取模版{templateId}详情失败, 返回报文: {response_json}')
            return {}
        
    def updateDocTemplateComponents(self, templateId:str, encryption:str, requestBody:dict) -> None:
        """
        指定模版id更新组件信息
        Args:
            templateId(str): 模版ID
            encryption(str): 访问秘钥
            requestBody(str): 组件参数
        """
        current_path = f'/webserver/v3/api/doc-templates/{quote(templateId)}/templateAndComponents?encryption={quote(encryption, safe='')}'
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post('http://' + self.web_host + current_path, json=requestBody, headers=headers)
        if response.status_code != 200:
            logging.error(f'上传更新的模版失败, 返回报文: {json.dumps(response, ensure_ascii=False)}')
        else:
            responseJson = response.json()
            if responseJson['code'] != 0:
                logging.warning(f'上传更新的模版失败, 返回报文: {response.json()}')
        

    def fetchSignUrl(self, flowId:str, mobile:str) -> str:
        """
        获取签约地址
        Args:
            flowId(str): e签宝的流水号
            mobile(str): 执行人账号。 因为e签宝上通常将个人电话作为账号，所以这里通常是输入手机号
        Returns:
            shortUrl(str): 签约地址
        """
        return self.getH5Url(mobile, flowId)
    
    def getExeUrl(self, accountId:str, thirdFlowId: str) -> str:
        """
        V1通过账号ID和流水号获取签约地址
        Args:
            accountId(str): 签署操作人账号ID（个人账号ID）
            thirdFlowId(str): 当前账号参与的签约流程ID
        Return:
            shortUrl(str): 合同签署流程
        """
        current_path = f'/v1/signflows/{thirdFlowId}/executeUrl?accountId={accountId}'
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(bodyRaw=None, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']['shortUrl']
        else:
            logging.error(f'获取签约地址失败，返回信息{response_json}')
            return ''
        
    def getH5Url(self, thirdFlowId: str, 
                 psnAccount: str = None, 
                 psnId:str = None) -> str:
        """
        V3通过账号和流水号获取签约地址
        Args:
            psnAccount(str): 用户在e签宝的登录账号，一般为移动电话号码/邮箱账号。 二选一
            psnId(str): 签署操作人账号ID（个人账号ID）。二选一
            thirdFlowId(str): 当前账号参与的签约流程ID
        Returns:
            shortUrl(str): 合同签署流程
        """
        if psnAccount is None and psnId is None:
            raise ValueError('手机号码和操作人账号ID不能同时为空')
        if psnId is not None and len(psnId) > 1:
            psnAccount = None
        else:
            psnId = None
        req = {
                    "needLogin": True,
                    "urlType": 2,
                    "operator": {
                        "psnAccount": psnAccount,
                        "psnId": psnId
                    }
                }
        current_path = f'/v3/sign-flow/{thirdFlowId}/sign-url'
        bodyRaw = json.dumps(req, ensure_ascii=False)
        self.establish_head_code(bodyRaw, current_path)
        response_json = self.getResponseJson(bodyRaw=bodyRaw, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']['shortUrl']
        else:
            logging.error(f'获取签约地址失败，返回信息{response_json}')
            return ''

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
        
    def updateAccountsByid(self, accountId:str, name:str, mobile:str) :
        """
        通过账号ID，更新人名和电话
        Args:
            accountId(str): 账号ID
            name(str): 签署人/执行人名称
            mobile(str): 电话号码/e签宝账号
        Retruns:
            data(dict): 更新结果
                - mobile(str): 最新电话
                - name(str): 最新姓名
                - accountId(str): 当前账号id
                - idType(str): 证件类型。'CRED_PSN_CH_IDCARD' 中国身份证号码
                - idNumber(str): 证件号码
        """
        current_path=f'/v1/accounts/{accountId}'
        bodyRaw = {
            "mobile": mobile,
            "name": name
        }
        bodyStr = json.dumps(bodyRaw)
        self.establish_head_code(bodyStr, current_path, 'PUT')
        response_json = self.getResponseJson(bodyStr, current_path)
        if response_json['code'] == 0:
            return response_json['data']
        else:
            logging.warning(f'更新用户信息失败，返回报文: {response_json}')
            return {}

        
    def createFlowOneStep(self, bodyRaw: str) -> str:
        """
        V2版本
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
        else:
            logging.error(f'异步发起签约请求失败, 返回报文:{response_json}')
            return ''
    
    def getSignFlowDetail(self, signFlowId:str) -> dict:
        """
        获取签署流程详情
        Args:
            signFlowId(str): 签约流水号
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
        
    def createByFile(self, req) -> str:
        """
        （精简版）基于文件发起签署
        Args:
            req: 请求报文。可以是str, dict, list等
        Returns:
            signFlowId(str): e签宝签约流水号
        """
        current_path = r'/v3/sign-flow/create-by-file'
        if not isinstance(req, str):
            if isinstance(req, dict) or isinstance(req, list):
                req = json.dumps(req)
            else:
                logging.error(f'不支持请求参数类型{type(req)},请输入str, dict, list或json')
                raise ValueError('请求参数不合法')
        self.establish_head_code(req, current_path)
        response_json = self.getResponseJson(bodyRaw=req, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']['signFlowId']
        else:
            logging.error(response_json)
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

    def getOrganizationInfo(self, orgIdCard: str = '', orgId: str = '') -> dict:
        """
        通过社会统一信用代码
        获取项目公司在e签宝上的相关信息
        Args:
            orgIdCard:str 社会统一信用代码
            orgId:str 公司ID编号
        Returns:
            data:dict 项目公司基本信息字典
            - orgId:str 项目公司在e签宝中的ID号
        """
        if orgId is not None and len(orgId) > 1:
            current_path = f'/v3/organizations/identity-info?orgId={orgId}'
        else:
            current_path = f'/v3/organizations/identity-info?orgIDCardNum={orgIdCard}&orgIDCardType=CRED_ORG_USCC'
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(bodyRaw=None, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']
        else:
            logging.error(f'获取公司信息失败, 返回报文{response_json}, 请求host: {self.host}')
            return {}
        
    def getSealsInfo(self, orgId:str) -> dict:
        """
        通过orgId获取该公司下的印章ID
        Args:
            orgId: str 企业在e签宝中记录的ID
        Returns:
            sealsInfo: dict 项目公司的印章相关信息
        """
        current_path = f'/v1/organizations/{orgId}/seals'
        self.establish_head_code(None, current_path, 'GET')
        response_json = self.getResponseJson(bodyRaw=None, current_path=current_path)
        if response_json['code'] == 0:
            return response_json['data']
        else:
            return {}

        
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
        
    def getResponseJson(self, bodyRaw, current_path, type:str = 'NOMAL') -> json:
        """
        发送请求，并解析返回结果
        Args:
            bodyRaw(str): 请求报文内容， GET，或者没有请求报文时传 None
            current_path(str): 当前请求路径
            type(str): 当前请求类型
                - NOMAL
                - UPLOAD
                - WEB
        Returns:
            response_json(json): 返回报文
        """
        match(type):
            case 'WEB':
                host = self.web_host
            case 'UPLOAD':
                host = self.upload_host
            case 'NOMAL':
                host = self.host
                
        conn = http.client.HTTPSConnection(host)
        if bodyRaw is not None:
            bodyRaw = bodyRaw.encode("utf-8").decode("latin1")
        conn.request(self.type, current_path, bodyRaw, self.header)
        response = conn.getresponse()

        match response.code:
            case 403:
                logging.warning(f'拒绝访问!')
                return json.loads(json.dumps({'code': 999}))
            case 401:
                logging.warning('未授权!')
                return json.loads(json.dumps({'code': 999}))
            case 404:
                logging.warning(f'请求路径不存在!{host}{current_path}')
                return json.loads(json.dumps({'code': 999}))
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
        elif method == 'PUT':
            contentMd5 = md5_base64_encode(bodyRaw)
            self.type = 'PUT'
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

def md5_base64_encode(body_raw:str):
    """
    将纯字符转化为MD5，然后再将MD5转化为Base64编码
    """
    if body_raw == None:
        body_raw = ''
    elif not isinstance(body_raw, str):
        logging.error('请求报文必须转化为字符串!')
        raise Exception("参数异常")
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
    client.getOrganizationInfo('91440300MA5H9NX89R')
    # templateId = 'eecc2d735fa04697bad4fb3aa9e46b87'
    # encryption = client.getEncryptionByTemplateId(templateId)
    # response_json = client.getDocTemplateDetails(templateId, encryption)
    # print(response_json)


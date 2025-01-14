from cmd2 import CommandSet, with_default_category
import cmd2
import os
import json
from bllose.tasks.commons.GetDynamicTemplate import uploadOneFile, uploadAndConvert2Html
from bllose.tasks.commons.CopyTemplate import copy
from bllose.esign.Client import eqb_sign
from bllose.esign.esign_enums.file_status import FileStatus
from bllose.esign.esign_enums.env_enum import EqbEnum
from bllose.esign.esign_enums.identity_type import IdentityEnum
from bllose.esign.eqb_functions import sign_flow_identity_list, download_and_check_image
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.style import Style

from bllose.esign.eqb_functions import (
    template_function, 
    set_title, 
    post_handler
    )


@with_default_category('e签宝命令')
class AutoLoadCommandSet(CommandSet):
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.env = 'test'
        set_title("e签宝 -> 测试环境")
        self.local_save_path = '/temp/download'
        self.urlStyle = Style(color="#0000FF", underline=True)

    identity_parser = cmd2.Cmd2ArgumentParser()
    # company_parser.add_argument('-o', '--orgId', action='store_true', help='通过orgId进行查询')
    identity_parser.add_argument('signFlowId', nargs=1, help='签约流水号')
    @cmd2.with_argparser(identity_parser)
    def do_identity(self, args):
        """
        获取签约流水号下所有认证信息，包括扫脸等
        """
        signFlowId = args.signFlowId[-1]
        identityDetailList = sign_flow_identity_list(flowId=signFlowId, env=self.env)
        for identityItem in identityDetailList:
            for psnId, identityList in identityItem.items():
                # identityFlowId = identity['identityFlowId']
                if identityList is None or len(identityList) < 1:
                    continue
                identity = identityList[0]
                identityType = identity['identityType']
                identityDetail = identity['identityDetail']
                identityBizType = identity['identityBizType']

                identityDetailJson = json.loads(identityDetail)
                facePhotoUrl = identityDetailJson['facePhotoUrl']

                # 认证数据信息
                conclusion = Text()
                conclusion.append("认证类型: ", style="bold yellow")
                conclusion.append('意愿认证' if identityBizType == '1' else '实名认证', style="bold green")
                conclusion.append("\n")
                conclusion.append("认证方式: ", style="bold yellow")
                conclusion.append(IdentityEnum.of(identityType), style="bold green")
                conclusion.append("\n")
                conclusion.append("刷脸活体率分值: ", style="bold yellow")
                conclusion.append(identityDetailJson['livingScore'], style="bold green")
                conclusion.append("\n")
                conclusion.append("刷脸相似度分值: ", style="bold yellow")
                conclusion.append(identityDetailJson['similarity'], style="bold green")
                conclusion.append("\n")
                conclusion.append("刷脸认证时刷脸照片: ", style="bold yellow")
                conclusion.append(identityDetailJson['facePhotoUrl'], style=self.urlStyle)
                panel = Panel(conclusion, title=f"自然人id:{psnId}")
                self.console.print(panel)

                # 人脸图片展示
                download_and_check_image(url=facePhotoUrl)
                input("Press [enter] to continue.")


    company_parser = cmd2.Cmd2ArgumentParser()
    company_parser.add_argument('-o', '--orgId', action='store_true', help='通过orgId进行查询')
    company_parser.add_argument('creditId', nargs=1, help='通过社会统一信用代码获取企业信息')
    @cmd2.with_argparser(company_parser)
    def do_company(self, args):
        creditId = args.creditId[-1]
        if creditId is None or len(creditId) < 1:
            self.console.print(f'')
            return

        client = eqb_sign(env=self.env)
        orgInfo = client.getOrganizationInfo(orgId=creditId) if args.orgId else client.getOrganizationInfo(creditId)
        if len(orgInfo) > 0:
            conclusion = Text()
            conclusion.append("企业ID    ", style="bold yellow")
            conclusion.append(' : ')
            conclusion.append(orgInfo['orgId'], style="green")
            conclusion.append("\r\n")
            if orgInfo['realnameStatus'] == 1:
                conclusion.append('已实名', style="green")
            else:
                conclusion.append('未实名', style="bold red")
            conclusion.append("\r\n")
            if orgInfo['authorizeUserInfo']:
                conclusion.append('已授权当前企业', style="green")
            else:
                conclusion.append('未授权当前企业', style="bold red")
            conclusion.append("\r\n")

            subOrgInfo = orgInfo['orgInfo']
            from bllose.esign.esign_enums.org_type import OrgTypeEnum
            conclusion.append(OrgTypeEnum.of(subOrgInfo['orgIDCardType']).msg, style='bold yellow')
            conclusion.append('   : ')
            conclusion.append(subOrgInfo['orgIDCardNum'], style='green')
            conclusion.append("\r\n")
            
            conclusion.append('法人名称  ', style='bold yellow')
            conclusion.append(' : ')
            conclusion.append(subOrgInfo['legalRepName'], style='green')
            conclusion.append("\r\n")
            
            conclusion.append('负责人    ', style='bold yellow')
            conclusion.append(' : ')
            conclusion.append(subOrgInfo['adminName'], style='green')
            conclusion.append("\r\n")
            
            conclusion.append('负责人电话', style='bold yellow')
            conclusion.append(' : ')
            conclusion.append(subOrgInfo['adminAccount'], style='green')
            panel = Panel(conclusion, title=orgInfo['orgName'])
            self.console.print(panel)
        else:
            self.console.print("未查询到相关信息", style="red")

    copy_parser = cmd2.Cmd2ArgumentParser()
    copy_parser.add_argument('-p', '--pro', action='store_true', help='拷贝到生产环境。默认为false，将被拷贝到测试环境')
    copy_parser.add_argument('params', nargs=1, help='将指定合同模版复制到指定环境，默认测试，-p生产。\r\n默认从测试环境拷贝，如果测试环境没有则从生产环境拷贝。若都不存在则报错。')
    @cmd2.with_argparser(copy_parser)
    def do_copy(self, args):
        templateId = args.params[-1]
        originEnv = 'test' 
        targetEnv = 'pro' if args.pro else 'test'
        try:
            originTemplate, targetTemplate = copy(originEnv, targetEnv, templateId)
        except ValueError:
            originEnv = 'pro'
            try:
                originTemplate, targetTemplate = copy(originEnv, targetEnv, templateId)
            except ValueError:
                self.console.print(f'模板:[bold red]{templateId}[/bold red]不存在~')
                return
        conclusion = Text()
        conclusion.append("源模版[", style="bold yellow")
        conclusion.append(originEnv, style="bold green")
        conclusion.append("]: ", style="bold yellow")
        conclusion.append(originTemplate, style="bold red on white")
        conclusion.append("\n")
        conclusion.append("目标模板[", style="bold yellow")
        conclusion.append(targetEnv, style="bold green")
        conclusion.append("]: ", style="bold yellow")
        conclusion.append(targetTemplate, style="bold red on white")
        panel = Panel(conclusion, title="拷贝完成")
        self.console.print(panel)


    upload_parser = cmd2.Cmd2ArgumentParser()
    upload_parser.add_argument('-c', '--convert', action='store_true', help='转化为HTML模版')
    upload_parser.add_argument('params', nargs='+', help='输入上传文件的绝对路径')
    @cmd2.with_argparser(upload_parser)
    def do_upload(self, args):
        """
        上传合同文件
        """
        abs_path = args.params[0]
        if not os.path.isfile(abs_path):
            abs_path = os.getcwd + os.sep + abs_path
            if not os.path.isfile(abs_path):
                self.console.print(f'文件不存在: [bold red]{args.params[0]}[/bold red]')
        if args.convert:
            templateId, fileId = uploadAndConvert2Html(abs_path=os.path.abspath(abs_path), 
                                                       convertToHTML=True, 
                                                       env=self.env)
            result = Text()
            result.append("模版ID: ", style="bold yellow")
            result.append(templateId, style="italic green")
            result.append("\n")
            result.append("文件ID: ", style="bold yellow")
            result.append(fileId, style="italic green")
            panel = Panel(result, title='上传文件并转化为HTML模版')
            self.console.print(panel)
        else:
            fileName, fileId = uploadOneFile(abs_path=abs_path, env=self.env)
            # self.console.print(f'[green]{fileName}[/green] -> fileId: [bold red]{fileId}[/bold red]')
            result = Text()
            result.append("文件ID: ", style="bold yellow")
            result.append(fileId, style="italic green")
            panel = Panel(result, title=fileName)
            self.console.print(panel)

    person_parser = cmd2.Cmd2ArgumentParser()
    person_parser.add_argument('params', nargs='*', help='身份证')
    @cmd2.with_argparser(person_parser)
    def do_person(self, args):
        params = args.params
        if not params:
            self.console.print('请输入一个身份证!', style = 'reverse')
            return
        creditId = params[0]
        client = eqb_sign(env=self.env)
        result_v3 = client.person_info_v3(psnIDCardNum = creditId)
        
        result_v1 = client.person_info_v1(thirdPartyUserId=creditId)
        self.console.print(f'v3: {result_v3['psnId']}\r\nv1: {result_v1['accountId']}')

    
    flowid_parser = cmd2.Cmd2ArgumentParser()
    flowid_parser.add_argument('params', nargs='*', help='e签宝签约流水号')
    @cmd2.with_argparser(flowid_parser)
    def do_flowId(self, args):
        """
        获取第三方流水对应合同下载地址
        """
        params = args.params
        if not params:
            self.console.print('请输入一个模版ID!', style = 'reverse')
            return
        flowId = params[0]
        client = eqb_sign(env=self.env)
        response:list = client.downloadContractByFlowId(flowId)
        if len(response) == 0:
            self.console.print('没有文件', style='red')
        for doc in response:
            urlStyle = Style(color="#0000FF", underline=True)
            result = Text()
            result.append("文件ID: ", style="bold yellow")
            result.append(doc['fileId'], style="italic green")
            result.append("\n")
            result.append("下载地址: ", style="bold yellow")
            result.append(doc['fileUrl'], style=urlStyle)
            panel = Panel(result, title=doc['fileName'])
            self.console.print(panel)

    
    template_edit_url_parser = cmd2.Cmd2ArgumentParser()
    template_edit_url_parser.add_argument('params', nargs='*', help='fileId, 文件ID, 比如：87f579e3648146cf825fc45f45bcf169')
    @cmd2.with_argparser(template_edit_url_parser)
    def do_template(self, args):
        params = args.params
        if not params:
            self.console.print('请输入一个模版ID!', style = 'reverse')
            return
        templateId = params[0]
        # 具体执行的逻辑
        shortUrl = template_function(env=self.env, templateId= templateId)
        # 具体执行的逻辑
        if shortUrl.startswith('http'):
            # self.console.print(f'[underline blue]{shortUrl}[/underline blue]')
            urlStyle = Style(color="#0000FF", underline=True)
            result = Text()
            result.append("模版编辑地址: ", style="bold yellow")
            result.append(shortUrl, style=urlStyle)
            panel = Panel(result, title=templateId)
            self.console.print(panel)
        else:
            self.console.print('获取模版编辑地址失败!', style = 'reverse')

    file_download_parser = cmd2.Cmd2ArgumentParser()
    file_download_parser.add_argument('params', nargs='*', help='fileId, 文件ID, 比如：87f579e3648146cf825fc45f45bcf169')
    @cmd2.with_argparser(file_download_parser)
    def do_fileId(self, args):
        """
        通过文件ID（fileId），获取其下载地址和状态
        """
        params = args.params
        if len(params) != 1:
            self.console.print(f'参数只能且必须是一个文件ID', style='red')
            return
        fileId = params[0]
        # 具体执行的逻辑
        client = eqb_sign(self.env)
        fileName, fileDownloadUrl, fileStatus = client.fetchFileByFileId(fileId)
        # 具体执行的逻辑
        
        # 渲染结果输出
        urlStyle = Style(color="#0000FF", underline=True)
        result = Text()
        result.append("文件名: ", style="bold yellow")
        result.append(fileName, style="italic green")
        result.append("\n")
        result.append("文件状态: ", style="bold yellow")
        result.append(FileStatus.from_code(fileStatus).msg, style="italic green")
        result.append("\n")
        result.append("下载地址: ", style="bold yellow")
        result.append(fileDownloadUrl, style=urlStyle)
        panel = Panel(result, title="执行结果")
        self.console.print(panel)
        # 渲染结果输出

        post_handler(fileDownloadUrl, self.local_save_path)


    def do_pro(self, args):
        """
        切换为生产环境
        """
        if self.env == 'pro':
            self.console.print('当前环境就是生产环境')
        else:
            self.console.print(f'环境切换 [strike white]{self.env}[/strike white] [blink2 red]->[/blink2 red] [bold green]pro[/bold green]')
            self.env = 'pro'
        set_title("e签宝 -> 生产环境")

    def do_test(self, args):
        """
        切换为测试环境
        """
        if self.env != 'pro':
            self.console.print('当前环境就是测试环境')
        else:
            self.console.print(f'环境切换 [strike white]{self.env}[/strike white] [blink2 red]->[/blink2 red] [bold green]test[/bold green]')
            self.env = 'test'
        set_title("e签宝 -> 测试环境")

    change_env_parser = cmd2.Cmd2ArgumentParser()
    change_env_parser.add_argument('params', nargs='*', help='显示或切换环境 pro; test')
    @cmd2.with_argparser(change_env_parser)
    def do_env(self, args):
        """
        获取当前环境
        """
        params = args.params
        if not params:
            self.console.print(f'当前环境[bold on_yellow]{self.env}[/bold on_yellow]')
            return
        target = EqbEnum.of(params[0]).value
        if target == self.env:
            self.console.print(f'维持原环境[dim cyan]{self.env}[/dim cyan]')
        else:
            self.console.print(f'环境切换 [strike white]{self.env}[/strike white] [blink2 red]->[/blink2 red] [bold green]{target}[/bold green]')
            self.env = target
        if self.env == 'pro':
            set_title("e签宝 -> 生产环境")
        else:
            set_title("e签宝 -> 测试环境")
        
            
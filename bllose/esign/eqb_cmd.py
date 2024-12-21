import cmd2
import logging
import os
import time
import json
from pathlib import Path
from bllose.tasks.commons.GetSignUrlAfterMobileChanged import getTheNewSignUrl
from bllose.tasks.commons.leaseContract import getSignUrl
from bllose.tasks.commons.GetDynamicTemplate import uploadOneFile
from bllose.esign.Client import eqb_sign
from bllose.esign.esign_enums.file_status import FileStatus
from bllose.esign.esign_enums.env_enum import EqbEnum
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.style import Style
from rich.progress import Progress
from bllose.esign.eqb_functions import template_function, set_title, post_handler


class eqb_cmd(cmd2.Cmd):
    intro = "e签宝相关功能"
    prompt = 'e签宝> '

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.env = 'test'
        set_title("e签宝 -> 测试环境")
        self.local_save_path = '/temp/download'
        self.update_prompt()

        # 定义别名
        self.aliases['flowid'] = 'flowId'
        self.aliases['fileid'] = 'fileId'

    def update_prompt(self):
        """更新提示符以显示当前工作目录"""
        current_dir = os.getcwd()
        self.prompt = f"e签宝 {current_dir}> "

    def do_cd(self, arg):
        """Change to the directory specified.

        Usage: cd <directory>
        """
        new_dir = arg.strip()
        if new_dir:
            try:
                os.chdir(new_dir)
                self.update_prompt()  # 更新提示符以反映新的工作目录
            except FileNotFoundError:
                self.perror(f"Directory not found: {new_dir}")
            except NotADirectoryError:
                self.perror(f"Not a directory: {new_dir}")
            except PermissionError:
                self.perror(f"Permission denied: {new_dir}")
            except Exception as e:
                self.perror(f"Failed to change directory: {e}")

    def do_pwd(self, arg):
        """Print the current working directory.

        Usage: pwd
        """
        print(os.getcwd())


    ls_parser = cmd2.Cmd2ArgumentParser()
    ls_parser.add_argument('directory', nargs='?', default='.', help='Directory to list')
    ls_parser.add_argument('-l', action='store_true', help='use a long listing format')
    ls_parser.add_argument('-a', '--all', action='store_true', help='do not ignore entries starting with .')
    def do_ls(self, arg):
        try:
            if len(arg.arg_list) > 0:
                directory = arg.arg_list[-1]
            else:
                directory = os.getcwd()

            target_dir = Path(directory)
            if not target_dir.exists():
                self.perror(f"Directory does not exist: {target_dir}")
                return

            if not target_dir.is_dir():
                self.perror(f"Not a directory: {target_dir}")
                return

            entries = list(target_dir.iterdir())    
            if not entries:
                print("No items found.")
                return

            for entry in sorted(entries):
                if entry.is_dir():
                    self.console.print(f'[green]{entry.name}[/green]')
                else:
                    self.console.print(entry.name)
        except Exception as e:
            self.perror(f"Failed to list directory: {e}")

    check_parser = cmd2.Cmd2ArgumentParser()
    check_parser.add_argument('params', nargs='+', help='输入上传文件的绝对路径')
    @cmd2.with_argparser(check_parser)
    def do_check(self, args):
        fileName = args.params[-1]

        # 判断入参是绝对路径还是文件名
        # 若不是绝对路径则尝试再当前目录寻找指定文件
        # 若依然不是一个文件，则抛出异常
        if not os.path.isfile(fileName):
            fileNameTemp = os.getcwd() + os.sep + fileName
            if os.path.isfile(fileNameTemp):
                fileName = fileNameTemp
            else:
                raise FileNotFoundError(f"No such file: '{fileName}'")
            
        # 请求失败，无法获取结果的流水号保存对象
        failed_holder = {}
        # 已经完成的流程
        finished_holder = []
        # 还在进行中的流程
        processing_holder = {}
        # 将读取的流水号暂存在内存
        flowIdList = []
        with open(fileName, 'r', encoding='utf-8') as file:
            client = eqb_sign(env=self.env)
            # 读取流水号，并统计行数    
            total_line = 0
            for line in file:
                flowIdList.append(line.strip())
                total_line += 1
            with Progress() as progress:
                cur_task = progress.add_task(f"[blue]分析{total_line}条合同结果", total=total_line)
                for flowId in flowIdList:
                    result_json = client.getSignFlowDetail(flowId)
                    code = result_json['code']
                    if code != 0:
                        failed_holder.update({flowId:result_json['message']})
                    else:
                        result = result_json['data']
                        signFlowStatus = result['signFlowStatus']
                        if signFlowStatus != 2:
                            processing_holder.update({flowId:result['signFlowDescription']})
                        else:
                            finished_holder.append({"action":"SIGN_FLOW_COMPLETE","timestamp":int(time.time()*1000),"signFlowId":flowId,"signFlowTitle":"户用光伏业务经销协议（2025版）","signFlowStatus":"2","statusDescription":"完成","signFlowCreateTime":result['signFlowCreateTime'],"signFlowStartTime":result['signFlowStartTime'],"signFlowFinishTime":result['signFlowFinishTime']})
                    progress.update(cur_task, advance=1)
        conclusion = Text()
        conclusion.append("已完成流程: ", style="bold yellow")
        conclusion.append(str(len(finished_holder)), style="bold green")
        conclusion.append("\n")
        conclusion.append("进行中流程: ", style="bold yellow")
        conclusion.append(str(len(processing_holder)), style="bold blue")
        conclusion.append("\n")
        conclusion.append("查询失败流程: ", style="bold yellow")
        conclusion.append(str(len(failed_holder)), style="bold red on white")
        panel = Panel(conclusion, title="执行结果")
        self.console.print(panel)
        
        self.console.print('\r\n')

        if len(processing_holder) < 1:
            self.console.print(f'[green]没有已完成流程[/green]')
        else:
            for cur_finish in finished_holder:
                self.console.print(json.dumps(cur_finish, ensure_ascii=False))

        if len(failed_holder) > 0:
            for key, value in failed_holder.items():
                self.console.print(f'[green]{key}[/green] -> [bold red]{value}[/bold red]')

                


    upload_parser = cmd2.Cmd2ArgumentParser()
    upload_parser.add_argument('params', nargs='+', help='输入上传文件的绝对路径')
    @cmd2.with_argparser(upload_parser)
    def do_upload(self, args):
        """
        上传合同文件
        """
        abs_path = args.params[0]
        fileName, fileId = uploadOneFile(abs_path=abs_path, env=self.env)
        self.console.print(f'[green]{fileName}[/green] -> fileId: [bold red]{fileId}[/bold red]')

    contract_parser = cmd2.Cmd2ArgumentParser()
    contract_parser.add_argument('params', nargs=4, help='发起签约的参数有且只能有四个，顺序为:社会统一信用代码、身份证、合同服务签约流水id, 文件id')
    @cmd2.with_argparser(contract_parser)
    def do_contract(self, args):
        """
        通过部分数据发起新的“屋顶租赁协议”的签约流程

        1.首先从数据库查询出“社会统一信用代码” 和 “身份证”  
        
        2.然后将合同文件id准备好
        
        使用改方法:
        ```
        e签宝> contract 社会统一信用代码 身份证 合同服务签约流水id 文件id
        签约流水号 文件id 签约地址
        ```

        参数的查询方法:
        ``` SQL
select CONCAT_WS(' - ', task.image_code, scene_name) as '类型', concat_ws(' ', unified_social_credit_code, ex_customer_idno, id) as '参数' from (
select a.ex_customer_name, 
AES_DECRYPT(from_base64(substr(a.ex_customer_mobile,3)),from_base64('XDM4Vvla+6kxP++4yOXb5A==')) 'ex_customer_mobile', 
AES_DECRYPT(from_base64(substr(a.ex_customer_idno,3)),from_base64('XDM4Vvla+6kxP++4yOXb5A==')) 'ex_customer_idno',
d.unified_social_credit_code,
d.company_name,
e.id,
e.scene_code,
e.image_code,
e.scene_name
from `xk-order`.`order` a 
left join `xk-order`.`order_product_config` b on a.order_no = b.order_no and b.is_delete = false
left join `xk-order`.`product_company` d on b.project_company_id = d.id and d.is_delete = false
left join `xk-contract`.`sf_sign_flow` e on a.order_no = e.object_no and e.is_delete = false
where a.is_delete = false
and a.order_no = 'GF241016115633116953'
order by a.create_time desc
limit 3 ) task;

        ```
        """
        credit_code, id_card, id, file_id = args.params
        signFlowId, fileId, shortUrl = getSignUrl(orgIdCard=credit_code, creditId=id_card, fileId=file_id, env=self.env)
        self.console.print(f'新的签约地址: {shortUrl}')
        sql = f"update `xk-contract`.`sf_sign_flow` set third_flow_id = '{signFlowId}', sign_flow_phase = 'NEW',  third_file_id = '{fileId}', sign_url = '{shortUrl}' where is_delete = 0 and "
        self.console.print(f'[green]{sql}[/green]id = [bold red]{id}[/bold red]')
    
    def do_sql(self, args):
        self.console.print(f"select CONCAT_WS(' - ', task.image_code, scene_name) as '类型', concat_ws(' ', unified_social_credit_code, ex_customer_idno, id) as '参数' from (")
        self.console.print(f"select a.ex_customer_name, ")
        self.console.print(f"AES_DECRYPT(from_base64(substr(a.ex_customer_mobile,3)),from_base64('XDM4Vvla+6kxP++4yOXb5A==')) 'ex_customer_mobile', ")
        self.console.print(f"AES_DECRYPT(from_base64(substr(a.ex_customer_idno,3)),from_base64('XDM4Vvla+6kxP++4yOXb5A==')) 'ex_customer_idno',")
        self.console.print(f"d.unified_social_credit_code,")
        self.console.print(f"d.company_name,")
        self.console.print(f"e.id,")
        self.console.print(f"e.scene_code,")
        self.console.print(f"e.image_code,")
        self.console.print(f"e.scene_name")
        self.console.print(f"from `xk-order`.`order` a ")
        self.console.print(f"left join `xk-order`.`order_product_config` b on a.order_no = b.order_no and b.is_delete = false")
        self.console.print(f"left join `xk-order`.`product_company` d on b.project_company_id = d.id and d.is_delete = false")
        self.console.print(f"left join `xk-contract`.`sf_sign_flow` e on a.order_no = e.object_no and e.is_delete = false")
        self.console.print(f"where a.is_delete = false")
        self.console.print(f"and a.order_no = 'GF241016115633116953'")
        self.console.print(f"order by a.create_time desc")
        self.console.print(f"limit 3 ) task;")
            

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
            print(f"\033]8;;{doc['fileUrl']}\033\\Click here to visit example.com\033]8;;\033\\")

    
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
            self.console.print(f'[underline blue]{shortUrl}[/underline blue]')
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
        

    load_parser = cmd2.Cmd2ArgumentParser()
    load_parser.add_argument('-t', '--target', type=str, default='signer', help='指定获取的签约地址所属角色，signer:签署人/农户； cosigner: 共签人/第二位签署人')
    load_parser.add_argument('params', nargs='+', help='其他参数')
    @cmd2.with_argparser(load_parser)
    def do_sign_url(self, args):
        """
        获取指定角色的签署地址(默认测试环境)
        订单号  流水号 sceneCode imageCode 合同名字 农户名字 农户电话 农户身份证 共签人名字 共签人电话 共签人身份证
        1       2       3         4           5       6       7       8           9         10          11
        数据查询SQL：
        ```
select concat_ws(',',order_no,third_flow_id,scene_code, image_code,scene_name,ex_customer_name,ex_customer_mobile,ex_customer_idno,cosigner_name,cosigner_phone,cosigner_idno)
from (
select a.order_no, c.third_flow_id, c.scene_code, c.image_code, c.scene_name,a.ex_customer_name,
AES_DECRYPT(from_base64(substr(a.ex_customer_mobile,3)),from_base64('XDM4Vvla+6kxP++4yOXb5A==')) 'ex_customer_mobile',
AES_DECRYPT(from_base64(substr(a.ex_customer_idno,3)),from_base64('XDM4Vvla+6kxP++4yOXb5A==')) 'ex_customer_idno',
b.cosigner_name,
AES_DECRYPT(from_base64(substr(b.cosigner_phone,3)),from_base64('XDM4Vvla+6kxP++4yOXb5A=='))  'cosigner_phone',
AES_DECRYPT(from_base64(substr(b.cosigner_idno,3)),from_base64('XDM4Vvla+6kxP++4yOXb5A==')) 'cosigner_idno'
from `xk-order`.`order` a left join `xk-order`.`order_cosigner` b on a.order_no = b.order_no and b.is_delete = false
left join `xk-contract`.`sf_sign_flow` c on a.order_no = c.object_no and c.is_delete = false
where a.is_delete = false 
and a.order_no = '需要处理的订单号') final;
        ```
        """
        target = args.target
        params = args.params
        if len(params) == 1:
            paramStr = params[0]
            if ',' in paramStr:
                params = paramStr.split(',')
            elif '\t' in paramStr:
                params = paramStr.split('\t')
            elif ';' in paramStr:
                params = paramStr.split(';')
        elif len(params) != 11:
            logging.error('请参照方法说明填入完整信息!')
            return
        
        
        if target.lower() != 'cosigner':
            name = params[5]
            mobile = params[6]
            creditId = params[7]
        else:
            name = params[8]
            mobile = params[9]
            creditId = params[10]
        
        if name is None or mobile is None or creditId is None or len(name) < 1 or len(mobile) < 1 or len(creditId) < 1:
            if target.lower() != 'cosigner':
                self.console.print(f'参数异常，获取的农户名字:{name} 农户电话:{mobile} 农户身份证:{creditId}, 整体解析参数{params}', style='red')
                return
            else:
                self.console.print(f'参数异常，获取的共签人名字:{name} 共签人电话:{mobile} 共签人身份证:{creditId}, 整体解析参数{params}', style='red')
                return

        shortUrl = getTheNewSignUrl(name=name, mobile=mobile, creditId=creditId, flowId=params[1], env=self.env)

        self.console.print(f'{name}电话{mobile}的最新签约地址是{shortUrl}', style='green')



def format_entry(entry):
    """格式化输出条目信息"""
    stats = entry.stat()
    permissions = oct(stats.st_mode)[-3:]
    size = stats.st_size
    modified_time = stats.st_mtime
    return f"{permissions} {size} bytes {entry.name}"

if __name__ == '__main__':
    eqb_cmd().cmdloop()
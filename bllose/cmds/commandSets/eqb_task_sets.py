from cmd2 import CommandSet, with_default_category
import cmd2
import logging
import os
import time
import json
from bllose.tasks.commons.GetSignUrlAfterMobileChanged import getTheNewSignUrl
from bllose.tasks.commons.leaseContract import getSignUrl
from bllose.tasks.commons.auth4Info import establish_contract_file
from bllose.esign.Client import eqb_sign
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress

from bllose.esign.eqb_functions import set_title


@with_default_category('e签宝任务')
class AutoLoadTaskSet(CommandSet):
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.env = 'test'
        set_title("e签宝 -> 测试环境")
        self.local_save_path = '/temp/download'

    contractinfo_parser = cmd2.Cmd2ArgumentParser()
    # contractinfo_parser.add_argument('-o', '--orgId', action='store_true', help='通过orgId进行查询')
    contractinfo_parser.add_argument('param', nargs=1, help='签约请求参数:companyName,mobile')
    @cmd2.with_argparser(contractinfo_parser)
    @cmd2.with_category('e签宝任务 - 信息使用授权书')
    def do_contractinfo(self, args):
        params = args.param[-1]
        paramSplit = params.split(',')
        companyName = paramSplit[0]
        mobile = paramSplit[1]
        id = paramSplit[2]
        if self.env == 'pro':
            templateId = '0d211ef74d3841458162539125129898'
        else:
            templateId = '7a6db35bdca948e5a434c77cd31d94d4'

        flowId, shortUrl, fileId = establish_contract_file(companyName=companyName, templateId=templateId, mobile=mobile, env=self.env)

        sql = f"update `xk-contract`.sf_sign_flow set third_flow_id = '{flowId}', sign_flow_phase = 'NEW', sign_url = '{shortUrl}', third_file_id = '{fileId}' where id = {id}; "

        conclusion = Text()
        conclusion.append("签约地址: ", style="bold yellow")
        conclusion.append(shortUrl, style="bold green")
        conclusion.append("\n")
        conclusion.append("工单SQL: ", style="bold yellow")
        conclusion.append(sql, style="bold green")
        panel = Panel(conclusion, title="信息使用授权书")
        self.console.print(panel)

    @cmd2.with_category('e签宝任务 - 信息使用授权书')
    def do_contractinfosql(self, args):
        self.console.print("select concat_ws(',', company_name, ex_customer_mobile, id)")
        self.console.print("from (")
        self.console.print("select a.ex_customer_name, ")
        self.console.print("AES_DECRYPT(from_base64(substr(a.ex_customer_mobile,3)),from_base64('XDM4Vvla+6kxP++4yOXb5A==')) 'ex_customer_mobile', ")
        self.console.print("AES_DECRYPT(from_base64(substr(a.ex_customer_idno,3)),from_base64('XDM4Vvla+6kxP++4yOXb5A==')) 'ex_customer_idno',")
        self.console.print("d.company_name, e.id, e.template_code, e.image_code ")
        self.console.print("from `xk-order`.`order` a")
        self.console.print("left join `xk-order`.`order_product_config` b on a.order_no = b.order_no and b.is_delete = false")
        self.console.print("left join `xk-order`.`product_company` d on b.project_company_id = d.id and d.is_delete = false")
        self.console.print("left join `xk-contract`.`sf_sign_flow` e on a.order_no = e.object_no and e.is_delete = false")
        self.console.print("where a.is_delete = false")
        self.console.print("and e.scene_code = 'PCI001'")
        self.console.print("and e.image_code = 'PC001#image1'")
        self.console.print(") final;")

    
    load_parser = cmd2.Cmd2ArgumentParser()
    load_parser.add_argument('-t', '--target', type=str, default='signer', help='指定获取的签约地址所属角色，signer:签署人/农户； cosigner: 共签人/第二位签署人')
    load_parser.add_argument('params', nargs='+', help='其他参数')
    @cmd2.with_argparser(load_parser)
    @cmd2.with_category('e签宝任务')
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



    check_parser = cmd2.Cmd2ArgumentParser()
    check_parser.add_argument('params', nargs='+', help='输入上传文件的绝对路径')
    @cmd2.with_argparser(check_parser)
    @cmd2.with_category('e签宝任务')
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

    @cmd2.with_category('e签宝任务')
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

    contract_parser = cmd2.Cmd2ArgumentParser()
    contract_parser.add_argument('params', nargs=4, help='发起签约的参数有且只能有四个，顺序为:社会统一信用代码、身份证、合同服务签约流水id, 文件id\r\n前三个参数使用命令:sql获取')
    @cmd2.with_argparser(contract_parser)
    @cmd2.with_category('e签宝任务')
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
        """
        credit_code, id_card, id, file_id = args.params
        signFlowId, fileId, shortUrl = getSignUrl(orgIdCard=credit_code, creditId=id_card, fileId=file_id, env=self.env)
        self.console.print(f'新的签约地址: {shortUrl}')
        sql = f"update `xk-contract`.`sf_sign_flow` set third_flow_id = '{signFlowId}', sign_flow_phase = 'NEW',  third_file_id = '{fileId}', sign_url = '{shortUrl}' where is_delete = 0 and "
        self.console.print(f'[green]{sql}[/green]id = [bold red]{id}[/bold red]')
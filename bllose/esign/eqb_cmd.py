import cmd2
import logging
from bllose.tasks.commons.GetSignUrlAfterMobileChanged import getTheNewSignUrl
from bllose.esign.Client import eqb_sign
from bllose.esign.esign_enums.file_status import FileStatus
from bllose.esign.esign_enums.env_enum import EqbEnum
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.style import Style
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


if __name__ == '__main__':
    eqb_cmd().cmdloop()
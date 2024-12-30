import cmd2
import json
from rich.console import Console
from bllose.helper.timeHelper import formatter
from bllose.helper.JsonHelper import deep_clean_null
from bllose.cmds.commandSets.sys_command_sets import CustomInitCommandSet


class bllose_cmd(cmd2.Cmd):
    intro = "工具集"
    prompt = 'bllose> '

    def __init__(self, *args, command_sets=None, **kwargs):
        # 将command_sets加入到kwargs中以便传递给父类构造函数
        if command_sets is not None:
            kwargs['command_sets'] = command_sets

        super().__init__(*args, **kwargs)
        
        self.console = Console()
        self.aliases['time'] = 'format'

    json_parser = cmd2.Cmd2ArgumentParser()
    json_parser.add_argument('params', nargs=1, help='json字符串中null对象全部清除掉')
    @cmd2.with_argparser(json_parser)
    @cmd2.with_category('小工具')
    def do_json(self, args):
        target = args.params[0]
        if target is None or len(target) < 1:
            return
        targetJson = json.loads(target)
        self.console.print(f'[green]{deep_clean_null(targetJson)}[/green]')

    format_parser = cmd2.Cmd2ArgumentParser()
    format_parser.add_argument('params', nargs=1, help='将时间戳转化为格式化的时间字符串')
    @cmd2.with_argparser(format_parser)
    @cmd2.with_category('小工具')
    def do_format(self, args):
        """
        将时间戳
        """
        try:
            timestamp = int(args.params[0])
        except ValueError:
            self.console.print(f'[red]入参->{args.params[0]}<-无法解析为时间戳[/red]')
            return
        self.console.print(f'[green]{formatter(timestamp)}[/green]')


if __name__ == '__main__':    
    my_command = CustomInitCommandSet('bllose')
    bllose_cmd(command_sets=[my_command]).cmdloop()
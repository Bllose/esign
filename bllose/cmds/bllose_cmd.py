import cmd2
import os
import json
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.style import Style
from rich.progress import Progress
from bllose.helper.timeHelper import formatter
from bllose.helper.JsonHelper import deep_clean_null

class bllose_cmd(cmd2.Cmd):
    intro = "工具集"
    prompt = 'bllose> '

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.update_prompt()
        self.aliases['time'] = 'format'

    json_parser = cmd2.Cmd2ArgumentParser()
    json_parser.add_argument('params', nargs=1, help='json字符串中null对象全部清除掉')
    @cmd2.with_argparser(json_parser)
    def do_json(self, args):
        target = args.params[0]
        if target is None or len(target) < 1:
            return
        targetJson = json.loads(target)
        self.console.print(f'[green]{deep_clean_null(targetJson)}[/green]')

    format_parser = cmd2.Cmd2ArgumentParser()
    format_parser.add_argument('params', nargs=1, help='将时间戳转化为格式化的时间字符串')
    @cmd2.with_argparser(format_parser)
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
    
    def update_prompt(self):
        """更新提示符以显示当前工作目录"""
        current_dir = os.getcwd()
        self.prompt = f"bllose {current_dir}> "

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


if __name__ == '__main__':
    bllose_cmd().cmdloop()            
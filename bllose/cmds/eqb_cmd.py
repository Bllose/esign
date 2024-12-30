import cmd2
from cmd2 import with_category, with_argparser
import os
from pathlib import Path
from rich.console import Console
from bllose.esign.eqb_functions import set_title
from bllose.cmds.commandSets.workplace_command_sets import AutoLoadCommandSet


class eqb_cmd(cmd2.Cmd):
    intro = "e签宝相关功能"
    prompt = 'e签宝> '

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.env = 'test'
        set_title("e签宝 -> 测试环境")
        self.update_prompt()

        # 定义别名
        self.aliases['flowid'] = 'flowId'
        self.aliases['fileid'] = 'fileId'


    def update_prompt(self):
        """更新提示符以显示当前工作目录"""
        current_dir = os.getcwd()
        self.prompt = f"e签宝 {current_dir}> "

    @with_category('系统操作')
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

    @with_category('系统操作')
    def do_pwd(self, arg):
        """Print the current working directory.

        Usage: pwd
        """
        print(os.getcwd())


    ls_parser = cmd2.Cmd2ArgumentParser()
    ls_parser.add_argument('directory', nargs='?', default='.', help='Directory to list')
    ls_parser.add_argument('-l', action='store_true', help='use a long listing format')
    ls_parser.add_argument('-a', '--all', action='store_true', help='do not ignore entries starting with .')
    ls_parser.add_argument('params', nargs='*', help='路径地址')
    @with_category('系统操作')
    @with_argparser(ls_parser)
    def do_ls(self, arg):
        try:
            directory = arg.directory

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
    eqb_cmd().cmdloop()
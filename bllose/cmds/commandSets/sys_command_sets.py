import cmd2
import os
from rich.console import Console
from pathlib import Path
from cmd2 import CommandSet, with_default_category, with_category, with_argparser

@with_default_category('系统操作')
class CustomInitCommandSet(CommandSet):
    def __init__(self, prompt_head, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.prompt_head = prompt_head
    
    def on_register(self, cmd:  cmd2.Cmd):
        """当 CommandSet 被注册时调用此方法"""
        super().on_register(cmd)
        self.update_prompt()

    def update_prompt(self):
        """更新提示符以显示当前工作目录"""
        current_dir = os.getcwd()
        self._cmd.prompt = f"{self.prompt_head} {current_dir}> "

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
                print(f"Directory not found: {new_dir}")
            except NotADirectoryError:
                print(f"Not a directory: {new_dir}")
            except PermissionError:
                print(f"Permission denied: {new_dir}")
            except Exception as e:
                print(f"Failed to change directory: {e}")

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
    @with_argparser(ls_parser)
    def do_ls(self, arg):
        try:
            directory = arg.directory

            target_dir = Path(directory)
            if not target_dir.exists():
                print(f"Directory does not exist: {target_dir}")
                return

            if not target_dir.is_dir():
                print(f"Not a directory: {target_dir}")
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
            print(f"Failed to list directory: {e}")
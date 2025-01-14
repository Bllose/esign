import cmd2
from bllose.cmds.commandSets.sys_command_sets import CustomInitCommandSet
from bllose.cmds.commandSets.eqb_command_sets import AutoLoadCommandSet
from bllose.cmds.commandSets.eqb_task_sets import AutoLoadTaskSet

class eqb_cmd(cmd2.Cmd):
    intro = "e签宝相关功能"
    prompt = 'e签宝> '

    def __init__(self, *args, command_sets=None, **kwargs):
        # 将command_sets加入到kwargs中以便传递给父类构造函数
        if command_sets is not None:
            kwargs['command_sets'] = command_sets
        super().__init__(*args, **kwargs)

        # 定义别名
        self.aliases['flowid'] = 'flowId'
        self.aliases['fileid'] = 'fileId'

if __name__ == '__main__':
    my_command = CustomInitCommandSet('e签宝')
    eqb_cmd(command_sets=[my_command]).cmdloop()
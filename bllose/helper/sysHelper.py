import psutil


def main():
    port = input("请输入要检查的端口号: ")
    port = int(port)
    found = False
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            found = True
            pid = conn.pid
            process = psutil.Process(pid)
            print(f"应用程序名称: {process.name()}")
            print(f"应用程序路径: {process.exe()}")
            print(f"进程 ID: {pid}")
            choice = input("是否杀死该进程? (y/n): ")
            if choice.lower() == 'y':
                try:
                    process.kill()
                    print("进程已成功杀死。")
                except psutil.NoSuchProcess:
                    print("进程已经不存在。")
                except psutil.AccessDenied:
                    print("没有权限杀死该进程。")
                except Exception as e:
                    print(f"杀死进程时出错: {e}")
    if not found:
        print(f"未找到占用端口 {port} 的应用程序。")


if __name__ == "__main__":
    main()
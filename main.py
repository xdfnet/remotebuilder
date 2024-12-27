import os
import sys
import logging
import argparse
from src.config import ConfigManager
from src.core import LoggerSetup
from src.packager import PackageManager, RemoteManager

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Smart Packager - 跨平台打包工具')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--entry-script', required=True, help='入口脚本路径')
    parser.add_argument('--workspace', required=True, help='工作空间路径')
    parser.add_argument('--platform', choices=['windows', 'macos', 'all'], default='all', help='目标平台')
    parser.add_argument('--server', help='Windows打包服务器配置')
    parser.add_argument('--interactive', '-i', action='store_true', help='启用交互式模式')
    parser.add_argument('--machine', choices=['1', '2', '3'], help='指定打包机器')
    return parser.parse_args()

def select_machine(config_manager):
    """选择要操作的机器"""
    machines = config_manager.get_machines_config()
    print("\n------选择打包机器------")
    print("可用的机器列表：")
    for key, machine in machines.items():
        print(f"{key}. {machine['name']}")
    
    while True:
        choice = input("\n请选择机器编号 (1/2/3): ").strip()
        if choice in machines:
            config = machines[choice]["config"]
            print(f"\n已选择: {machines[choice]['name']}")
            return config
        print("无效的选择，请重试")

def select_build_type():
    """选择打包类型"""
    print("\n------选择打包类型------")
    print("1. 仅打包 Windows")
    print("2. 仅打包 macOS")
    print("3. 同时打包 Windows 和 macOS")
    print("0. 退出程序")
    
    while True:
        choice = input("\n请选择打包类型 (0/1/2/3): ").strip()
        if choice in ['0', '1', '2', '3']:
            return choice
        print("无效的选择，请重试")

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager(args.config)
        
        # 设置日志系统
        LoggerSetup.setup_logging(config_manager.get_logging_config())

        if args.interactive:
            # 交互式模式
            build_type = select_build_type()
            if build_type == '0':
                print("\n程序已退出")
                return
            
            if build_type in ['1', '3']:  # Windows 或全部
                machine_config = select_machine(config_manager)
                args.server = machine_config
                args.platform = 'windows' if build_type == '1' else 'all'
            elif build_type == '2':  # 仅 macOS
                args.platform = 'macos'
        
        # 验证入口脚本
        entry_script = args.entry_script
        if not os.path.exists(entry_script):
            logging.error(f"Entry script not found: {entry_script}")
            sys.exit(1)
            
        # 设置工作空间
        workspace_path = args.workspace
        if not os.path.exists(workspace_path):
            logging.error(f"Workspace not found: {workspace_path}")
            sys.exit(1)
            
        # 根据平台选择执行打包
        if args.platform in ['windows', 'all']:
            # Windows打包
            remote_manager = RemoteManager(args.server)
            if not remote_manager:
                if args.platform == 'windows':
                    sys.exit(1)
            else:
                windows_packager = PackageManager(
                    remote_manager,
                    config_manager.get_packaging_config('windows'),
                    workspace_path
                )
                
                if not windows_packager.verify_resources(config_manager.get_packaging_config('windows')):
                    logging.error("Windows resource verification failed")
                    if args.platform == 'windows':
                        sys.exit(1)
                elif not windows_packager.build_windows(entry_script):
                    logging.error("Windows build failed")
                    if args.platform == 'windows':
                        sys.exit(1)

        if args.platform in ['macos', 'all']:
            # macOS打包
            if not PackageManager.build_mac_package(entry_script, workspace_path):
                logging.error("macOS build failed")
                if args.platform == 'macos':
                    sys.exit(1)

    except Exception as e:
        logging.error(f"Build failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
"""
配置系统级进度监控任务
"""

import json
import subprocess

# 初始化监控器
exec(open('progress_monitor.py', 'r', encoding='utf-8').read())

monitor = ProgressMonitor()

# 清空现有任务
monitor.config['tasks'] = {}

print("="*50)
print("  配置系统级进度监控任务")
print("="*50)
print()

# 任务 1：Docker Desktop
monitor.add_task(
    task_name='Docker Desktop',
    process_name='Docker Desktop'
)

# 任务 2：Docker 后端
monitor.add_task(
    task_name='Docker Backend',
    process_name='com.docker.backend.exe'
)

# 任务 3：WSL Ubuntu
monitor.add_task(
    task_name='WSL Ubuntu',
    process_name=None,  # WSL 通过 wsl 命令检查
    check_command='wsl -l -v'
)

# 任务 4：向日葵
monitor.add_task(
    task_name='Sunlogin (向日葵)',
    process_name='SunloginClient.exe'
)

# 任务 5：Docker CLI 测试
monitor.add_task(
    task_name='Docker CLI',
    process_name=None,
    check_command='docker ps'
)

# 任务 6：长时间运行进程（超过10分钟）
# 可以通过外部监控添加

print("✓ 已添加监控任务：")
print()
print("1. Docker Desktop - 监控进程运行状态")
print("2. Docker Backend - 监控后端服务")
print("3. WSL Ubuntu - 监控 Linux 发行版状态")
print("4. Sunlogin (向日葵) - 监控远程工具")
print("5. Docker CLI - 监控命令行工具")
print()
print("="*50)
print()
print("配置已保存！现在可以设置定时任务...")
print()

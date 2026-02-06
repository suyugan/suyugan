"""
创建每3分钟运行一次的定时任务
"""

import json
import subprocess
import sys

print("=" * 50)
print("  Create Scheduled Task (Every 3 Minutes)")
print("=" * 50)
print()

# 检查配置文件
config_file = "progress_monitor_config.json"
monitor_script = "progress_monitor.py"

try:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    interval = config.get('monitor_interval_minutes', 3)
    enabled = config.get('enabled', True)

    print(f"Monitor Interval: {interval} minutes")
    print(f"Enabled: {enabled}")
    print()
    print("Scheduled Task Configuration:")
    print()

    # 创建 Windows 任务计划程序任务
    task_name = "OpenClaw_Progress_Monitor_3min"
    task_command = f'python "{sys.path[0]}\\{monitor_script}"'

    # 获取当前目录的绝对路径
    working_dir = sys.path[0]

    # 创建 schtasks 命令
    # SC: Create（创建）
    /TN: 任务名称（TaskName）
    /TR: 每 X 分钟运行（Schedule / MINUTE）
    /MO: 开始时间（Modify）
    /SC: 调度器类型（Schedule）
    /F: 强制创建任务（Force）
    /RL: 最高优先级（Run Level）
    /ST: 启动目录（Start In）

    schtasks_command = f'''schtasks /Create /TN "{task_name}" /TR "{interval}" /SC MINUTE /MO 00:00 /F /RL HIGHEST /ST "{working_dir}" /TR /SC MINUTE /F /RL HIGHEST /ST "{working_dir}" /C /C python "{working_dir}\\{monitor_script}"'''

    print(f"Task Name: {task_name}")
    print(f"Interval: Every {interval} minutes")
    print(f"Command: {task_command}")
    print(f"Working Dir: {working_dir}")
    print()

    # 执行创建任务
    print("Creating scheduled task...")
    print()

    result = subprocess.run(
        f'schtasks /Create /TN "{task_name}" /TR "{interval}" /SC MINUTE /F /RL HIGHEST /ST "{working_dir}" /C python "{working_dir}\\{monitor_script}"',
        shell=True,
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    print("Command Output:")
    print(result.stdout)
    if result.stderr:
        print("Error:")
        print(result.stderr)
    print()

    if result.returncode == 0:
        print("=" * 50)
        print("  Scheduled Task Created Successfully!")
        print("=" * 50)
        print()
        print("Task will run every 3 minutes")
        print(f"Task Name: {task_name}")
        print()
        print("To check task: schtasks /Query /TN OpenClaw_Progress_Monitor_3min")
        print("To delete task: schtasks /Delete /TN OpenClaw_Progress_Monitor_3min")
        print()
        print("=" * 50)
    else:
        print("=" * 50)
        print("  Failed to Create Scheduled Task")
        print("=" * 50)

    # 显示所有已配置的任务
    print()
    print("Configured Monitor Tasks:")
    print("-" * 50)
    for task_name, task_config in config.get('tasks', {}).items():
        process = task_config.get('process_name', 'N/A')
        command = task_config.get('check_command', 'N/A')
        print(f"Task: {task_name}")
        print(f"  Process: {process}")
        print(f"  Check Command: {command if command else 'N/A'}")
        print()

    print("-" * 50)

except FileNotFoundError:
    print(f"Config file not found: {config_file}")
    print("Please run setup_monitor.py first")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

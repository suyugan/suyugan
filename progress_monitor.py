"""
系统级进度监控脚本
自动每3分钟汇报一次进度
"""

import json
import subprocess
import time
from datetime import datetime

class ProgressMonitor:
    def __init__(self):
        self.config_file = "progress_monitor_config.json"
        self.log_file = "progress_monitor.log"

        # 加载配置
        self.load_config()

    def load_config(self):
        """加载监控配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # 默认配置
            self.config = {
                'monitor_interval_minutes': 3,  # 监控间隔（分钟）
                'enabled': True,
                'tasks': {}
            }
            self.save_config()

    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def add_task(self, task_name, process_name=None, check_command=None):
        """添加监控任务"""
        self.config['tasks'][task_name] = {
            'process_name': process_name,
            'check_command': check_command,
            'last_report': None,
            'running': False
        }
        self.save_config()

    def remove_task(self, task_name):
        """移除监控任务"""
        if task_name in self.config['tasks']:
            del self.config['tasks'][task_name]
            self.save_config()

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(log_entry.strip())

    def check_process(self, process_name):
        """检查进程是否在运行"""
        try:
            result = subprocess.run(
                ['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                # 检查输出中是否包含进程名
                if process_name.lower() in result.stdout.lower():
                    return True
            return False
        except Exception as e:
            self.log(f"检查进程 {process_name} 时出错: {e}")
            return False

    def run_check_command(self, command):
        """运行检查命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            self.log(f"执行命令 {command} 时出错: {e}")
            return False, "", str(e)

    def report(self, task_name, status, message, progress=0):
        """生成进度报告"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = {
            'timestamp': timestamp,
            'task': task_name,
            'status': status,
            'message': message,
            'progress': progress
        }

        # 记录日志
        self.log(f"[{task_name}] {status}: {message} (进度: {progress}%)")

        # 更新配置中的最后汇报时间
        if task_name in self.config['tasks']:
            self.config['tasks'][task_name]['last_report'] = timestamp
            self.save_config()

        return report

    def monitor(self):
        """执行一次监控检查"""
        if not self.config.get('enabled', True):
            self.log("监控已禁用")
            return []

        reports = []

        for task_name, task_config in self.config['tasks'].items():
            # 检查进程
            process_name = task_config.get('process_name')
            if process_name:
                is_running = self.check_process(process_name)

                if is_running and not task_config['running']:
                    # 进程刚刚开始运行
                    self.report(task_name, 'STARTED', f'进程 {process_name} 已启动')
                    task_config['running'] = True

                elif not is_running and task_config['running']:
                    # 进程刚刚停止
                    self.report(task_name, 'STOPPED', f'进程 {process_name} 已停止')
                    task_config['running'] = False
                elif is_running:
                    # 进程仍在运行
                    self.report(task_name, 'RUNNING', f'进程 {process_name} 正在运行')

                reports.append({
                    'task': task_name,
                    'process_name': process_name,
                    'is_running': is_running
                })

            # 运行检查命令
            check_command = task_config.get('check_command')
            if check_command:
                success, stdout, stderr = self.run_check_command(check_command)

                if success:
                    self.report(task_name, 'SUCCESS', f'命令执行成功: {check_command[:50]}...', 100)
                else:
                    self.report(task_name, 'FAILED', f'命令执行失败: {stderr[:50]}...', 0)

                reports.append({
                    'task': task_name,
                    'check_command': check_command,
                    'success': success,
                    'stdout': stdout[:200] if stdout else '',
                    'stderr': stderr[:200] if stderr else ''
                })

        self.save_config()
        return reports


def main():
    """主函数"""
    monitor = ProgressMonitor()

    print("="*50)
    print("  系统级进度监控")
    print("="*50)
    print()

    # 监控检查
    reports = monitor.monitor()

    # 输出报告
    if reports:
        print("监控报告：")
        print("="*50)

        for report in reports:
            if 'is_running' in report:
                status = "✅ 运行中" if report['is_running'] else "❌ 已停止"
                print(f"进程 [{report['process_name']}]: {status}")

            elif 'success' in report:
                status = "✅ 成功" if report['success'] else "❌ 失败"
                print(f"命令 [{report['check_command'][:30]}...]: {status}")

                if report.get('stdout'):
                    print(f"  输出: {report['stdout']}")
                if report.get('stderr'):
                    print(f"  错误: {report['stderr']}")

        print("="*50)
        print()

    # 输出 JSON 格式（供程序解析）
    print("JSON_OUTPUT_START")
    print(json.dumps({
        'success': True,
        'reports': reports,
        'timestamp': datetime.now().isoformat()
    }, ensure_ascii=False))
    print("JSON_OUTPUT_END")


if __name__ == "__main__":
    main()

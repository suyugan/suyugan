#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 助手个人 Dashboard - 后端 API
Flask + SQLite
端口: 5052
"""

import os
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

# 配置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'dashboard.db'
STATUS_FILE = DATA_DIR / 'status.json'
OPENCLAW_DIR = Path.home() / '.openclaw'
WORKSPACE_DIR = OPENCLAW_DIR / 'workspace'

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 任务表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            column_name TEXT DEFAULT 'todo',
            description TEXT DEFAULT '',
            steps TEXT DEFAULT '[]',
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # 活动日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            message TEXT,
            time TEXT
        )
    ''')
    
    # Token 用量统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            agent TEXT DEFAULT 'main',
            api_calls INTEGER DEFAULT 0,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cache_read INTEGER DEFAULT 0,
            cache_write INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            total_cost REAL DEFAULT 0.0,
            created_at TEXT
        )
    ''')
    
    # 成本配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cost_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            input_cost_per_1m REAL DEFAULT 0,
            output_cost_per_1m REAL DEFAULT 0,
            cache_read_per_1m REAL DEFAULT 0,
            cache_write_per_1m REAL DEFAULT 0,
            updated_at TEXT
        )
    ''')
    
    # 备份日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backup_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            status TEXT,
            message TEXT,
            created_at TEXT
        )
    ''')
    
    # 记忆更新日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            source TEXT,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # 初始化状态文件
    if not STATUS_FILE.exists():
        save_status({
            'status': 'idle',
            'current_task': '待命中',
            'last_active': datetime.now().isoformat()
        })


def load_status():
    """加载状态"""
    if STATUS_FILE.exists():
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'status': 'idle', 'current_task': '待命中', 'last_active': None}


def save_status(status):
    """保存状态"""
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def log_activity(activity_type, message):
    """记录活动"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO activity (type, message, time) VALUES (?, ?, ?)',
        (activity_type, message, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


# ==================== 静态文件 ====================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


# ==================== 状态 API ====================

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取状态"""
    status = load_status()
    # 检查 Gateway 进程
    status['online'] = check_gateway_online()
    return jsonify(status)


@app.route('/api/status', methods=['POST'])
def update_status():
    """更新状态"""
    data = request.json
    status = load_status()
    
    if 'status' in data:
        status['status'] = data['status']
    if 'current_task' in data:
        status['current_task'] = data['current_task']
    
    status['last_active'] = datetime.now().isoformat()
    save_status(status)
    
    log_activity('status', f"状态更新: {status['status']} - {status['current_task']}")
    return jsonify({'success': True, 'status': status})


def check_gateway_online():
    """检查 Gateway 是否在线"""
    import subprocess
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq node.exe'],
            capture_output=True, text=True, timeout=5
        )
        return 'node.exe' in result.stdout
    except:
        return False


# ==================== 任务 API ====================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取所有任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    # 按列分组
    tasks = {
        'todo': [],
        'inProgress': [],
        'done': [],
        'archived': []
    }
    
    for row in rows:
        task = dict(row)
        task['steps'] = json.loads(task['steps']) if task['steps'] else []
        column = task.get('column_name', 'todo')
        if column in tasks:
            tasks[column].append(task)
    
    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """创建任务"""
    data = request.json
    task_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    # 简单的步骤拆解（可以后续接入 LLM）
    steps = data.get('steps', [])
    if not steps and data.get('title'):
        steps = [{'text': '开始执行', 'done': False}, {'text': '完成任务', 'done': False}]
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (id, title, date, priority, column_name, description, steps, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        task_id,
        data.get('title', ''),
        data.get('date', now[:10]),
        data.get('priority', 'medium'),
        data.get('column_name', 'todo'),
        data.get('description', ''),
        json.dumps(steps, ensure_ascii=False),
        now,
        now
    ))
    conn.commit()
    conn.close()
    
    log_activity('task', f"创建任务: {data.get('title', '')}")
    return jsonify({'success': True, 'id': task_id})


@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务"""
    data = request.json
    now = datetime.now().isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取当前任务
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    
    task = dict(row)
    
    # 更新字段
    for key in ['title', 'date', 'priority', 'column_name', 'description']:
        if key in data:
            task[key] = data[key]
    
    if 'steps' in data:
        task['steps'] = json.dumps(data['steps'], ensure_ascii=False)
    
    cursor.execute('''
        UPDATE tasks SET title=?, date=?, priority=?, column_name=?, description=?, steps=?, updated_at=?
        WHERE id=?
    ''', (task['title'], task['date'], task['priority'], task['column_name'], 
          task['description'], task['steps'], now, task_id))
    conn.commit()
    conn.close()
    
    log_activity('task', f"更新任务: {task['title']}")
    return jsonify({'success': True})


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT title FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    title = row['title'] if row else ''
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    log_activity('task', f"删除任务: {title}")
    return jsonify({'success': True})


@app.route('/api/tasks/<task_id>/step/<int:step_index>', methods=['POST'])
def toggle_step(task_id, step_index):
    """切换步骤完成状态"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT steps FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    
    steps = json.loads(row['steps']) if row['steps'] else []
    if 0 <= step_index < len(steps):
        steps[step_index]['done'] = not steps[step_index].get('done', False)
    
    cursor.execute('UPDATE tasks SET steps=?, updated_at=? WHERE id=?',
                   (json.dumps(steps, ensure_ascii=False), datetime.now().isoformat(), task_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'steps': steps})


# ==================== 定时任务 API ====================

@app.route('/api/cron', methods=['GET'])
def get_cron_jobs():
    """获取定时任务列表"""
    cron_file = OPENCLAW_DIR / 'cron' / 'jobs.json'
    if cron_file.exists():
        with open(cron_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        return jsonify(jobs)
    return jsonify([])


# ==================== Token 用量 API ====================

@app.route('/api/usage', methods=['GET'])
def get_usage():
    """获取用量统计"""
    conn = get_db()
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT * FROM usage_stats WHERE date = ?', (today,))
    row = cursor.fetchone()
    
    if row:
        usage = dict(row)
    else:
        usage = {
            'date': today,
            'api_calls': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0,
            'total_cost': 0.0
        }
    
    conn.close()
    return jsonify(usage)


@app.route('/api/usage/chart', methods=['GET'])
def get_usage_chart():
    """获取图表数据（最近14天）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, total_tokens, total_cost 
        FROM usage_stats 
        ORDER BY date DESC 
        LIMIT 14
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    data = [dict(row) for row in rows]
    data.reverse()
    return jsonify(data)


# ==================== 记忆系统 API ====================

@app.route('/api/memory', methods=['GET'])
def get_memory():
    """获取记忆内容"""
    memory_file = WORKSPACE_DIR / 'MEMORY.md'
    if memory_file.exists():
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content})
    return jsonify({'content': ''})


@app.route('/api/memory', methods=['POST'])
def save_memory():
    """保存记忆内容"""
    data = request.json
    memory_file = WORKSPACE_DIR / 'MEMORY.md'
    
    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(data.get('content', ''))
    
    # 记录更新日志
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO memory_log (content, source, created_at) VALUES (?, ?, ?)',
        ('记忆内容更新', 'editor', datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    
    log_activity('system', '记忆内容已更新')
    return jsonify({'success': True})


# ==================== 技能列表 API ====================

@app.route('/api/skills', methods=['GET'])
def get_skills():
    """获取技能列表"""
    skills = []
    
    # 系统技能
    system_skills_dir = Path(r'C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\skills')
    if system_skills_dir.exists():
        for skill_dir in system_skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / 'SKILL.md'
                if skill_md.exists():
                    skills.append({
                        'name': skill_dir.name,
                        'type': 'system',
                        'path': str(skill_dir)
                    })
    
    # 用户技能
    user_skills_dir = WORKSPACE_DIR / 'skills'
    if user_skills_dir.exists():
        for skill_dir in user_skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / 'SKILL.md'
                if skill_md.exists():
                    skills.append({
                        'name': skill_dir.name,
                        'type': 'user',
                        'path': str(skill_dir)
                    })
    
    return jsonify(skills)


# ==================== 活动日志 API ====================

@app.route('/api/activity', methods=['GET'])
def get_activity():
    """获取最近动态"""
    limit = request.args.get('limit', 20, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM activity ORDER BY time DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in rows])


# ==================== 健康检查 ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()})


# ==================== 启动 ====================

if __name__ == '__main__':
    init_db()
    print('Dashboard 启动中...')
    print('访问地址: http://localhost:5052')
    app.run(host='0.0.0.0', port=5052, debug=True)

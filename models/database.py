"""
数据库模型定义
"""
import sqlite3
import os
from datetime import datetime


class Database:
    """数据库管理类"""

    def __init__(self, db_path='holiday_manager.db'):
        """初始化数据库连接"""
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def get_connection(self):
        """获取数据库连接"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 创建假期类别表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leave_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                total_days REAL NOT NULL DEFAULT 0,
                expire_date TEXT,
                color TEXT NOT NULL DEFAULT '#4A90E2',
                is_system INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')

        # 创建系统设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                overtime_expire_date TEXT NOT NULL DEFAULT '12-31',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # 创建加班记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS overtime_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                overtime_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                equivalent_days REAL NOT NULL,
                used_days REAL NOT NULL DEFAULT 0,
                is_expired INTEGER NOT NULL DEFAULT 0,
                description TEXT,
                created_at TEXT NOT NULL
            )
        ''')

        # 创建假期使用记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leave_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                leave_date TEXT NOT NULL,
                leave_type_id INTEGER NOT NULL,
                leave_type_name TEXT NOT NULL,
                days_used REAL NOT NULL,
                start_time TEXT,
                end_time TEXT,
                overtime_id INTEGER,
                description TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (leave_type_id) REFERENCES leave_types(id),
                FOREIGN KEY (overtime_id) REFERENCES overtime_records(id)
            )
        ''')

        conn.commit()

        # 初始化默认数据
        self._init_default_data(cursor, conn)

    def _init_default_data(self, cursor, conn):
        """初始化默认数据"""
        # 检查是否已有系统设置
        cursor.execute('SELECT COUNT(*) FROM system_settings')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO system_settings (overtime_expire_date, created_at, updated_at)
                VALUES (?, ?, ?)
            ''', ('12-31', datetime.now().isoformat(), datetime.now().isoformat()))

        # 检查是否已有系统假期类别
        cursor.execute('SELECT COUNT(*) FROM leave_types WHERE is_system = 1')
        if cursor.fetchone()[0] == 0:
            # 添加年假
            cursor.execute('''
                INSERT INTO leave_types (name, total_days, expire_date, color, is_system, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('年假', 5, '12-31', '#4A90E2', 1, datetime.now().isoformat()))

            # 添加调休
            cursor.execute('''
                INSERT INTO leave_types (name, total_days, expire_date, color, is_system, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('调休', 0, '12-31', '#7ED321', 1, datetime.now().isoformat()))

        conn.commit()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

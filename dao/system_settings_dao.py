"""
系统设置数据访问对象
"""
from datetime import datetime


class SystemSettingsDAO:
    """系统设置DAO"""

    def __init__(self, db):
        self.db = db

    def get(self):
        """获取系统设置"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM system_settings LIMIT 1')
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_overtime_expire_date(self, expire_date):
        """更新调休过期日期"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE system_settings
            SET overtime_expire_date = ?, updated_at = ?
            WHERE id = 1
        ''', (expire_date, datetime.now().isoformat()))
        conn.commit()
        return cursor.rowcount > 0

    def get_overtime_expire_date(self):
        """获取调休过期日期"""
        settings = self.get()
        return settings['overtime_expire_date'] if settings else '12-31'

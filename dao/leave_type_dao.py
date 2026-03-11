"""
假期类别数据访问对象
"""
from datetime import datetime


class LeaveTypeDAO:
    """假期类别DAO"""

    def __init__(self, db):
        self.db = db

    def get_all(self):
        """获取所有假期类别"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM leave_types ORDER BY is_system DESC, created_at ASC')
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, leave_type_id):
        """根据ID获取假期类别"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM leave_types WHERE id = ?', (leave_type_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_by_name(self, name):
        """根据名称获取假期类别"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM leave_types WHERE name = ?', (name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def create(self, name, total_days=0, expire_date=None, color='#4A90E2', is_system=0):
        """创建假期类别"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leave_types (name, total_days, expire_date, color, is_system, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, total_days, expire_date, color, is_system, datetime.now().isoformat()))
        conn.commit()
        return cursor.lastrowid

    def update(self, leave_type_id, **kwargs):
        """更新假期类别"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # 构建更新语句
        update_fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['name', 'total_days', 'expire_date', 'color']:
                update_fields.append(f'{key} = ?')
                values.append(value)

        if not update_fields:
            return False

        values.append(leave_type_id)
        sql = f"UPDATE leave_types SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount > 0

    def delete(self, leave_type_id):
        """删除假期类别"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM leave_types WHERE id = ? AND is_system = 0', (leave_type_id,))
        conn.commit()
        return cursor.rowcount > 0

    def get_used_days(self, leave_type_id):
        """获取假期类别已使用的天数"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(days_used), 0) as used_days
            FROM leave_records
            WHERE leave_type_id = ?
        ''', (leave_type_id,))
        row = cursor.fetchone()
        return row['used_days'] if row else 0

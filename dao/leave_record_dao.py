"""
假期使用记录数据访问对象
"""
from datetime import datetime


class LeaveRecordDAO:
    """假期使用记录DAO"""

    def __init__(self, db):
        self.db = db

    def get_all(self):
        """获取所有假期使用记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM leave_records
            ORDER BY leave_date DESC, created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, record_id):
        """根据ID获取假期使用记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM leave_records WHERE id = ?', (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_by_type(self, leave_type_id):
        """根据假期类别获取记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM leave_records
            WHERE leave_type_id = ?
            ORDER BY leave_date DESC
        ''', (leave_type_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_by_overtime(self, overtime_id):
        """根据加班记录获取关联的休假记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM leave_records
            WHERE overtime_id = ?
            ORDER BY leave_date DESC
        ''', (overtime_id,))
        return [dict(row) for row in cursor.fetchall()]

    def create(self, leave_date, leave_type_id, leave_type_name, days_used,
               start_time=None, end_time=None, overtime_id=None, description=None):
        """创建假期使用记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leave_records
            (leave_date, leave_type_id, leave_type_name, days_used, start_time, end_time, overtime_id, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (leave_date, leave_type_id, leave_type_name, days_used, start_time, end_time, overtime_id, description, datetime.now().isoformat()))
        conn.commit()
        return cursor.lastrowid

    def update(self, record_id, **kwargs):
        """更新假期使用记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # 构建更新语句
        update_fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['leave_date', 'leave_type_id', 'leave_type_name', 'days_used', 'start_time', 'end_time', 'overtime_id', 'description']:
                update_fields.append(f'{key} = ?')
                values.append(value)

        if not update_fields:
            return False

        values.append(record_id)
        sql = f"UPDATE leave_records SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount > 0

    def delete(self, record_id):
        """删除假期使用记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM leave_records WHERE id = ?', (record_id,))
        conn.commit()
        return cursor.rowcount > 0

    def get_by_date_range(self, start_date, end_date):
        """获取日期范围内的假期使用记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM leave_records
            WHERE leave_date >= ? AND leave_date <= ?
            ORDER BY leave_date ASC
        ''', (start_date, end_date))
        return [dict(row) for row in cursor.fetchall()]

    def get_used_days_by_type(self, leave_type_id):
        """获取指定假期类别的已使用天数"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(days_used), 0) as total_used
            FROM leave_records
            WHERE leave_type_id = ?
        ''', (leave_type_id,))
        row = cursor.fetchone()
        return row['total_used'] if row else 0

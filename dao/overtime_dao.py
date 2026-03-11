"""
加班记录数据访问对象
"""
from datetime import datetime, date


class OvertimeDAO:
    """加班记录DAO"""

    def __init__(self, db):
        self.db = db

    def get_all(self):
        """获取所有加班记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM overtime_records
            ORDER BY overtime_date DESC, created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, overtime_id):
        """根据ID获取加班记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM overtime_records WHERE id = ?', (overtime_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_available(self):
        """获取可用的加班记录（未过期且有剩余天数）"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM overtime_records
            WHERE is_expired = 0 AND equivalent_days > used_days
            ORDER BY overtime_date ASC
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def create(self, overtime_date, start_time, end_time, equivalent_days, description=None):
        """创建加班记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO overtime_records
            (overtime_date, start_time, end_time, equivalent_days, used_days, is_expired, description, created_at)
            VALUES (?, ?, ?, ?, 0, 0, ?, ?)
        ''', (overtime_date, start_time, end_time, equivalent_days, description, datetime.now().isoformat()))
        conn.commit()
        return cursor.lastrowid

    def update(self, overtime_id, **kwargs):
        """更新加班记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # 构建更新语句
        update_fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['overtime_date', 'start_time', 'end_time', 'equivalent_days', 'used_days', 'is_expired', 'description']:
                update_fields.append(f'{key} = ?')
                values.append(value)

        if not update_fields:
            return False

        values.append(overtime_id)
        sql = f"UPDATE overtime_records SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount > 0

    def delete(self, overtime_id):
        """删除加班记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        # 检查是否有关联的休假记录
        cursor.execute('SELECT COUNT(*) FROM leave_records WHERE overtime_id = ?', (overtime_id,))
        if cursor.fetchone()[0] > 0:
            return False
        cursor.execute('DELETE FROM overtime_records WHERE id = ?', (overtime_id,))
        conn.commit()
        return cursor.rowcount > 0

    def get_remaining_days(self, overtime_id):
        """获取加班记录的剩余天数"""
        record = self.get_by_id(overtime_id)
        if record:
            return record['equivalent_days'] - record['used_days']
        return 0

    def get_total_remaining_days(self):
        """获取所有可用加班的总剩余天数"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(equivalent_days - used_days), 0) as total_remaining
            FROM overtime_records
            WHERE is_expired = 0
        ''')
        row = cursor.fetchone()
        return row['total_remaining'] if row else 0

    def mark_expired(self, overtime_id):
        """标记加班记录为已过期"""
        return self.update(overtime_id, is_expired=1)

    def get_by_date_range(self, start_date, end_date):
        """获取日期范围内的加班记录"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM overtime_records
            WHERE overtime_date >= ? AND overtime_date <= ?
            ORDER BY overtime_date ASC
        ''', (start_date, end_date))
        return [dict(row) for row in cursor.fetchall()]

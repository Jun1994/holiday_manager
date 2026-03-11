"""
加班管理视图
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QDateEdit, QTimeEdit, QLineEdit, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QFont, QColor

from utils import calculate_overtime_days, get_remaining_color, format_time


class OvertimeView(QWidget):
    """加班管理视图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.init_ui()
        self.refresh()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 标题和按钮
        header_layout = QHBoxLayout()

        title_label = QLabel('加班记录')
        title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        add_btn = QPushButton('添加加班')
        add_btn.clicked.connect(self.on_add_overtime)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['加班日期', '时间段', '等效天数', '已用天数', '剩余天数', '备注', '操作'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setFont(QFont('Microsoft YaHei', 10))

        layout.addWidget(self.table)

    def refresh(self):
        """刷新数据"""
        records = self.main_window.overtime_dao.get_all()
        self.table.setRowCount(len(records))

        for row, record in enumerate(records):
            # 加班日期
            date_item = QTableWidgetItem(str(record['overtime_date']))
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, date_item)

            # 时间段
            time_str = f"{format_time(record['start_time'])} - {format_time(record['end_time'])}"
            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, time_item)

            # 等效天数
            equiv_item = QTableWidgetItem(f"{record['equivalent_days']:.1f}天")
            equiv_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, equiv_item)

            # 已用天数
            used_item = QTableWidgetItem(f"{record['used_days']:.1f}天")
            used_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, used_item)

            # 剩余天数
            remaining = record['equivalent_days'] - record['used_days']
            remaining_item = QTableWidgetItem(f"{remaining:.1f}天")
            remaining_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # 设置颜色
            if record['is_expired']:
                remaining_item.setForeground(QColor('#999999'))
                remaining_item.setText('已过期')
            else:
                color = QColor(get_remaining_color(remaining))
                remaining_item.setForeground(color)

            self.table.setItem(row, 4, remaining_item)

            # 备注
            desc_item = QTableWidgetItem(record['description'] or '')
            self.table.setItem(row, 5, desc_item)

            # 操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            action_layout.setSpacing(5)

            # 删除按钮
            delete_btn = QPushButton('删除')
            delete_btn.setFixedWidth(60)
            delete_btn.clicked.connect(lambda checked, r=record: self.on_delete_overtime(r))
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 6, action_widget)

    def on_add_overtime(self):
        """添加加班记录"""
        dialog = AddOvertimeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self.main_window.refresh_all()

    def on_delete_overtime(self, record):
        """删除加班记录"""
        # 检查是否有关联的休假记录
        leave_records = self.main_window.leave_record_dao.get_by_overtime(record['id'])
        if leave_records:
            QMessageBox.warning(self, '警告', '该加班记录已有关联的休假记录,无法删除!')
            return

        reply = QMessageBox.question(
            self,
            '确认删除',
            f'确定要删除 {record["overtime_date"]} 的加班记录吗?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.main_window.overtime_dao.delete(record['id']):
                QMessageBox.information(self, '成功', '删除成功!')
                self.refresh()
                self.main_window.refresh_all()
            else:
                QMessageBox.warning(self, '错误', '删除失败!')


class AddOvertimeDialog(QDialog):
    """添加加班对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.overtime_view = parent
        self.main_window = parent.main_window
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('添加加班记录')
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # 表单
        form_layout = QFormLayout()

        # 加班日期
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        form_layout.addRow('加班日期:', self.date_edit)

        # 开始时间
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(9, 0))
        self.start_time_edit.setDisplayFormat('HH:mm')
        form_layout.addRow('开始时间:', self.start_time_edit)

        # 结束时间
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(18, 0))
        self.end_time_edit.setDisplayFormat('HH:mm')
        form_layout.addRow('结束时间:', self.end_time_edit)

        # 备注
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText('可选')
        form_layout.addRow('备注说明:', self.desc_edit)

        layout.addLayout(form_layout)

        # 等效天数预览
        self.days_label = QLabel('等效天数: 0.5天')
        self.days_label.setFont(QFont('Microsoft YaHei', 11, QFont.Weight.Bold))
        layout.addWidget(self.days_label)

        # 连接信号
        self.date_edit.dateChanged.connect(self.update_days_preview)
        self.start_time_edit.timeChanged.connect(self.update_days_preview)
        self.end_time_edit.timeChanged.connect(self.update_days_preview)

        self.update_days_preview()

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def update_days_preview(self):
        """更新等效天数预览"""
        overtime_date = self.date_edit.date().toString('yyyy-MM-dd')
        start_time = self.start_time_edit.time().toString('HH:mm')
        end_time = self.end_time_edit.time().toString('HH:mm')

        days = calculate_overtime_days(overtime_date, start_time, end_time)
        self.days_label.setText(f'等效天数: {days:.1f}天')

    def on_accept(self):
        """确认添加"""
        overtime_date = self.date_edit.date().toString('yyyy-MM-dd')
        start_time = self.start_time_edit.time().toString('HH:mm')
        end_time = self.end_time_edit.time().toString('HH:mm')
        description = self.desc_edit.text().strip() or None

        # 验证时间
        if start_time >= end_time:
            QMessageBox.warning(self, '错误', '结束时间必须大于开始时间!')
            return

        # 计算等效天数
        equivalent_days = calculate_overtime_days(overtime_date, start_time, end_time)

        # 保存到数据库
        try:
            self.main_window.overtime_dao.create(
                overtime_date, start_time, end_time, equivalent_days, description
            )
            QMessageBox.information(self, '成功', '添加成功!')
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'添加失败: {str(e)}')

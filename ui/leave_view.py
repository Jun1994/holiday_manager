"""
休假申请视图
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QDateEdit, QTimeEdit, QLineEdit, QFormLayout,
    QDialogButtonBox, QComboBox, QDoubleSpinBox, QGroupBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QFont

from utils import format_time


class LeaveView(QWidget):
    """休假申请视图"""

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

        title_label = QLabel('休假申请')
        title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # 可用调休提示
        self.overtime_hint_label = QLabel()
        self.overtime_hint_label.setFont(QFont('Microsoft YaHei', 10))
        header_layout.addWidget(self.overtime_hint_label)

        add_btn = QPushButton('申请休假')
        add_btn.clicked.connect(self.on_add_leave)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['休假日期', '假期类型', '使用天数', '时间段', '备注', '操作'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setFont(QFont('Microsoft YaHei', 10))

        layout.addWidget(self.table)

    def refresh(self):
        """刷新数据"""
        # 更新可用调休提示
        total_remaining = self.main_window.overtime_dao.get_total_remaining_days()
        self.overtime_hint_label.setText(f'可用调休: {total_remaining:.1f}天')

        # 获取所有休假记录
        records = self.main_window.leave_record_dao.get_all()
        self.table.setRowCount(len(records))

        for row, record in enumerate(records):
            # 休假日期
            date_item = QTableWidgetItem(str(record['leave_date']))
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, date_item)

            # 假期类型
            type_item = QTableWidgetItem(record['leave_type_name'])
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, type_item)

            # 使用天数
            days_item = QTableWidgetItem(f"{record['days_used']:.1f}天")
            days_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, days_item)

            # 时间段
            if record['start_time'] and record['end_time']:
                time_str = f"{format_time(record['start_time'])} - {format_time(record['end_time'])}"
            else:
                time_str = '全天'
            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, time_item)

            # 备注
            desc_item = QTableWidgetItem(record['description'] or '')
            self.table.setItem(row, 4, desc_item)

            # 操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            action_layout.setSpacing(5)

            # 删除按钮
            delete_btn = QPushButton('删除')
            delete_btn.setFixedWidth(60)
            delete_btn.clicked.connect(lambda checked, r=record: self.on_delete_leave(r))
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 5, action_widget)

    def on_add_leave(self):
        """申请休假"""
        dialog = AddLeaveDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self.main_window.refresh_all()

    def on_delete_leave(self, record):
        """删除休假记录"""
        reply = QMessageBox.question(
            self,
            '确认删除',
            f'确定要删除 {record["leave_date"]} 的休假记录吗?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 如果是调休,需要恢复加班记录的已用天数
            if record['overtime_id']:
                overtime_record = self.main_window.overtime_dao.get_by_id(record['overtime_id'])
                if overtime_record:
                    new_used_days = overtime_record['used_days'] - record['days_used']
                    self.main_window.overtime_dao.update(record['overtime_id'], used_days=new_used_days)

            # 删除休假记录
            if self.main_window.leave_record_dao.delete(record['id']):
                QMessageBox.information(self, '成功', '删除成功!')
                self.refresh()
                self.main_window.refresh_all()
            else:
                QMessageBox.warning(self, '错误', '删除失败!')


class AddLeaveDialog(QDialog):
    """申请休假对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.leave_view = parent
        self.main_window = parent.main_window
        self.selected_overtime_id = None
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('申请休假')
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # 表单
        form_layout = QFormLayout()

        # 假期类型
        self.type_combo = QComboBox()
        self.load_leave_types()
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form_layout.addRow('假期类型:', self.type_combo)

        # 休假日期
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        form_layout.addRow('休假日期:', self.date_edit)

        # 时间段选择
        time_group = QGroupBox('时间段选择')
        time_layout = QVBoxLayout(time_group)

        # 全天/时间段选择
        mode_layout = QHBoxLayout()
        self.all_day_radio = QPushButton('全天')
        self.all_day_radio.setCheckable(True)
        self.all_day_radio.setChecked(True)
        self.all_day_radio.clicked.connect(lambda: self.on_time_mode_changed('all_day'))
        mode_layout.addWidget(self.all_day_radio)

        self.time_period_radio = QPushButton('时间段')
        self.time_period_radio.setCheckable(True)
        self.time_period_radio.clicked.connect(lambda: self.on_time_mode_changed('time_period'))
        mode_layout.addWidget(self.time_period_radio)

        mode_layout.addStretch()
        time_layout.addLayout(mode_layout)

        # 时间段输入
        period_layout = QHBoxLayout()

        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(8, 30))
        self.start_time_edit.setDisplayFormat('HH:mm')
        self.start_time_edit.setEnabled(False)
        period_layout.addWidget(QLabel('开始:'))
        period_layout.addWidget(self.start_time_edit)

        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(12, 0))
        self.end_time_edit.setDisplayFormat('HH:mm')
        self.end_time_edit.setEnabled(False)
        period_layout.addWidget(QLabel('结束:'))
        period_layout.addWidget(self.end_time_edit)

        # 快捷按钮
        self.morning_btn = QPushButton('上午')
        self.morning_btn.clicked.connect(self.set_morning_time)
        self.morning_btn.setEnabled(False)
        period_layout.addWidget(self.morning_btn)

        self.afternoon_btn = QPushButton('下午')
        self.afternoon_btn.clicked.connect(self.set_afternoon_time)
        self.afternoon_btn.setEnabled(False)
        period_layout.addWidget(self.afternoon_btn)

        period_layout.addStretch()
        time_layout.addLayout(period_layout)

        form_layout.addRow(time_group)

        # 休假天数
        self.days_spin = QDoubleSpinBox()
        self.days_spin.setRange(0.5, 30)
        self.days_spin.setValue(1.0)
        self.days_spin.setSingleStep(0.5)
        self.days_spin.setSuffix(' 天')
        form_layout.addRow('休假天数:', self.days_spin)

        # 备注
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText('可选')
        form_layout.addRow('备注说明:', self.desc_edit)

        layout.addLayout(form_layout)

        # 调休加班选择(仅调休类型显示)
        self.overtime_group = QGroupBox('选择加班日期')
        overtime_layout = QVBoxLayout(self.overtime_group)

        self.overtime_list = QListWidget()
        self.overtime_list.itemClicked.connect(self.on_overtime_selected)
        overtime_layout.addWidget(self.overtime_list)

        self.overtime_hint = QLabel('请选择要使用的加班日期')
        overtime_layout.addWidget(self.overtime_hint)

        layout.addWidget(self.overtime_group)
        self.overtime_group.hide()

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_leave_types(self):
        """加载假期类型"""
        leave_types = self.main_window.leave_type_dao.get_all()
        for leave_type in leave_types:
            self.type_combo.addItem(leave_type['name'], leave_type['id'])

    def on_type_changed(self, index):
        """假期类型改变"""
        type_name = self.type_combo.currentText()

        if type_name == '调休':
            self.overtime_group.show()
            self.load_available_overtime()
        else:
            self.overtime_group.hide()
            self.selected_overtime_id = None

    def load_available_overtime(self):
        """加载可用的加班记录"""
        self.overtime_list.clear()
        overtime_records = self.main_window.overtime_dao.get_available()

        for record in overtime_records:
            remaining = record['equivalent_days'] - record['used_days']
            item_text = f"{record['overtime_date']} - 剩余 {remaining:.1f}天"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, record['id'])
            self.overtime_list.addItem(item)

        if not overtime_records:
            self.overtime_hint.setText('无可用加班记录')
        else:
            self.overtime_hint.setText('请选择要使用的加班日期')

    def on_overtime_selected(self, item):
        """加班记录被选择"""
        self.selected_overtime_id = item.data(Qt.ItemDataRole.UserRole)

        # 获取该加班记录的剩余天数
        overtime_record = self.main_window.overtime_dao.get_by_id(self.selected_overtime_id)
        if overtime_record:
            remaining = overtime_record['equivalent_days'] - overtime_record['used_days']
            self.days_spin.setMaximum(remaining)
            self.overtime_hint.setText(f'已选择: {item.text()}')

    def on_time_mode_changed(self, mode):
        """时间模式改变"""
        if mode == 'all_day':
            self.all_day_radio.setChecked(True)
            self.time_period_radio.setChecked(False)
            self.start_time_edit.setEnabled(False)
            self.end_time_edit.setEnabled(False)
            self.morning_btn.setEnabled(False)
            self.afternoon_btn.setEnabled(False)
            self.days_spin.setValue(1.0)
        else:
            self.all_day_radio.setChecked(False)
            self.time_period_radio.setChecked(True)
            self.start_time_edit.setEnabled(True)
            self.end_time_edit.setEnabled(True)
            self.morning_btn.setEnabled(True)
            self.afternoon_btn.setEnabled(True)
            self.days_spin.setValue(0.5)

    def set_morning_time(self):
        """设置上午时间"""
        self.start_time_edit.setTime(QTime(8, 30))
        self.end_time_edit.setTime(QTime(12, 0))

    def set_afternoon_time(self):
        """设置下午时间"""
        self.start_time_edit.setTime(QTime(13, 30))
        self.end_time_edit.setTime(QTime(17, 30))

    def on_accept(self):
        """确认申请"""
        leave_type_id = self.type_combo.currentData()
        leave_type_name = self.type_combo.currentText()
        leave_date = self.date_edit.date().toString('yyyy-MM-dd')
        days_used = self.days_spin.value()
        description = self.desc_edit.text().strip() or None

        # 验证
        if leave_type_name == '调休':
            if not self.selected_overtime_id:
                QMessageBox.warning(self, '错误', '请选择要使用的加班日期!')
                return

            # 检查剩余天数
            overtime_record = self.main_window.overtime_dao.get_by_id(self.selected_overtime_id)
            if not overtime_record:
                QMessageBox.warning(self, '错误', '加班记录不存在!')
                return

            remaining = overtime_record['equivalent_days'] - overtime_record['used_days']
            if days_used > remaining:
                QMessageBox.warning(self, '错误', f'可用天数不足! 剩余 {remaining:.1f}天')
                return
        else:
            # 检查其他假期类型的剩余天数
            leave_type = self.main_window.leave_type_dao.get_by_id(leave_type_id)
            if leave_type:
                used_days = self.main_window.leave_record_dao.get_used_days_by_type(leave_type_id)
                remaining = leave_type['total_days'] - used_days
                if days_used > remaining:
                    QMessageBox.warning(self, '错误', f'可用天数不足! 剩余 {remaining:.1f}天')
                    return

        # 时间段
        start_time = None
        end_time = None
        if not self.all_day_radio.isChecked():
            start_time = self.start_time_edit.time().toString('HH:mm')
            end_time = self.end_time_edit.time().toString('HH:mm')

            if start_time >= end_time:
                QMessageBox.warning(self, '错误', '结束时间必须大于开始时间!')
                return

        # 保存到数据库
        try:
            # 创建休假记录
            self.main_window.leave_record_dao.create(
                leave_date, leave_type_id, leave_type_name, days_used,
                start_time, end_time, self.selected_overtime_id, description
            )

            # 如果是调休,更新加班记录的已用天数
            if self.selected_overtime_id:
                overtime_record = self.main_window.overtime_dao.get_by_id(self.selected_overtime_id)
                new_used_days = overtime_record['used_days'] + days_used
                self.main_window.overtime_dao.update(self.selected_overtime_id, used_days=new_used_days)

            QMessageBox.information(self, '成功', '申请成功!')
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'申请失败: {str(e)}')

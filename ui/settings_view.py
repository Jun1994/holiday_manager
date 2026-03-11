"""
系统设置视图
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QLineEdit, QDoubleSpinBox, QFormLayout,
    QDialogButtonBox, QColorDialog, QDateEdit, QGroupBox,
    QTabWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor


class SettingsView(QWidget):
    """系统设置视图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.init_ui()
        self.refresh()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 标题
        title_label = QLabel('系统设置')
        title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # 打开设置按钮
        open_btn = QPushButton('打开设置')
        open_btn.clicked.connect(self.open_settings_dialog)
        layout.addWidget(open_btn)

        layout.addStretch()

    def refresh(self):
        """刷新数据"""
        pass

    def open_settings_dialog(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec()
        self.main_window.refresh_all()


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_view = parent
        self.main_window = parent.main_window
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('系统设置')
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # 选项卡
        tab_widget = QTabWidget()

        # 假期类别管理
        leave_type_tab = QWidget()
        leave_type_layout = QVBoxLayout(leave_type_tab)

        # 添加按钮
        add_btn = QPushButton('添加假期类别')
        add_btn.clicked.connect(self.on_add_leave_type)
        leave_type_layout.addWidget(add_btn)

        # 假期类别表格
        self.leave_type_table = QTableWidget()
        self.leave_type_table.setColumnCount(5)
        self.leave_type_table.setHorizontalHeaderLabels(['类别名称', '总天数', '过期日期', '颜色', '操作'])
        self.leave_type_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.leave_type_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.leave_type_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.leave_type_table.setFont(QFont('Microsoft YaHei', 10))
        leave_type_layout.addWidget(self.leave_type_table)

        tab_widget.addTab(leave_type_tab, '假期类别')

        # 系统设置
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)

        # 调休过期设置
        overtime_group = QGroupBox('调休过期设置')
        overtime_layout = QFormLayout(overtime_group)

        self.overtime_expire_edit = QDateEdit()
        self.overtime_expire_edit.setDisplayFormat('MM-dd')
        self.overtime_expire_edit.setDate(QDate(2024, 12, 31))
        overtime_layout.addRow('调休过期日期:', self.overtime_expire_edit)

        hint_label = QLabel('说明: 每年该日期后,未使用的调休将自动作废')
        hint_label.setStyleSheet('color: #666;')
        overtime_layout.addRow(hint_label)

        system_layout.addWidget(overtime_group)
        system_layout.addStretch()

        tab_widget.addTab(system_tab, '系统设置')

        layout.addWidget(tab_widget)

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.on_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_settings(self):
        """加载设置"""
        # 加载假期类别
        self.load_leave_types()

        # 加载系统设置
        settings = self.main_window.system_settings_dao.get()
        if settings:
            expire_date = settings['overtime_expire_date']
            month, day = map(int, expire_date.split('-'))
            self.overtime_expire_edit.setDate(QDate(2024, month, day))

    def load_leave_types(self):
        """加载假期类别"""
        leave_types = self.main_window.leave_type_dao.get_all()
        self.leave_type_table.setRowCount(len(leave_types))

        for row, leave_type in enumerate(leave_types):
            # 类别名称
            name_item = QTableWidgetItem(leave_type['name'])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.leave_type_table.setItem(row, 0, name_item)

            # 总天数
            days_item = QTableWidgetItem(f"{leave_type['total_days']:.1f}天")
            days_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.leave_type_table.setItem(row, 1, days_item)

            # 过期日期
            expire_item = QTableWidgetItem(leave_type['expire_date'] or '无')
            expire_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.leave_type_table.setItem(row, 2, expire_item)

            # 颜色
            color_widget = QWidget()
            color_layout = QHBoxLayout(color_widget)
            color_layout.setContentsMargins(5, 5, 5, 5)

            color_label = QLabel()
            color_label.setFixedSize(30, 30)
            color_label.setStyleSheet(f'background-color: {leave_type["color"]}; border-radius: 5px;')
            color_layout.addWidget(color_label)
            color_layout.addStretch()

            self.leave_type_table.setCellWidget(row, 3, color_widget)

            # 操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 0, 5, 0)
            action_layout.setSpacing(5)

            # 编辑按钮
            edit_btn = QPushButton('编辑')
            edit_btn.setFixedWidth(60)
            edit_btn.clicked.connect(lambda checked, lt=leave_type: self.on_edit_leave_type(lt))
            action_layout.addWidget(edit_btn)

            # 删除按钮(系统类别不可删除)
            if not leave_type['is_system']:
                delete_btn = QPushButton('删除')
                delete_btn.setFixedWidth(60)
                delete_btn.clicked.connect(lambda checked, lt=leave_type: self.on_delete_leave_type(lt))
                action_layout.addWidget(delete_btn)

            self.leave_type_table.setCellWidget(row, 4, action_widget)

    def on_add_leave_type(self):
        """添加假期类别"""
        dialog = EditLeaveTypeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_leave_types()

    def on_edit_leave_type(self, leave_type):
        """编辑假期类别"""
        dialog = EditLeaveTypeDialog(self, leave_type)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_leave_types()

    def on_delete_leave_type(self, leave_type):
        """删除假期类别"""
        # 检查是否有使用记录
        used_days = self.main_window.leave_record_dao.get_used_days_by_type(leave_type['id'])
        if used_days > 0:
            QMessageBox.warning(self, '警告', '该假期类别已有使用记录,无法删除!')
            return

        reply = QMessageBox.question(
            self,
            '确认删除',
            f'确定要删除假期类别 "{leave_type["name"]}" 吗?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.main_window.leave_type_dao.delete(leave_type['id']):
                QMessageBox.information(self, '成功', '删除成功!')
                self.load_leave_types()
            else:
                QMessageBox.warning(self, '错误', '删除失败!')

    def on_save(self):
        """保存设置"""
        # 保存调休过期日期
        expire_date = self.overtime_expire_edit.date().toString('MM-dd')
        self.main_window.system_settings_dao.update_overtime_expire_date(expire_date)

        QMessageBox.information(self, '成功', '设置已保存!')
        self.accept()


class EditLeaveTypeDialog(QDialog):
    """编辑假期类别对话框"""

    def __init__(self, parent=None, leave_type=None):
        super().__init__(parent)
        self.settings_dialog = parent
        self.main_window = parent.main_window
        self.leave_type = leave_type
        self.selected_color = leave_type['color'] if leave_type else '#4A90E2'
        self.init_ui()

        if leave_type:
            self.load_data()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('编辑假期类别' if self.leave_type else '添加假期类别')
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # 表单
        form_layout = QFormLayout()

        # 类别名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('请输入类别名称')
        form_layout.addRow('类别名称:', self.name_edit)

        # 总天数
        self.days_spin = QDoubleSpinBox()
        self.days_spin.setRange(0, 365)
        self.days_spin.setValue(5)
        self.days_spin.setSingleStep(0.5)
        self.days_spin.setSuffix(' 天')
        form_layout.addRow('总天数:', self.days_spin)

        # 过期日期
        self.expire_edit = QDateEdit()
        self.expire_edit.setDisplayFormat('MM-dd')
        self.expire_edit.setDate(QDate(2024, 12, 31))
        self.expire_edit.setSpecialValueText('无')
        form_layout.addRow('过期日期:', self.expire_edit)

        # 颜色
        color_layout = QHBoxLayout()

        self.color_label = QLabel()
        self.color_label.setFixedSize(30, 30)
        self.color_label.setStyleSheet(f'background-color: {self.selected_color}; border-radius: 5px;')
        color_layout.addWidget(self.color_label)

        color_btn = QPushButton('选择颜色')
        color_btn.clicked.connect(self.on_select_color)
        color_layout.addWidget(color_btn)

        color_layout.addStretch()
        form_layout.addRow('显示颜色:', color_layout)

        layout.addLayout(form_layout)

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_data(self):
        """加载数据"""
        self.name_edit.setText(self.leave_type['name'])
        self.days_spin.setValue(self.leave_type['total_days'])

        if self.leave_type['expire_date']:
            month, day = map(int, self.leave_type['expire_date'].split('-'))
            self.expire_edit.setDate(QDate(2024, month, day))

        self.selected_color = self.leave_type['color']
        self.color_label.setStyleSheet(f'background-color: {self.selected_color}; border-radius: 5px;')

        # 系统类别不可修改名称
        if self.leave_type['is_system']:
            self.name_edit.setEnabled(False)

    def on_select_color(self):
        """选择颜色"""
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self.color_label.setStyleSheet(f'background-color: {self.selected_color}; border-radius: 5px;')

    def on_accept(self):
        """确认"""
        name = self.name_edit.text().strip()
        total_days = self.days_spin.value()
        expire_date = self.expire_edit.date().toString('MM-dd')
        color = self.selected_color

        # 验证
        if not name:
            QMessageBox.warning(self, '错误', '请输入类别名称!')
            return

        # 检查名称是否重复
        existing = self.main_window.leave_type_dao.get_by_name(name)
        if existing and (not self.leave_type or existing['id'] != self.leave_type['id']):
            QMessageBox.warning(self, '错误', '该类别名称已存在!')
            return

        try:
            if self.leave_type:
                # 更新
                self.main_window.leave_type_dao.update(
                    self.leave_type['id'],
                    name=name,
                    total_days=total_days,
                    expire_date=expire_date,
                    color=color
                )
                QMessageBox.information(self, '成功', '更新成功!')
            else:
                # 创建
                self.main_window.leave_type_dao.create(
                    name, total_days, expire_date, color, is_system=0
                )
                QMessageBox.information(self, '成功', '添加成功!')

            self.accept()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'操作失败: {str(e)}')

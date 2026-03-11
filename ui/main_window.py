"""
主窗口界面
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from models import Database
from dao import LeaveTypeDAO, OvertimeDAO, LeaveRecordDAO, SystemSettingsDAO
from .calendar_view import CalendarView
from .overtime_view import OvertimeView
from .leave_view import LeaveView
from .settings_view import SettingsView


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_daos()
        self.init_ui()
        self.check_expired_overtime()

    def init_daos(self):
        """初始化DAO对象"""
        self.leave_type_dao = LeaveTypeDAO(self.db)
        self.overtime_dao = OvertimeDAO(self.db)
        self.leave_record_dao = LeaveRecordDAO(self.db)
        self.system_settings_dao = SystemSettingsDAO(self.db)

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('假期管理系统')
        self.setMinimumSize(1200, 800)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 标题
        title_label = QLabel('假期管理系统')
        title_label.setFont(QFont('Microsoft YaHei', 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # 假期总览区域
        self.overview_widget = self.create_overview_widget()
        main_layout.addWidget(self.overview_widget)

        # 选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont('Microsoft YaHei', 10))

        # 日历视图
        self.calendar_view = CalendarView(self)
        self.tab_widget.addTab(self.calendar_view, '日历视图')

        # 加班管理
        self.overtime_view = OvertimeView(self)
        self.tab_widget.addTab(self.overtime_view, '加班管理')

        # 休假申请
        self.leave_view = LeaveView(self)
        self.tab_widget.addTab(self.leave_view, '休假申请')

        # 系统设置
        self.settings_view = SettingsView(self)
        self.tab_widget.addTab(self.settings_view, '系统设置')

        main_layout.addWidget(self.tab_widget)

    def create_overview_widget(self):
        """创建假期总览部件"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(180)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 滚动内容
        scroll_content = QWidget()
        layout = QHBoxLayout(scroll_content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 获取所有假期类别
        leave_types = self.leave_type_dao.get_all()

        for leave_type in leave_types:
            card = self.create_leave_card(leave_type)
            layout.addWidget(card)

        # 添加弹性空间
        layout.addStretch()

        scroll.setWidget(scroll_content)
        return scroll

    def create_leave_card(self, leave_type):
        """创建假期卡片"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f'''
            QFrame {{
                background-color: {leave_type['color']};
                border-radius: 10px;
                padding: 5px;
                min-width: 80px;
                max-width: 200px;
            }}
            QLabel {{
                color: white;
                background-color: transparent;
            }}
        ''')

        layout = QVBoxLayout(card)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # 类别名称
        name_label = QLabel(leave_type['name'])
        name_label.setFont(QFont('Microsoft YaHei', 12, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # 计算已用和剩余天数
        if leave_type['name'] == '调休':
            # 调休从加班记录计算
            # 获取所有未过期的加班记录的总等效天数
            overtime_records = self.overtime_dao.get_all()
            total_days = sum(record['equivalent_days'] for record in overtime_records if not record['is_expired'])
            # 获取所有未过期的加班记录的已用天数
            used_days = sum(record['used_days'] for record in overtime_records if not record['is_expired'])
            remaining_days = total_days - used_days
        else:
            total_days = leave_type['total_days']
            used_days = self.leave_record_dao.get_used_days_by_type(leave_type['id'])
            remaining_days = total_days - used_days

        # 总计
        total_label = QLabel(f'总计: {total_days:.1f}天')
        total_label.setFont(QFont('Microsoft YaHei', 9))
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(total_label)

        # 已用
        used_label = QLabel(f'已用: {used_days:.1f}天')
        used_label.setFont(QFont('Microsoft YaHei', 9))
        used_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(used_label)

        # 剩余
        remaining_label = QLabel(f'剩余: {remaining_days:.1f}天')
        remaining_label.setFont(QFont('Microsoft YaHei', 9, QFont.Weight.Bold))
        remaining_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(remaining_label)

        return card

    def refresh_overview(self):
        """刷新假期总览"""
        # 重新创建总览部件
        parent_layout = self.centralWidget().layout()
        parent_layout.removeWidget(self.overview_widget)
        self.overview_widget.deleteLater()
        self.overview_widget = self.create_overview_widget()
        parent_layout.insertWidget(1, self.overview_widget)

    def refresh_all(self):
        """刷新所有视图"""
        self.refresh_overview()
        self.calendar_view.refresh()
        self.overtime_view.refresh()
        self.leave_view.refresh()
        self.settings_view.refresh()

    def check_expired_overtime(self):
        """检查过期的加班记录"""
        from datetime import date
        from utils import is_date_expired

        expire_date = self.system_settings_dao.get_overtime_expire_date()
        today = date.today()

        # 获取所有未过期的加班记录
        overtime_records = self.overtime_dao.get_all()
        expired_count = 0

        for record in overtime_records:
            if record['is_expired']:
                continue

            overtime_date = record['overtime_date']
            if isinstance(overtime_date, str):
                from datetime import datetime
                overtime_date = datetime.strptime(overtime_date, '%Y-%m-%d').date()

            # 检查是否过期
            if is_date_expired(overtime_date, expire_date):
                self.overtime_dao.mark_expired(record['id'])
                expired_count += 1

        if expired_count > 0:
            QMessageBox.information(
                self,
                '过期提醒',
                f'有 {expired_count} 条加班记录已过期并自动作废。'
            )

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.db.close()
        event.accept()

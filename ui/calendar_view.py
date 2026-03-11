"""
日历视图
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGridLayout, QFrame, QScrollArea, QMessageBox, QDialog,
    QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import date

from utils import get_month_calendar, get_current_year, get_current_month


class CalendarView(QWidget):
    """日历视图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.current_year = get_current_year()
        self.current_month = get_current_month()
        self.view_mode = 'month'  # 'month' or 'year'
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 控制栏
        control_layout = QHBoxLayout()

        # 视图模式切换
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(['月视图', '年视图'])
        self.view_mode_combo.currentIndexChanged.connect(self.on_view_mode_changed)
        control_layout.addWidget(self.view_mode_combo)

        control_layout.addStretch()

        # 导航按钮
        self.prev_btn = QPushButton('◀ 上月')
        self.prev_btn.clicked.connect(self.on_prev)
        control_layout.addWidget(self.prev_btn)

        self.date_label = QLabel()
        self.date_label.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setMinimumWidth(200)
        control_layout.addWidget(self.date_label)

        self.next_btn = QPushButton('下月 ▶')
        self.next_btn.clicked.connect(self.on_next)
        control_layout.addWidget(self.next_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # 日历区域
        self.calendar_scroll = QScrollArea()
        self.calendar_scroll.setWidgetResizable(True)
        self.calendar_widget = QWidget()
        self.calendar_layout = QVBoxLayout(self.calendar_widget)
        self.calendar_scroll.setWidget(self.calendar_widget)
        layout.addWidget(self.calendar_scroll)

        # 图例
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()

        legends = [
            ('加班', '#FFA500'),
            ('年假', '#4A90E2'),
            ('调休', '#7ED321'),
            ('婚假', '#FF69B4'),
            ('丧假', '#9B59B6'),
            ('其他', '#95A5A6')
        ]

        for name, color in legends:
            legend_item = QFrame()
            legend_item.setFixedSize(20, 20)
            legend_item.setStyleSheet(f'background-color: {color}; border-radius: 3px;')
            legend_layout.addWidget(legend_item)

            legend_label = QLabel(name)
            legend_label.setFont(QFont('Microsoft YaHei', 9))
            legend_layout.addWidget(legend_label)
            legend_layout.addSpacing(10)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        self.update_date_label()
        self.refresh()

    def on_view_mode_changed(self, index):
        """视图模式改变"""
        self.view_mode = 'month' if index == 0 else 'year'
        if self.view_mode == 'year':
            self.prev_btn.setText('◀ 上年')
            self.next_btn.setText('下年 ▶')
        else:
            self.prev_btn.setText('◀ 上月')
            self.next_btn.setText('下月 ▶')
        self.update_date_label()
        self.refresh()

    def on_prev(self):
        """上一个"""
        if self.view_mode == 'month':
            self.current_month -= 1
            if self.current_month < 1:
                self.current_month = 12
                self.current_year -= 1
        else:
            self.current_year -= 1
        self.update_date_label()
        self.refresh()

    def on_next(self):
        """下一个"""
        if self.view_mode == 'month':
            self.current_month += 1
            if self.current_month > 12:
                self.current_month = 1
                self.current_year += 1
        else:
            self.current_year += 1
        self.update_date_label()
        self.update_date_label()
        self.refresh()

    def update_date_label(self):
        """更新日期标签"""
        if self.view_mode == 'month':
            self.date_label.setText(f'{self.current_year}年{self.current_month}月')
        else:
            self.date_label.setText(f'{self.current_year}年')

    def refresh(self):
        """刷新日历"""
        # 清除现有日历
        while self.calendar_layout.count():
            item = self.calendar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self.view_mode == 'month':
            self.create_month_view()
        else:
            self.create_year_view()

    def create_month_view(self):
        """创建月视图"""
        # 星期标题
        weekday_widget = QWidget()
        weekday_layout = QHBoxLayout(weekday_widget)
        weekday_layout.setContentsMargins(0, 0, 0, 5)

        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        for weekday in weekdays:
            label = QLabel(weekday)
            label.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weekday_layout.addWidget(label)

        self.calendar_layout.addWidget(weekday_widget)

        # 日历网格
        calendar_data = get_month_calendar(self.current_year, self.current_month)

        for week in calendar_data:
            week_widget = QWidget()
            week_layout = QHBoxLayout(week_widget)
            week_layout.setContentsMargins(0, 0, 0, 0)
            week_layout.setSpacing(2)

            for day in week:
                day_widget = self.create_day_widget(day)
                week_layout.addWidget(day_widget)

            self.calendar_layout.addWidget(week_widget)

        self.calendar_layout.addStretch()

    def create_year_view(self):
        """创建年视图"""
        from utils import get_year_calendar

        year_data = get_year_calendar(self.current_year)

        # 每行显示3个月
        for row in range(4):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setSpacing(10)

            for col in range(3):
                month_idx = row * 3 + col
                month_widget = self.create_month_widget(month_idx + 1, year_data[month_idx])
                row_layout.addWidget(month_widget)

            self.calendar_layout.addWidget(row_widget)

    def create_month_widget(self, month, month_data):
        """创建月份小部件(年视图用)"""
        month_widget = QFrame()
        month_widget.setFrameShape(QFrame.Shape.StyledPanel)
        month_widget.setStyleSheet('QFrame { background-color: #f5f5f5; border-radius: 5px; padding: 5px; }')

        layout = QVBoxLayout(month_widget)
        layout.setSpacing(2)

        # 月份标题
        month_label = QLabel(f'{month}月')
        month_label.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(month_label)

        # 星期标题
        weekday_widget = QWidget()
        weekday_layout = QHBoxLayout(weekday_widget)
        weekday_layout.setContentsMargins(0, 0, 0, 0)
        weekday_layout.setSpacing(1)

        weekdays = ['一', '二', '三', '四', '五', '六', '日']
        for weekday in weekdays:
            label = QLabel(weekday)
            label.setFont(QFont('Microsoft YaHei', 8))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weekday_layout.addWidget(label)

        layout.addWidget(weekday_widget)

        # 日期
        for week in month_data:
            week_widget = QWidget()
            week_layout = QHBoxLayout(week_widget)
            week_layout.setContentsMargins(0, 0, 0, 0)
            week_layout.setSpacing(1)

            for day in week:
                day_label = QLabel()
                day_label.setFont(QFont('Microsoft YaHei', 8))
                day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                day_label.setFixedHeight(20)

                if day:
                    day_label.setText(str(day.day))
                    # 检查是否有活动
                    color = self.get_day_color(day)
                    if color:
                        day_label.setStyleSheet(f'background-color: {color}; color: white; border-radius: 3px;')

                week_layout.addWidget(day_label)

            layout.addWidget(week_widget)

        return month_widget

    def create_day_widget(self, day):
        """创建日期部件"""
        day_widget = QFrame()
        day_widget.setFixedHeight(80)
        day_widget.setStyleSheet('QFrame { background-color: white; border: 1px solid #ddd; }')

        layout = QVBoxLayout(day_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        if day:
            # 日期数字
            day_label = QLabel(str(day.day))
            day_label.setFont(QFont('Microsoft YaHei', 12, QFont.Weight.Bold))
            day_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            layout.addWidget(day_label)

            # 获取当天的活动
            activities = self.get_day_activities(day)

            # 显示活动
            for activity in activities[:3]:  # 最多显示3个
                activity_label = QLabel(activity['text'])
                activity_label.setFont(QFont('Microsoft YaHei', 8))
                activity_label.setStyleSheet(f'color: white; background-color: {activity["color"]}; border-radius: 2px; padding: 1px;')
                layout.addWidget(activity_label)

            # 设置背景色
            color = self.get_day_color(day)
            if color:
                day_widget.setStyleSheet(f'QFrame {{ background-color: {color}; border: 1px solid #ddd; }}')

            # 点击事件
            day_widget.mousePressEvent = lambda e, d=day: self.on_day_clicked(d)

        return day_widget

    def get_day_activities(self, day):
        """获取指定日期的活动"""
        activities = []
        day_str = day.strftime('%Y-%m-%d')

        # 获取加班记录
        overtime_records = self.main_window.overtime_dao.get_all()
        for record in overtime_records:
            if record['overtime_date'] == day_str:
                activities.append({
                    'text': f"加班 {record['start_time']}-{record['end_time']}",
                    'color': '#FFA500'
                })

        # 获取休假记录
        leave_records = self.main_window.leave_record_dao.get_all()
        for record in leave_records:
            if record['leave_date'] == day_str:
                leave_type = self.main_window.leave_type_dao.get_by_id(record['leave_type_id'])
                color = leave_type['color'] if leave_type else '#95A5A6'
                activities.append({
                    'text': f"{record['leave_type_name']} {record['days_used']}天",
                    'color': color
                })

        return activities

    def get_day_color(self, day):
        """获取日期的背景色"""
        day_str = day.strftime('%Y-%m-%d')

        # 检查加班
        overtime_records = self.main_window.overtime_dao.get_all()
        for record in overtime_records:
            if record['overtime_date'] == day_str:
                return '#FFA500'

        # 检查休假
        leave_records = self.main_window.leave_record_dao.get_all()
        for record in leave_records:
            if record['leave_date'] == day_str:
                leave_type = self.main_window.leave_type_dao.get_by_id(record['leave_type_id'])
                return leave_type['color'] if leave_type else '#95A5A6'

        return None

    def on_day_clicked(self, day):
        """日期被点击"""
        activities = self.get_day_activities(day)

        if not activities:
            QMessageBox.information(self, '日期详情', f'{day.strftime("%Y-%m-%d")}\n\n无活动记录')
            return

        # 显示详情对话框
        dialog = DayDetailDialog(day, activities, self)
        dialog.exec()


class DayDetailDialog(QDialog):
    """日期详情对话框"""

    def __init__(self, day, activities, parent=None):
        super().__init__(parent)
        self.day = day
        self.activities = activities
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(f'{self.day.strftime("%Y-%m-%d")} 详情')
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        # 日期标题
        title_label = QLabel(self.day.strftime('%Y年%m月%d日'))
        title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 活动列表
        info_text = '\n'.join([f"• {act['text']}" for act in self.activities])
        info_label = QLabel(info_text)
        info_label.setFont(QFont('Microsoft YaHei', 11))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

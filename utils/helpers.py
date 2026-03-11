"""
工具函数
"""
from datetime import datetime, date, timedelta
from calendar import monthrange


def calculate_overtime_days(overtime_date, start_time, end_time):
    """
    计算加班等效天数

    规则:
    - 周末加班: 满6小时=1天, 不满6小时=0.5天
    - 工作日晚上加班: 统一0.5天
    """
    # 解析日期和时间
    if isinstance(overtime_date, str):
        overtime_date = datetime.strptime(overtime_date, '%Y-%m-%d').date()

    start_dt = datetime.strptime(start_time, '%H:%M')
    end_dt = datetime.strptime(end_time, '%H:%M')

    # 计算时长(小时)
    duration = (end_dt - start_dt).seconds / 3600

    # 判断是否周末 (5=周六, 6=周日)
    is_weekend = overtime_date.weekday() >= 5

    if is_weekend:
        # 周末加班
        if duration >= 6:
            return 1.0
        else:
            return 0.5
    else:
        # 工作日晚上加班
        return 0.5


def get_remaining_color(remaining_days):
    """
    根据剩余天数返回颜色
    - 红色: 不足1天
    - 绿色: 充足
    - 灰色: 已用完
    """
    if remaining_days <= 0:
        return '#999999'  # 灰色
    elif remaining_days < 1:
        return '#E74C3C'  # 红色
    else:
        return '#27AE60'  # 绿色


def get_month_days(year, month):
    """获取指定月份的天数"""
    return monthrange(year, month)[1]


def get_month_calendar(year, month):
    """
    获取指定月份的日历数据
    返回一个列表,每个元素是一周(7天)的日期列表
    """
    first_day = date(year, month, 1)
    month_days = get_month_days(year, month)

    # 计算第一天的星期几 (0=周一, 6=周日)
    first_weekday = first_day.weekday()

    # 构建日历数据
    calendar_data = []
    week = []

    # 填充月初空白
    for _ in range(first_weekday):
        week.append(None)

    # 填充日期
    for day in range(1, month_days + 1):
        week.append(date(year, month, day))
        if len(week) == 7:
            calendar_data.append(week)
            week = []

    # 填充月末空白
    if week:
        while len(week) < 7:
            week.append(None)
        calendar_data.append(week)

    return calendar_data


def get_year_calendar(year):
    """获取指定年份的日历数据"""
    return [get_month_calendar(year, month) for month in range(1, 13)]


def format_date(dt):
    """格式化日期为 YYYY-MM-DD"""
    if isinstance(dt, date):
        return dt.strftime('%Y-%m-%d')
    return str(dt)


def format_time(time_str):
    """格式化时间为 HH:MM"""
    if not time_str:
        return ''
    return time_str[:5] if len(time_str) >= 5 else time_str


def parse_date(date_str):
    """解析日期字符串"""
    if isinstance(date_str, date):
        return date_str
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def is_date_expired(check_date, expire_date_str):
    """
    检查日期是否过期
    expire_date_str: 格式 MM-DD
    """
    if not expire_date_str:
        return False

    month, day = map(int, expire_date_str.split('-'))
    expire_dt = date(check_date.year, month, day)

    return check_date > expire_dt


def get_current_year():
    """获取当前年份"""
    return date.today().year


def get_current_month():
    """获取当前月份"""
    return date.today().month

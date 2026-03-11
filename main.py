"""
假期管理系统 - 主程序入口
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui import MainWindow


def main():
    """主函数"""
    # 创建应用
    app = QApplication(sys.argv)

    # 设置应用信息
    app.setApplicationName('假期管理系统')
    app.setApplicationVersion('1.0.0')

    # 设置字体
    font = app.font()
    font.setFamily('Microsoft YaHei')
    app.setFont(font)

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 运行应用
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

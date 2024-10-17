import random
import re
import time
import uuid

import os
from datetime import datetime

from PyQt5.QtCore import Qt, QDate

import ui as m
import numpy as np
import database_service as d
import qrcode
import parking_lot
import date_anly as d_a
import tkinter as tk
from tkinter import messagebox
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QFileDialog
from qdarkstyle import load_stylesheet_pyqt5
from prettytable import PrettyTable
from PyQt5.QtGui import QPixmap


class APP(QMainWindow, m.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.ui = m.Ui_MainWindow()
        self.ui.setupUi(self)

        self.parking_lot_num = np.zeros((30, 30), dtype=object)
        self.parking_lot_num.fill(0)
        self.final_parking_fee = 0
        self.admin = False

        self.pattern = r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4,6}$'

        # ------------------page_btu---------------------- #
        self.in_or_out_page_btu = self.ui.pushButton_4
        self.search_page_btu = self.ui.pushButton_6
        self.parking_page_btu = self.ui.pushButton_10
        self.data_page_btu = self.ui.pushButton_5
        self.data_page_btu.setEnabled(False)
        self.setting_page_btu = self.ui.pushButton_2
        self.login_page_btu = self.ui.pushButton
        # ------------------------------------------------ #
        self.parking_lot = self.ui.tableWidget  # 单元格模拟停车位
        self.parking_lot.setMouseTracking(True)  # 鼠标跟踪
        self.parking_lot.verticalHeader().setVisible(False)  # 隐藏行号
        self.parking_lot.horizontalHeader().setVisible(False)  # 隐藏列号
        self.parking_lot.setRowCount(30)  # 行数
        self.parking_lot.setColumnCount(30)  # 列数
        self.parking_lot.setStyleSheet("""
                                        QTableWidget {
                                            border: none;
                                            gridline-color: transparent;
                                        }
                                        QTableWidget::item {
                                            border: none;
                                        }
                                        QTableWidget::item:selected {
                                            color: white;
                                            background-color: #0078d7;
                                        }
                                        """)
        delegate = parking_lot.CustomDelegate(self.parking_lot)
        self.parking_lot.setItemDelegate(delegate)

        self.init_ui()
        self.solt()
        d.create_database()

        # noinspection PyAttributeOutsideInit

    def init_ui(self):  # 初始化界面
        # ------------------in_or_put------------------------------------------- #
        self.entrance_btu = self.ui.pushButton_3  # 入场按钮
        self.car_id_in_input_txt = self.ui.lineEdit  # 入场车牌号输入框
        self.result_output_when_enter = self.ui.textBrowser  # 入场信息输出框

        self.exit_btu = self.ui.pushButton_7  # 出场按钮
        self.car_id_out_input_txt = self.ui.lineEdit_2  # 出场车牌号输入框
        self.result_output_when_exit = self.ui.textBrowser_2  # 出场信息输出框

        self.qr_code_png = self.ui.label_3  # 二维码显示
        self.refresh_qr_code = self.ui.pushButton_8  # 更新二维码

        # ------------------setting-------------------------------------------- #
        self.discount_box = self.ui.comboBox_9  # 折扣选择框
        self.theme_box = self.ui.comboBox_10  # 主题选择框

        # ------------------search--------------------------------------------- #
        self.search_car_id_btu = self.ui.pushButton_9  # 搜索按钮
        self.search_car_id_input_txt = self.ui.lineEdit_3  # 搜索车牌号输入框
        self.search_result_txt = self.ui.textBrowser_3  # 搜索结果输出框

        # ------------------page----------------------------------------------- #
        self.parking = self.ui.tableWidget  # 停车位

        # ------------------login----------------------------------------------- #
        self.confirm_login_btu = self.ui.pushButton_13  # 确认登录
        self.cancel_login_btu = self.ui.pushButton_14  # 取消登录
        self.username_input_txt = self.ui.lineEdit_4  # 登录账号密码输入框
        self.password_input_txt = self.ui.lineEdit_5  # 登录账号密码输入框
        self.login_result_txt = self.ui.login_info  # 登录信息输出框

        # ------------------other----------------------------------------------- #
        self.theme_box = self.ui.comboBox_10  # 主题选择框
        # ------------------------------------------------------------------- #
        self.calender = self.ui.calendarWidget  # 日历选择
        # ------------------data----------------------------------------------- #
        self.data_analy_review_btu = self.ui.pushButton_11  # 预览按钮
        self.data_analy_deduced_btu = self.ui.pushButton_12  # 保存按钮
        self.start_date_input_txt = self.ui.dateTimeEdit
        self.end_date_input_txt = self.ui.dateTimeEdit_2
        self.start_date_input_txt.setDate(QDate.currentDate())
        self.end_date_input_txt.setDate(QDate.currentDate())

    def solt(self):  # 槽函数
        # ------------------page----------------------------------------------- #
        in_or_out_page = 0
        setting_page = 1
        data = 2
        search_page = 3
        login_page = 4
        parking_page = 5

        self.in_or_out_page_btu.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(in_or_out_page))
        self.data_page_btu.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(data))
        self.setting_page_btu.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(setting_page))
        self.search_page_btu.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(search_page))
        self.parking_page_btu.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(parking_page))
        self.login_page_btu.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(login_page))
        # -------------------------------------------------------------------- #
        self.entrance_btu.clicked.connect(self.add_vehicle)  # 入场
        self.exit_btu.clicked.connect(self.end_parking)  # 出场
        self.search_car_id_btu.clicked.connect(self.get_vehicle_history)  # 搜索历史
        # ------------------other--------------------------------------------- #
        self.theme_box.currentTextChanged.connect(self.change_theme)  # 主题切换
        # ------------------qrcode-------------------------------------------- #
        self.refresh_qr_code.clicked.connect(lambda: self.generate_alipay_qr_code(self.final_parking_fee))
        # ------------------login---------------------------------------------- #
        self.confirm_login_btu.clicked.connect(self.login)
        self.cancel_login_btu.clicked.connect(self.clear_login_info)
        # ------------------data_analy---------------------------------------- #
        self.data_analy_review_btu.clicked.connect(self.generate_report)
        self.data_analy_deduced_btu.clicked.connect(self.save_report)

    def login(self):
        try:
            print("登录")
            username = self.username_input_txt.text()
            password = self.password_input_txt.text()
            if not username or not password:
                self.login_result_txt.setText("账号或密码为空")
                return
            if username == "admin" and password == "admin":
                self.login_result_txt.setText("登录成功")
                print("登录成功")
                self.admin = True
                self.data_page_btu.setEnabled(True)
            else:
                self.login_result_txt.setText("登录失败")
                print("登录失败")
                self.data_page_btu.setEnabled(False)
        except Exception as e:
            print(e)

    def clear_login_info(self):
        self.username_input_txt.clear()
        self.password_input_txt.clear()

    def add_vehicle(self):  # 添加车辆
        self.car_id = self.car_id_in_input_txt.text()

        if not re.match(self.pattern, self.car_id):
            self.result_output_when_enter.setText(f"车牌号 {self.car_id} 不合法")
            return
        else:
            d.add_vehicle(self.car_id, "car")
            self.start_parking()

    def start_parking(self):  # 开始停车

        if d.is_parking(self.car_id):
            self.result_output_when_enter.setText(f"{self.car_id} 已经在停车")
            return
        else:
            self.allocate_parking(self.car_id)
            self.result_output_when_enter.setText(
                f"{self.car_id} 开始停车，停车位为 {self.allocate_parking(self.car_id)}")
            self.show_parking_lot()  # 显示停车位

            d.start_parking(self.car_id, f"{self.allocate_parking(self.car_id)}")

    def end_parking(self):  # 结束停车
        self.car_id = self.car_id_out_input_txt.text()
        # try:
        if not re.match(self.pattern, self.car_id):
            self.result_output_when_exit.setText(f"车牌号 {self.car_id} 不合法")
            return

        if d.is_parking(self.car_id):
            result = d.end_parking(self.car_id)  # 结束停车

            self.release_parking(self.parking)  # 释放停车位
            self.del_parking_lot()  # 删除停车位
            # print("qweweqweq")
            # print(type(result))
            if isinstance(result, tuple):  # 返回元组

                self.final_parking_fee = result[1]
                self.result_output_when_exit.setText(
                    f"{self.car_id} 停车结束，停车时间为 {result[0]} 小时，费用为 {result[1]} 元")
                print(result)
                self.generate_alipay_qr_code(result[1])
                # print(121212121212)
            else:
                self.result_output_when_exit.setText(result)
        else:
            self.result_output_when_exit.setText(f"{self.car_id} 没有停车")

        # except Exception as e:
        #     print(e)

    def get_vehicle_history(self):  # 获取车辆历史记录
        self.car_id = self.search_car_id_input_txt.text()
        if not re.match(self.pattern, self.car_id):
            self.search_result_txt.setText(f"车牌号 {self.car_id} 不合法")
            return
        try:
            self.search_result_txt.clear()
            if self.car_id == "":
                self.search_result_txt.setText("请输入车牌号")
                return

            # 设置 HTML 格式
            html = '''<html><head><style>
                                    body {
                                        font-family: Arial, sans-serif;
                                        background-color: rgba(136, 181, 181, 0.73);
                                    }
                                    table {
                                        width: 100%;
                                        border-collapse: collapse;
                                        margin: 20px auto;
                                    }
                                    th, td {
                                        border: 1px solid rgba(32, 165, 82, 0.66);
                                        padding: 8px;
                                        text-align: center;
                                    }
                                    th {
                                        background-color: #A2a2d1;
                                        font-weight: bold;
                                    }
                                    tr:nth-child(even) {
                                        background-color: #a26aea;
                                    }
                                    tr:hover {
                                        background-color: rgba(164, 136, 253, 0.8);
                                    }
                                </style></head><body>'''

            # 添加表头
            html += '<table border="1">'
            html += '<tr><th>停车位</th><th>开始时间</th><th>结束时间</th><th>时间长短</th><th>费用</th></tr>'

            # 创建 PrettyTable 对象
            table = PrettyTable()

            # 设置表头
            table.field_names = ['停车位', '开始时间', '结束时间', '时间长短', '费用']
            result = d.get_vehicle_history_paginated(self.car_id)
            for entry in result:
                row_html = (f'<tr><td>{entry["停车位"]}</td>'
                            f'<td>{entry["开始时间"]}</td>'
                            f'<td>{entry["结束时间"]}</td>'
                            f'<td>{entry["时间长短"]}</td>'
                            f'<td>{entry["费用"]}</td></tr>')
                html += row_html
            html += '</table></body></html>'
            self.search_result_txt.setHtml(html)
        except Exception as e:
            print(e)

    def allocate_parking(self, vehicle_id):
        """
        动态分配停车位
        :param vehicle_id: 车辆 ID
        :return: 分配的停车位坐标 (row, col)，如果未找到空闲停车位返回 None
        """
        # 初始化检查
        self.print_matrix("Initial parking lot:")

        # 查找空闲停车位
        for row in range(30):
            for col in range(30):
                print(f"Checking slot at ({row}, {col}): {self.parking_lot_num[row][col]}")
                if self.parking_lot_num[row][col] == 0:
                    print(f"Found empty slot at ({row}, {col})")
                    self.parking_lot_num[row][col] = vehicle_id
                    return row, col

        # 如果没有找到空闲停车位
        return None

    def print_matrix(self, message):
        """
        打印矩阵
        :param message: 打印的消息前缀
        """
        print(message)
        for row in range(30):
            for col in range(30):
                print(f"{self.parking_lot_num[row][col]:3}", end=' ')
            print()
        print()

    def show_parking_lot(self):
        row, col = self.allocate_parking(self.car_id)
        item = QTableWidgetItem(f"{row},{col}"
                                f"{self.car_id}")
        self.parking_lot.setItem(row, col, item)

    def release_parking(self, vehicle_id):
        """
        释放停车位
        :param vehicle_id: 车辆 ID
        :return: 是否成功释放停车位
        """
        for row in range(30):
            for col in range(30):
                if self.parking_lot_num[row, col] == vehicle_id:
                    self.parking_lot_num[row, col] = 0
                    print("sjishu:", row, col)
                    return row, col
        return False

    def del_parking_lot(self):
        row, col = self.release_parking(self.car_id)
        if row and col:
            print("释放成功")
            item = QTableWidgetItem(0)
            self.parking_lot.setItem(row, col, item)
        else:
            print("释放失败")

    def rebate(self):  # 优惠设置
        pass

    def change_theme(self):  # 主题设置
        print(self.theme_box.currentText())
        if self.theme_box.currentText() == "黑    夜":
            self.setStyleSheet(load_stylesheet_pyqt5())
            print("黑夜")
        if self.theme_box.currentText() == "白    天":
            self.setStyleSheet("")
            print("白天")
            pass

    def generate_report(self):  # 生成报表
        self.data_a = d_a.parking_data()
        chart_type = self.ui.comboBox.currentText()  # 报告类型选择框
        chart_data = self.ui.comboBox_2.currentText()  # 报告数据选择框
        print(chart_type,
              chart_data)
        # 获取开始时间和结束时间
        start_time_str = self.ui.dateTimeEdit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        end_time_str = self.ui.dateTimeEdit_2.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
        interval_str = self.ui.comboBox_3.currentText()

        try:
            match interval_str:
                case "1小时":
                    self.interval = 1
                case "3小时":
                    self.interval = 3
                case "5小时":
                    self.interval = 5
                case "7小时":
                    self.interval = 7
                case "10小时":
                    self.interval = 10
                case "12小时":
                    self.interval = 12
                case "24小时":
                    self.interval = 24
                case "3天":
                    self.interval = 72
                case "5天":
                    self.interval = 120
                case "10天":
                    self.interval = 240
                case _:
                    self.interval = 0
        except ValueError:
            self.show_message("有错误！")
            return
        try:
            print("chart_type:", chart_type)
            match chart_type:
                case "饼状图":
                    self.test_chart_type = "pie"
                case "柱形图":
                    self.test_chart_type = "bar"
                case "折线图":
                    self.test_chart_type = "line"
                case _:
                    self.test_chart_type = "pie"
        except ValueError:
            self.show_message("有错误！")
            return
        print("interval:", self.interval)
        if self.interval <= ((end_time - start_time).total_seconds()) / 3600:
            print(((end_time - start_time).total_seconds()) / 3600)
            if chart_data == "收入":
                self.data_a.read_fee_from_parking(str(start_time), str(end_time), self.interval)
                self.data_a.generate_parking_fee_chart(self.test_chart_type, (6, 5), f"fee_{self.test_chart_type}chart.png")
                self.ui.label_6.setPixmap(QPixmap(f"fee_{self.test_chart_type}chart.png"))
                self.ui.label_6.setAlignment(Qt.AlignCenter)
            elif chart_data == "停车时长":
                self.data_a.read_time_from_parking(str(start_time), str(end_time), self.interval)
                self.data_a.generate_parking_time_chart(self.test_chart_type, (6, 5),f"time_{self.test_chart_type}chart.png")
                self.ui.label_6.setPixmap(QPixmap(f"time_{self.test_chart_type}chart.png"))
                self.ui.label_6.setAlignment(Qt.AlignCenter)
            elif chart_data == "停车数量":
                self.data_a.read_number_from_parking(str(start_time), str(end_time), self.interval)
                self.data_a.generate_parking_number_chart(self.test_chart_type, (6, 5),f"number_{self.test_chart_type}chart.png")
                self.ui.label_6.setPixmap(QPixmap(f"number_{self.test_chart_type}chart.png"))
                self.ui.label_6.setAlignment(Qt.AlignCenter)


        else:
            self.show_message("时间间隔不合理，请检查您的输入！")
        print(start_time, end_time, self.interval)

    def save_report(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存图片", "", "PNG Files (*.png);;All Files (*)",
                                                   options=options)

        if file_path:
            self.data_a.generate_parking_fee_chart(self.test_chart_type, (6, 5), file_path)
            self.ui.label_6.setPixmap(QPixmap(file_path))
            self.ui.label_6.setAlignment(Qt.AlignCenter)
        else:
            print("用户取消了保存操作")


    def show_message(self, message):
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showinfo("提示", message)

    def generate_alipay_qr_code(self, amount):
        """
        生成支付宝付款二维码图片。

        参数:
        amount (float): 需要支付的金额。

        返回:
        None
        """
        # 构建支付宝付款链接，这里假设使用标准的支付宝收款链接格式
        alipay_url = f"{self.create_alipay_qr_key()}"
        qr = qrcode.main.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(alipay_url)
        qr.make(fit=True)
        fill_color = ["black", "blue", "red"]
        back_color = ["white", "green", "yellow"]

        img = qr.make_image(fill_color=random.choice(fill_color), back_color=random.choice(back_color))

        # 调整图像大小到400x400像素
        img = img.resize((380, 380))
        img.save(f"alipay_{amount}_qr.png")
        self.ui.label_3.setPixmap(QPixmap(f"alipay_{amount}_qr.png"))
        # 展示完之后删除

        os.remove(f"alipay_{amount}_qr.png")

        # 保存图像
        # img.save(f"alipay_{amount}_qr.png")

    def create_alipay_qr_key(self):
        """
        创建支付宝二维码Key API调用
        返回:
        str: 二维码Key字符串
        """

        return "https://github.com/UF4OVER"


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    # app.setStyleSheet(load_stylesheet_pyqt5())
    window = APP()
    window.show()
    app.exec()

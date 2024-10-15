import sqlite3
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_template import FigureCanvas
from pyqtgraph.canvas import Canvas


class parking_data:
    def __init__(self):
        self.dis_fee = None


    def read_time_from_parking(self, time_start, time_end, time_interval):
        """
        从数据库中读取停车时间，并按给定的时间间隔统计停车时长分布
        :param time_start: 开始时间字符串，格式为 "YYYY-MM-DD HH:MM:SS"
        :param time_end: 结束时间字符串，格式为 "YYYY-MM-DD HH:MM:SS"
        :param time_interval: 时间间隔，单位为小时
        """
        # 将输入的时间字符串转换为 datetime 对象
        start_datetime = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S")

        # 计算时间差
        total_hours = (end_datetime - start_datetime).total_seconds() / 3600

        # 动态生成区间
        intervals = ['<{}h'.format(time_interval)]
        intervals.extend(
            ['{}-{}h'.format(i, i + time_interval) for i in range(time_interval, int(total_hours) + 1, time_interval)])

        # 初始化统计字典
        distribution = {interval: 0 for interval in intervals}

        # 连接数据库并执行查询
        conn = sqlite3.connect('parking.db')
        cursor = conn.cursor()

        # 查询符合条件的停车记录
        cursor.execute("SELECT start_time, end_time FROM parking_records WHERE start_time >= ? AND end_time <= ?",
                       (time_start, time_end))
        rows = cursor.fetchall()
        conn.close()

        # 统计每个停车记录的时长，并归入对应的区间
        for row in rows:
            start_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
            duration = (end_time - start_time).total_seconds() / 3600  # 转换为小时

            # 根据停车时长更新统计结果
            if duration < time_interval:
                distribution['<{}h'.format(time_interval)] += 1
            else:
                for i in range(time_interval, int(total_hours) + 1, time_interval):
                    if i <= duration < i + time_interval:
                        distribution['{}-{}h'.format(i, i + time_interval)] += 1
                        break

        # 返回统计结果
        self.dis = distribution

    def read_number_from_parking(self) -> list:
        """
        从数据库中读取停车数量
        :return:
        """
        pass

    def read_fee_from_parking(self, time_start, time_end, fee_interval) -> dict:
        """
        从数据库中读取停车费用，并按给定的费用间隔统计费用分布
        :param time_start: 开始时间字符串，格式为 "YYYY-MM-DD HH:MM:SS"
        :param time_end: 结束时间字符串，格式为 "YYYY-MM-DD HH:MM:SS"
        :param fee_interval: 费用间隔，单位为元
        :return: 包含各区间费用分布的字典
        """

        if fee_interval == 0:
            return
        # 将输入的时间字符串转换为 datetime 对象
        start_datetime = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S")

        # 初始化统计字典
        distribution = {'<{}￥'.format(fee_interval): 0}
        distribution.update(
            {str(i) + '-' + str(i + fee_interval) + '￥': 0 for i in range(fee_interval, 1000, fee_interval)})

        # 连接数据库并执行查询
        conn = sqlite3.connect('parking.db')
        cursor = conn.cursor()

        # 查询符合条件的停车记录
        cursor.execute("SELECT start_time, end_time, fee FROM parking_records WHERE start_time >= ? AND end_time <= ?",
                       (start_datetime, end_datetime))
        rows = cursor.fetchall()
        conn.close()

        # 统计每个停车记录的费用，并归入对应的区间
        for row in rows:
            fee = row[2]

            # 根据费用更新统计结果
            if fee < fee_interval:
                distribution['<{}￥'.format(fee_interval)] += 1
            else:
                for i in range(fee_interval, 1000, fee_interval):
                    if i <= fee < i + fee_interval:
                        distribution['{}-{}￥'.format(i, i + fee_interval)] += 1
                        break

        # 返回统计结果
        self.dis_fee = distribution

    def merge_zero_intervals(self, distribution):
        """
        合并连续的零值区间
        :param distribution: 包含各区间停车时长占比的字典
        :return: 合并后的字典
        """
        merged_distribution = {}
        current_start = None
        current_sum = 0

        keys = list(distribution.keys())
        for i, key in enumerate(keys):
            value = distribution[key]
            if value == 0:
                if current_start is None:
                    current_start = key
                current_sum += 1
            else:
                if current_start is not None:
                    start, _ = current_start.split('-')
                    start = int(start[:-1])
                    end = int(current_start.split('-')[1][:-1])
                    merged_distribution['{}-{}h'.format(start, end)] = 0
                    current_start = None
                    current_sum = 0
                merged_distribution[key] = value
        # 不处理，连续的0区间直接裁撤
        # # 处理最后一个连续的零值区间
        # if current_start is not None:
        #     start, _ = current_start.split('-')
        #     start = int(start[:-1])
        #     end = int(current_start.split('-')[1][:-1]) + time_interval * current_sum
        #     merged_distribution['>{}h'.format(end)] = 0

        return merged_distribution

    def filter_result(self, result, exclude_last=True):  # 默认排除最后一个区间
        """
        过滤结果，排除最后一个区间
        :param result: 包含各区间停车时长占比的字典
        :param exclude_last: 是否排除最后一个区间，默认为 True
        :return: 过滤后的字典
        """
        keys = list(result.keys())
        if exclude_last and keys:
            exclude_keys = [keys[-1]]
        else:
            exclude_keys = []

        filtered_result = {key: value for key, value in result.items() if key not in exclude_keys}
        return filtered_result

    def generate_parking_time_chart(self, chart_type, figsize=(8, 8)):
        """
        生成饼状图或折线图
        :param chart_type: 图表类型，'pie' 或 'line'
        :param figsize: 图表大小，默认为 (8, 8)
        """
        plt.figure(figsize=figsize)
        labels = list(self.dis.keys())
        values = list(self.dis.values())

        if chart_type == 'pie':
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
            plt.title('Parking Time Distribution')
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        elif chart_type == 'line':
            plt.plot(labels, values, marker='o')
            plt.title('Parking Time Distribution')
            plt.xlabel('Time Interval (Hours)')
            plt.ylabel('Number of Parkings')
            plt.xticks(rotation=45)  # 旋转 x 轴标签
            plt.grid(True)
        elif chart_type == 'bar':
            plt.bar(labels, values)
            plt.title('Parking Time Distribution')
            plt.xlabel('Time Interval (Hours)')
            plt.ylabel('Number of Parkings')
            plt.xticks(rotation=45)  # 旋转 x 轴标签
            plt.grid(axis='y')
        else:
            raise ValueError("Invalid chart type. Use 'pie' or 'line'.")

        plt.tight_layout()  # 自动调整布局
        plt.show()

    def generate_parking_fee_chart(self, chart_type, figsize=(8, 8), filename=None):
        """
        生成图表
        :param chart_type: 图表类型 ('pie', 'line', 'bar')
        :param figsize: 图表大小
        :param filename: 保存图表的文件名，默认为 None 不保存
        """
        plt.figure(figsize=figsize)
        labels = list(self.dis_fee.keys())
        values = list(self.dis_fee.values())

        if chart_type == 'pie':
            plt.pie(values, labels=labels, autopct='%1.1f%%')
            plt.title('Parking Fee Distribution (Pie Chart)')
        elif chart_type == 'line':
            plt.plot(labels, values, marker='o')
            plt.xlabel('Fee Interval')
            plt.ylabel('Count')
            plt.title('Parking Fee Distribution (Line Chart)')
        elif chart_type == 'bar':
            plt.bar(labels, values)
            plt.xlabel('Fee Interval')
            plt.ylabel('Count')
            plt.title('Parking Fee Distribution (Bar Chart)')

        plt.tight_layout()  # 自动调整布局

        if filename:
            plt.savefig(filename)  # 保存图表到文件
        plt.show()  # 显示图表
        plt.close()  # 关闭图形窗口


if __name__ == '__main__':
    # 示例调用
    time_start = "2024-10-01 00:00:00"
    time_end = "2024-10-07 12:00:00"
    fee_interval = 10
    aaaa = parking_data
    aaaa.read_time_from_parking(aaaa, time_start, time_end, 10)
    aaaa.generate_parking_time_chart(aaaa, 'pie')

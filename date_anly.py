import sqlite3
import time
from datetime import datetime


def read_time_from_parking(time_start, time_end, time_interval) -> list:
    """
    从数据库中读取停车时间
    :time_start str
    :time_end str
    :time_interval str
    :return:
    """
    conn = sqlite3.connect('parking.db')  # 连接数据库
    cursor = conn.cursor()

    cursor.execute("SELECT start_time, end_time FROM parking_records")
    rows = cursor.fetchall()
    conn.close()
    print(rows)
    print("---------------------------------")
    for row in rows:
        if row[0] >= time_start and row[1] <= time_end:
            delta = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S") - datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            # 如果需要进一步处理时间差，可以提取天数、小时数、分钟数等
            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds // 60) % 60
            seconds = delta.seconds % 60  # 保留
            print(f"Days: {days}, Hours: {hours}, Minutes: {minutes}, Seconds: {seconds}")

    if not rows:
        print("No matching records found.")


def read_number_from_parking() -> list:
    """
    从数据库中读取停车数量
    :return:
    """
    pass


def read_fee_from_parking(time_start, time_end, time_interval) -> list:
    """
    从数据库中读取停车费用
    :return:
    """
    pass


if __name__ == '__main__':
    read_time_from_parking("2024-10-01 23:36:00", "2024-10-02 21:06:00", "1:00:00")

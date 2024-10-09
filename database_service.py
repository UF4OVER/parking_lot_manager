import sqlite3
import time
from datetime import datetime
from typing import Tuple, Any


def create_database():
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # 创建 vehicles 表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        vehicle_id INTEGER PRIMARY KEY,
        plate_number TEXT NOT NULL UNIQUE,
        type TEXT
    )
    ''')

    # 创建 parking_records 表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking_records (
        record_id INTEGER PRIMARY KEY,
        vehicle_id INTEGER,
        parking_spot TEXT,
        start_time TEXT,
        end_time TEXT,
        duration TEXT,
        fee REAL,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles (vehicle_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("已成功创建数据库")


def add_vehicle(plate_number, vehicle_type):
    print("正在添加车辆...")
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # 检查车牌号是否已存在
    cursor.execute('SELECT vehicle_id FROM vehicles WHERE plate_number = ?', (plate_number,))
    existing_vehicle = cursor.fetchone()

    if existing_vehicle:
        conn.close()
        print(f"车辆{plate_number}已存在")
        return f"车辆{plate_number}已存在"

    # 插入新车辆信息
    cursor.execute('INSERT INTO vehicles (plate_number, type) VALUES (?, ?)', (plate_number, vehicle_type))
    conn.commit()
    conn.close()
    print(f"已成功添加车辆{plate_number}")
    return f"已成功添加车辆{plate_number}"


def start_parking(plate_number, parking_spot) -> str | tuple[str, str]:
    print("正在启动停车...")
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # 获取车辆ID
    cursor.execute('SELECT vehicle_id FROM vehicles WHERE plate_number = ?', (plate_number,))
    vehicle_id = cursor.fetchone()
    if vehicle_id is None:
        conn.close()
        return f"未找到车辆{plate_number}"

    vehicle_id = vehicle_id[0]

    # 检测车辆是否正在停车
    if is_parking(plate_number):
        conn.close()
        return f"车辆{plate_number}已在停放中"

    # 插入停车记录
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO parking_records (vehicle_id, parking_spot, start_time) VALUES (?, ?, ?)',
                   (vehicle_id, parking_spot, current_time))
    conn.commit()
    conn.close()

    print(f"已成功停车{plate_number}")
    return f"已成功停车{plate_number}", parking_spot


def calculate_fee(duration_hours: float) -> float:
    """计算费用，假设每小时10元"""
    return round(duration_hours * 10, 2)


def end_parking(plate_number, fee_calculator=calculate_fee) -> tuple[None, int] | tuple[Any, float]:
    print("正在结束停车...")
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # 获取车辆ID
    cursor.execute('SELECT vehicle_id FROM vehicles WHERE plate_number = ?', (plate_number,))
    vehicle_id_row = cursor.fetchone()
    if vehicle_id_row is None:
        print(f"未找到车辆{plate_number}")
        return None, 0
        conn.close()

    vehicle_id = vehicle_id_row[0]

    # 获取最新的停车记录
    cursor.execute('''
    SELECT 
        record_id, 
        start_time, 
        end_time 
    FROM 
        parking_records 
    WHERE 
        vehicle_id = ? 
    AND 
        end_time IS NULL
    ''', (vehicle_id,))
    record = cursor.fetchone()
    # print(f"获取的记录: {record}")

    if not record:
        print(f"未找到有效的停车{plate_number}记录")
        conn.close()
        return None, 0

    record_id, start_time, end_time = record

    if end_time is not None:
        print(f"车辆{plate_number}已经离开停车场")

        conn.close()
        return None, 0

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 计算停车时长
    start_datetime = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
    duration = end_datetime - start_datetime
    duration_str = str(duration)

    # 计算费用（假设每小时10元）

    hours = duration.total_seconds() / 3600
    fee = fee_calculator(hours)

    # 更新停车记录
    cursor.execute('''
    UPDATE 
        parking_records 
    SET 
        end_time = ?, 
        duration = ?, 
        fee = ? 
    WHERE 
        record_id = ?
    ''', (current_time, duration_str, fee, record_id))
    conn.commit()
    conn.close()

    print(f"车辆{plate_number}已离开停车场。时长: {duration_str}, 费用: {fee}")
    return duration_str, fee


def is_parking(plate_number):
    print(f"正在检查车辆{plate_number}是否正在停车...")
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # 获取车辆ID
    cursor.execute('SELECT vehicle_id FROM vehicles WHERE plate_number = ?', (plate_number,))
    vehicle_id_row = cursor.fetchone()
    if vehicle_id_row is None:
        conn.close()
        return False

    vehicle_id = vehicle_id_row[0]

    # 获取最新的停车记录
    cursor.execute('''
    SELECT 
        record_id, 
        start_time, 
        end_time 
    FROM 
        parking_records 
    WHERE 
        vehicle_id = ? 
    AND 
        end_time IS NULL
    ''', (vehicle_id,))
    record = cursor.fetchone()

    conn.close()

    return record is not None


def get_vehicle_history_paginated(plate_number, page=1, page_size=10):
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # 获取车辆ID
    cursor.execute('SELECT vehicle_id FROM vehicles WHERE plate_number = ?', (plate_number,))
    vehicle_id_row = cursor.fetchone()
    if vehicle_id_row is None:
        return f"未找到车辆{plate_number}"

    vehicle_id = vehicle_id_row[0]

    # 计算偏移量
    offset = (page - 1) * page_size

    # 查询所有历史记录
    cursor.execute('''
    SELECT 
        parking_spot, 
        start_time, 
        end_time, 
        duration, 
        fee 
    FROM 
        parking_records 
    WHERE 
        vehicle_id = ? 
    ORDER BY 
        start_time DESC
    LIMIT ?
    OFFSET ?
    ''', (vehicle_id, page_size, offset))

    records = cursor.fetchall()
    history = []

    for record in records:
        parking_spot, start_time, end_time, duration, fee = record
        is_parking = end_time is None
        if is_parking:
            end_time = f"{plate_number}仍在停车"
            duration = "计算中..."
            fee = "计算中..."

        history.append({
            "停车位": parking_spot,
            "开始时间": start_time,
            "结束时间": end_time,
            "时间长短": duration,
            "费用": fee
        })

    conn.close()
    return history


def find_vehicle_info(plate_number: str) -> dict | str:
    """
    根据车牌号查询车辆的最近一次停车信息。

    :param plate_number: 车牌号
    :return: 包含最近一次停车信息的字典或未找到车辆的信息
    """
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # 获取车辆ID
    cursor.execute('SELECT vehicle_id FROM vehicles WHERE plate_number = ?', (plate_number,))
    vehicle_id_row = cursor.fetchone()
    if vehicle_id_row is None:
        conn.close()
        return f"未找到车辆{plate_number}"

    vehicle_id = vehicle_id_row[0]

    # 查询最新的停车记录
    cursor.execute('''
    SELECT 
        parking_spot, 
        start_time, 
        end_time, 
        duration, 
        fee 
    FROM 
        parking_records 
    WHERE 
        vehicle_id = ? 
    ORDER BY 
        start_time DESC 
    LIMIT 1
    ''', (vehicle_id,))
    record = cursor.fetchone()

    conn.close()

    if record is None:
        return f"未找到车辆{plate_number}的停车记录"

    parking_spot, start_time, end_time, duration, fee = record
    is_parking = end_time is None
    if is_parking:
        end_time = f"{plate_number}仍在停车"
        duration = "计算中..."
        fee = "计算中..."

    return {
        "车牌号": plate_number,
        "停车位": parking_spot,
        "开始时间": start_time,
        "结束时间": end_time,
        "时间长短": duration,
        "费用": fee
    }


def get_parking_vehicles():
    """
    查询数据库中当前正在停车的车辆信息。
    返回一个字典列表，每个字典包含停车位号和车牌号。
    """
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # 查询当前正在停车的记录
    cursor.execute('''
    SELECT pr.parking_spot, v.plate_number 
    FROM parking_records pr
    JOIN vehicles v ON pr.vehicle_id = v.vehicle_id
    WHERE pr.end_time IS NULL
    ''')

    # 获取查询结果
    parking_vehicles = [{'parking_spot': spot, 'plate_number': plate_number} for spot, plate_number in
                        cursor.fetchall()]

    conn.close()
    return parking_vehicles


def clear_all_data():
    print("正在清空所有数据...")
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # 清空 parking_records 表
    cursor.execute('DELETE FROM parking_records')

    # 清空 vehicles 表
    cursor.execute('DELETE FROM vehicles')

    conn.commit()
    conn.close()

    print("已成功清除所有数据")


if __name__ == '__main__':
    clear_all_data()

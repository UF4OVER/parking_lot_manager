import sqlite3
import random
from datetime import datetime, timedelta

# 连接数据库
conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

# 插入车辆信息
vehicles_data = [
    ('京A12345',),
    ('沪B56789',),
    ('粤C23456',),
    ('苏D67890',),
    ('浙E34567',),
    ('渝F78901',),
    ('冀G45678',),
    ('辽H89012',),
    ('吉I56789',),
    ('黑J67890',),
]

# 插入车辆信息
cursor.executemany('INSERT INTO vehicles (plate_number) VALUES (?)', vehicles_data)
conn.commit()

# 生成停车记录
start_date = datetime(2024, 10, 1)
end_date = datetime(2024, 10, 2)

# 生成随机停车记录
parking_records = []
for i in range(30):  # 生成 300 条记录
    vehicle_id = random.randint(1, len(vehicles_data))
    start_time = start_date + timedelta(hours=random.randint(0, 24 * 6))
    end_time = start_time + timedelta(hours=random.randint(1, 24))
    duration = str(end_time - start_time)
    fee = round(random.uniform(0.01, 100.00), 2)

    parking_records.append((vehicle_id, start_time, end_time, duration, fee))

# 插入停车记录
cursor.executemany('''
INSERT INTO parking_records (vehicle_id, start_time, end_time, duration, fee)
VALUES (?, ?, ?, ?, ?)
''', parking_records)
conn.commit()

# 关闭数据库连接
conn.close()

print("测试数据已成功插入数据库。")

import sqlite3
from datetime import datetime, timedelta


def create_database():
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    # 创建书籍信息表
    c.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            publisher TEXT,
            entry_date DATE,
            quantity INTEGER DEFAULT 0
        )
    ''')

    # 创建借阅记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS BorrowRecords (
            borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reader_id INTEGER,
            book_id INTEGER,
            borrow_date DATE,
            due_date DATE,
            return_date DATE,
            FOREIGN KEY (reader_id) REFERENCES Readers(reader_id),
            FOREIGN KEY (book_id) REFERENCES Books(book_id)
        )
    ''')

    # 创建读者信息表
    c.execute('''
        CREATE TABLE IF NOT EXISTS Readers (
            reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT
        )
    ''')

    # 创建管理员信息表
    c.execute('''
        CREATE TABLE IF NOT EXISTS Admins (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def add_book(title, author, publisher, entry_date, quantity):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO Books (title, author, publisher, entry_date, quantity)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, author, publisher, entry_date, quantity))

    conn.commit()
    conn.close()


def update_book(book_id, title=None, author=None, quantity=None):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    if title is not None:
        c.execute('UPDATE Books SET title = ? WHERE book_id = ?', (title, book_id))
    if author is not None:
        c.execute('UPDATE Books SET author = ? WHERE book_id = ?', (author, book_id))
    if quantity is not None:
        c.execute('UPDATE Books SET quantity = ? WHERE book_id = ?', (quantity, book_id))

    conn.commit()
    conn.close()


def delete_book(book_id):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    c.execute('DELETE FROM Books WHERE book_id = ?', (book_id,))

    conn.commit()
    conn.close()


def search_books(title=None, author=None):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    query = 'SELECT * FROM Books'
    params = []

    if title is not None:
        query += ' WHERE title LIKE ?'
        params.append(f'%{title}%')

    if author is not None:
        if title is not None:
            query += ' AND'
        query += ' author LIKE ?'
        params.append(f'%{author}%')

    c.execute(query, tuple(params))
    books = c.fetchall()

    conn.close()
    return books


def borrow_book(reader_id, book_id, borrow_date, due_date):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO BorrowRecords (reader_id, book_id, borrow_date, due_date)
        VALUES (?, ?, ?, ?)
    ''', (reader_id, book_id, borrow_date, due_date))

    # 更新图书库存量
    c.execute('UPDATE Books SET quantity = quantity - 1 WHERE book_id = ?', (book_id,))

    conn.commit()
    conn.close()


def update_borrow_record(borrow_id, return_date):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    c.execute('UPDATE BorrowRecords SET return_date = ? WHERE borrow_id = ?', (return_date, borrow_id))

    # 获取图书 ID 并更新库存量
    c.execute('SELECT book_id FROM BorrowRecords WHERE borrow_id = ?', (borrow_id,))
    book_id = c.fetchone()[0]
    c.execute('UPDATE Books SET quantity = quantity + 1 WHERE book_id = ?', (book_id,))

    conn.commit()
    conn.close()


def get_borrow_records(reader_id=None):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    query = 'SELECT * FROM BorrowRecords'
    params = []

    if reader_id is not None:
        query += ' WHERE reader_id = ?'
        params.append(reader_id)

    c.execute(query, tuple(params))
    records = c.fetchall()

    conn.close()
    return records


def add_reader(name, contact):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO Readers (name, contact)
        VALUES (?, ?)
    ''', (name, contact))

    conn.commit()
    conn.close()


def update_reader(reader_id, name=None, contact=None):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    if name is not None:
        c.execute('UPDATE Readers SET name = ? WHERE reader_id = ?', (name, reader_id))
    if contact is not None:
        c.execute('UPDATE Readers SET contact = ? WHERE reader_id = ?', (contact, reader_id))

    conn.commit()
    conn.close()


def delete_reader(reader_id):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    c.execute('DELETE FROM Readers WHERE reader_id = ?', (reader_id,))

    conn.commit()
    conn.close()


def search_readers(name=None):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    query = 'SELECT * FROM Readers'
    params = []

    if name is not None:
        query += ' WHERE name LIKE ?'
        params.append(f'%{name}%')

    c.execute(query, tuple(params))
    readers = c.fetchall()

    conn.close()
    return readers


def borrow_book(reader_id, book_id):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    # 检查图书库存量
    c.execute('SELECT quantity FROM Books WHERE book_id = ?', (book_id,))
    quantity = c.fetchone()[0]

    if quantity <= 0:
        print("库存不足，无法借阅")
        return

    # 记录借阅信息
    borrow_date = datetime.now().strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    c.execute('''
        INSERT INTO BorrowRecords (reader_id, book_id, borrow_date, due_date)
        VALUES (?, ?, ?, ?)
    ''', (reader_id, book_id, borrow_date, due_date))

    # 更新图书库存量
    c.execute('UPDATE Books SET quantity = quantity - 1 WHERE book_id = ?', (book_id,))

    conn.commit()
    conn.close()


def return_book(borrow_id, return_date):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    # 更新借阅记录
    c.execute('UPDATE BorrowRecords SET return_date = ? WHERE borrow_id = ?', (return_date, borrow_id))

    # 获取图书 ID 并更新库存量
    c.execute('SELECT book_id FROM BorrowRecords WHERE borrow_id = ?', (borrow_id,))
    book_id = c.fetchone()[0]
    c.execute('UPDATE Books SET quantity = quantity + 1 WHERE book_id = ?', (book_id,))

    conn.commit()
    conn.close()


def get_reader_borrow_stats(reader_id):
    conn = sqlite3.connect('library_system.db')
    c = conn.cursor()

    # 获取读者借阅记录总数
    c.execute('SELECT COUNT(*) FROM BorrowRecords WHERE reader_id = ?', (reader_id,))
    total_borrows = c.fetchone()[0]

    # 获取平均借阅量
    c.execute('SELECT AVG(julianday(return_date) - julianday(borrow_date)) FROM BorrowRecords WHERE reader_id = ?',
              (reader_id,))
    avg_days = c.fetchone


if __name__ == '__main__':
    create_database()

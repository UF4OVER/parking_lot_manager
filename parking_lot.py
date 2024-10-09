import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QStyledItemDelegate, QWidget, QVBoxLayout, \
    QStyle
from PyQt5.QtGui import QPainter, QColor, QPainterPath
from PyQt5.QtCore import Qt, QRectF


class CustomDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):  # 重写 paint 方法
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # 获取单元格的尺寸
        rect = option.rect
        radius = min(rect.width(), rect.height()) // 2 - 1

        # 创建一个圆角矩形路径
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)

        # 设置背景色
        if option.state & QStyle.State_Selected:
            bgColor = QColor('#D3D3F0')  # 当单元格被选中时的颜色
        elif option.state & QStyle.State_MouseOver:  # 当鼠标悬停时的颜色
            bgColor = QColor('#FFFFCC')
        else:
            bgColor = QColor('#F0F0F0')
            if index.row() % 2 == 0:
                bgColor = QColor('#E0E0E0')

        painter.fillPath(path, bgColor)

        # 绘制内容
        text = index.data(Qt.DisplayRole)
        painter.drawText(rect, Qt.AlignCenter, text)

        painter.restore()


if __name__ == '__main__':  # debug or test
    app = QApplication([])
    # 创建一个 QTableWidget 实例
    table = QTableWidget(4, 3)  # 4 行 3 列

    # 启用鼠标跟踪
    table.setMouseTracking(True)

    # 隐藏行号和列号
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setVisible(False)

    # 设置单元格的宽度和高度
    column_widths = [100, 150, 200]
    row_heights = [50, 75, 100, 125]

    for col, width in enumerate(column_widths):
        table.setColumnWidth(col, width)

    for row, height in enumerate(row_heights):
        table.setRowHeight(row, height)

    # 填充表格数据，从第1行开始
    for row in range(1, 4):  # 从第1行开始
        for col in range(3):
            item = QTableWidgetItem(f'Row{row} Col{col}')
            table.setItem(row, col, item)

    # 应用自定义委托
    delegate = CustomDelegate(table)
    table.setItemDelegate(delegate)

    # 设置样式表以隐藏网格线
    table.setStyleSheet("""
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

    # 显示表格
    window = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(table)
    window.setLayout(layout)
    window.show()
    app.exec_()

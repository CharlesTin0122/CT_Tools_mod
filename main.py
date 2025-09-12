from PySide6.QtWidgets import QApplication, QScrollBar, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
import sys

app = QApplication(sys.argv)

# 创建主窗口
window = QWidget()
layout = QVBoxLayout(window)

# 创建 QScrollBar
scroll_bar = QScrollBar(Qt.Horizontal)
scroll_bar.setMinimum(0)
scroll_bar.setMaximum(100)
scroll_bar.setSingleStep(1)
scroll_bar.setPageStep(10)

# 创建一个标签，用于显示滚动条的值
label = QLabel("Value: 0")

# 连接信号
scroll_bar.valueChanged.connect(lambda value: label.setText(f"Value: {value}"))

# 添加到布局
layout.addWidget(scroll_bar)
layout.addWidget(label)

window.setLayout(layout)
window.resize(300, 100)
window.show()

sys.exit(app.exec())

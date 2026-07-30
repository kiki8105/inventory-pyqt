from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QTableWidget, QTableWidgetItem, \
    QLineEdit, QPushButton, QDateTimeEdit, QMessageBox, QHeaderView
from PyQt5.QtCore import QDateTime

class HistoryDialog(QDialog):  # 입고/판매 이력 목록 + 등록 팝업 (mode: "stockin" 또는 "sale")
    def __init__(self, db, item, mode, parent=None):
        super().__init__(parent)
        self.db = db
        self.items_code = item[0]
        self.current_price = item[3]
        self.mode = mode
        self.setWindowTitle("입고 이력" if mode == "stockin" else "판매 이력")
        self.resize(400, 400)

        self.table = QTableWidget()
        if mode == "stockin":
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["입고일시", "수량"])
        else:
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["판매일시", "수량", "판매가"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.input_datetime = QDateTimeEdit()
        self.input_datetime.setCalendarPopup(True)
        self.input_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.input_datetime.setDateTime(QDateTime.currentDateTime())
        self.input_quantity = QLineEdit()

        form = QFormLayout()
        form.addRow("일시", self.input_datetime)
        form.addRow("수량", self.input_quantity)

        self.btn_register = QPushButton("입고 등록" if mode == "stockin" else "판매 등록")
        self.btn_register.clicked.connect(self.register_entry)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(form)
        layout.addWidget(self.btn_register)
        self.setLayout(layout)

        self.load_history()

    # 이력 목록을 다시 불러와 테이블에 표시
    def load_history(self):
        self.table.setRowCount(0)
        rows = self.db.fetch_stock_in_history(self.items_code) if self.mode == "stockin" \
            else self.db.fetch_sale_history(self.items_code)

        for row_index, row in enumerate(rows):
            self.table.insertRow(row_index)
            for col_index, value in enumerate(row):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    # 입력한 일시/수량으로 입고 또는 판매 등록
    def register_entry(self):
        quantity = self.input_quantity.text().strip()
        if not quantity.isdigit() or int(quantity) <= 0:
            QMessageBox.warning(self, "오류", "수량은 1 이상의 숫자여야 합니다.")
            return
        quantity = int(quantity)
        entry_datetime = self.input_datetime.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        if self.mode == "stockin":
            ok = self.db.add_stock_in(self.items_code, entry_datetime, quantity)
        else:
            current_number = self.db.fetch_item(self.items_code)[4]
            if quantity > current_number:
                QMessageBox.warning(self, "오류", f"현재 재고({current_number}개)보다 많이 판매할 수 없습니다.")
                return
            ok = self.db.add_sale(self.items_code, entry_datetime, quantity, self.current_price)

        if ok:
            self.input_quantity.clear()
            self.load_history()
        else:
            QMessageBox.critical(self, "실패", "등록 중 오류가 발생했습니다.")

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QCheckBox, QDateEdit, \
    QMessageBox, QLabel
from PyQt5.QtCore import QDate

class EditItemDialog(QDialog):  # 선택한 상품 정보를 수정하는 팝업 폼
    def __init__(self, db, item, parent=None):
        super().__init__(parent)
        self.setWindowTitle("상품 수정")
        self.db = db

        items_code, product_code, name, price, number, min_stock, stockdate, expdate, status = item
        self.items_code = items_code  # 일련번호는 PK라 수정 대상 식별용으로만 사용

        self.label_items_code = QLabel(str(items_code))
        self.input_product_code = QLineEdit(product_code)
        self.input_name = QLineEdit(name)
        self.input_price = QLineEdit(str(price) if price is not None else "")
        self.input_number = QLineEdit(str(number) if number is not None else "")
        self.input_min_stock = QLineEdit(str(min_stock) if min_stock is not None else "")

        self.input_stockdate = QDateEdit()
        self.input_stockdate.setCalendarPopup(True)
        self.input_stockdate.setDate(QDate(stockdate.year, stockdate.month, stockdate.day) if stockdate else QDate.currentDate())

        self.input_expdate = QDateEdit()
        self.input_expdate.setCalendarPopup(True)
        self.input_expdate.setDate(QDate(expdate.year, expdate.month, expdate.day) if expdate else QDate.currentDate())

        self.input_status = QCheckBox("정상 판매 가능")
        self.input_status.setChecked(bool(status))

        form = QFormLayout()
        form.addRow("일련번호", self.label_items_code)
        form.addRow("상품코드", self.input_product_code)
        form.addRow("상품명", self.input_name)
        form.addRow("가격", self.input_price)
        form.addRow("재고", self.input_number)
        form.addRow("적정재고", self.input_min_stock)
        form.addRow("입고일", self.input_stockdate)
        form.addRow("만료일", self.input_expdate)
        form.addRow("상태", self.input_status)

        self.btn_save = QPushButton("저장")
        self.btn_save.clicked.connect(self.save)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_save)
        self.setLayout(layout)

    # 입력값 검증 후 DB에 반영
    def save(self):
        product_code = self.input_product_code.text().strip()
        name = self.input_name.text().strip()
        price = self.input_price.text().strip()
        number = self.input_number.text().strip()
        min_stock = self.input_min_stock.text().strip()
        if not product_code or not name:
            QMessageBox.warning(self, "오류", "상품코드와 상품명은 필수입니다.")
            return
        if price and not price.isdigit():
            QMessageBox.warning(self, "오류", "가격은 숫자여야 합니다.")
            return
        if number and not number.isdigit():
            QMessageBox.warning(self, "오류", "재고는 숫자여야 합니다.")
            return
        if min_stock and not min_stock.isdigit():
            QMessageBox.warning(self, "오류", "적정재고는 숫자여야 합니다.")
            return

        stockdate = self.input_stockdate.date().toString("yyyy-MM-dd")
        expdate = self.input_expdate.date().toString("yyyy-MM-dd")
        status = self.input_status.isChecked()

        ok = self.db.update_item(
            self.items_code, product_code, name,
            int(price) if price else None,
            int(number) if number else None,
            int(min_stock) if min_stock else None,
            stockdate, expdate, status
        )
        if ok:
            self.accept()
        else:
            QMessageBox.critical(self, "실패", "수정 중 오류가 발생했습니다.")

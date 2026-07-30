from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QPushButton, QMessageBox, QDateEdit, QCheckBox, QAbstractItemView, QHeaderView, QLabel, QDateTimeEdit
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QColor
from db_helper import DB, DB_CONFIG
from edit_item_dialog import EditItemDialog

LOW_STOCK_COLOR = QColor("#FFCDD2")  # 부족 재고 행 배경색

class Mainwindow(QMainWindow):
    def __init__(self, store_code):
        super().__init__()
        self.db = DB(**DB_CONFIG)
        self.store_code = store_code
        self.setWindowTitle(f"{store_code} 점포 재고현황")
        self.resize(800, 500)

        central = QWidget()
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)

        # 검색 필터 (상품명/상품코드 키워드 + 가격 범위)
        self.search_keyword = QLineEdit()
        self.search_keyword.setFixedWidth(400)
        self.search_keyword.setPlaceholderText("상품명/상품코드 검색")
        self.search_keyword.textChanged.connect(self.load_items)
        self.search_date = QDateEdit()
        self.search_date.setSpecialValueText("입고일을 선택하세요")
        self.search_date.setMinimumDate(QDate(2026, 1, 1))
        self.search_date.setDate(self.search_date.minimumDate())
        self.date_filter_enabled = False
        self.search_date.setCalendarPopup(True)
        
        self.search_date.dateChanged.connect(self.on_date_changed)

        # self.search_price_min = QLineEdit()
        # self.search_price_min.setPlaceholderText("최소 가격")
        # self.search_price_min.textChanged.connect(self.load_items)
        # self.search_price_max = QLineEdit()
        # self.search_price_max.setPlaceholderText("최대 가격")
        # self.search_price_max.textChanged.connect(self.load_items)

        search_box = QHBoxLayout()
        search_box.addWidget(self.search_keyword)
        search_box.addWidget(self.search_date)
        # search_box.addWidget(self.search_price_min)
        # search_box.addWidget(self.search_price_max)
        vbox.addLayout(search_box)
        self.btn_clear_date = QPushButton('날짜 필터 해제')
        search_box.addWidget(self.btn_clear_date)
        self.btn_clear_date.clicked.connect(self.clear_date_filter)


        # 부족 재고 필터
        self.chk_low_stock_only = QCheckBox("부족한 재고만 보기")
        self.chk_low_stock_only.stateChanged.connect(self.load_items)
        vbox.addWidget(self.chk_low_stock_only)

        # 재고 목록 테이블
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["일련번호", "상품코드", "상품명", "가격", "재고", "적정재고", "재고자산", "입고일", "만료일", "상태"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        vbox.addWidget(self.table)

        # 재고자산 합계 표시
        self.label_total_asset = QLabel("총 재고자산: 0")
        vbox.addWidget(self.label_total_asset)

        # 상품 등록 입력 폼
        self.input_product_code = QLineEdit()
        self.input_name = QLineEdit()
        self.input_price = QLineEdit()
        self.input_number = QLineEdit()
        self.input_min_stock = QLineEdit()
        self.input_stockdate = QDateTimeEdit()
        self.input_stockdate.setCalendarPopup(True)
        self.input_stockdate.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.input_stockdate.setDate(QDate.currentDate())
        self.input_expdate = QDateTimeEdit()
        self.input_expdate.setCalendarPopup(True)
        self.input_expdate.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.input_expdate.setDateTime(self.input_stockdate.dateTime().addYears(1))
        self.input_stockdate.dateTimeChanged.connect(self.on_stockdate_changed)
        self.input_status = QCheckBox("정상 판매 가능")
        self.input_status.setChecked(True)

        form = QFormLayout()
        form.addRow("상품코드", self.input_product_code)
        form.addRow("상품명", self.input_name)
        form.addRow("가격", self.input_price)
        form.addRow("재고", self.input_number)
        form.addRow("적정재고", self.input_min_stock)
        form.addRow("입고일", self.input_stockdate)
        form.addRow("만료일", self.input_expdate)
        form.addRow("상태", self.input_status)
        vbox.addLayout(form)

        # 등록/수정/삭제 버튼
        btn_box = QHBoxLayout()
        self.btn_add = QPushButton("등록")
        self.btn_add.clicked.connect(self.add_item)
        self.btn_edit = QPushButton("수정")
        self.btn_edit.clicked.connect(self.edit_selected_item)
        self.btn_delete = QPushButton("삭제")
        self.btn_delete.clicked.connect(self.delete_selected_item)
        btn_box.addWidget(self.btn_add)
        btn_box.addWidget(self.btn_edit)
        btn_box.addWidget(self.btn_delete)
        vbox.addLayout(btn_box)

        self.load_items()

    def clear_date_filter(self):
        self.search_date.setDate(self.search_date.minimumDate())
        self.date_filter_enabled = False
        self.load_items()


    
    def on_date_changed(self):
        self.date_filter_enabled = True
        self.load_items()

    # 현재 점포의 재고 목록을 불러와 테이블에 표시
    def load_items(self):
        items = self.db.fetch_items(self.store_code)
        show_low_stock_only = self.chk_low_stock_only.isChecked()
        keyword = self.search_keyword.text().strip().lower()
        date = self.search_date.date()
        # price_min_text = self.search_price_min.text().strip()
        # price_max_text = self.search_price_max.text().strip()
        # price_min = int(price_min_text) if price_min_text.isdigit() else None
        # price_max = int(price_max_text) if price_max_text.isdigit() else None
        self.table.setRowCount(0)

        row_index = 0
        for item in items:
            items_code, product_code, name, price, number, min_stock, stockdate, expdate, status = item
            asset = (price or 0) * (number or 0)
            status_text = "판매가능" if status else "판매불가"
            is_low_stock = min_stock is not None and number is not None and number <= min_stock

            if show_low_stock_only and not is_low_stock:
                continue
            if keyword and keyword not in name.lower() and keyword not in product_code.lower():
                continue
            if self.date_filter_enabled and stockdate.date() != date.toPyDate():
                continue

            # if price_min is not None and (price is None or price < price_min):
            #     continue
            # if price_max is not None and (price is None or price > price_max):
            #     continue

            display_values = [items_code, product_code, name, price, number, min_stock, asset, stockdate, expdate, status_text]

            self.table.insertRow(row_index)
            for col_index, value in enumerate(display_values):
                cell = QTableWidgetItem("" if value is None else str(value))
                if is_low_stock:
                    cell.setBackground(LOW_STOCK_COLOR)
                self.table.setItem(row_index, col_index, cell)
            row_index += 1

        self.calculate_total_asset(items)

    # 전체 재고자산(가격 x 수량)을 취합해 라벨에 표시
    def calculate_total_asset(self, items):
        total = sum((price or 0) * (number or 0) for _, _, _, price, number, *_ in items)
        self.label_total_asset.setText(f"총 재고자산: {total:,}")

    # 입력 폼 내용으로 상품 등록
    def add_item(self):
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
            QMessageBox.warning(self, "오류", "수량은 숫자여야 합니다.")
            return
        if min_stock and not min_stock.isdigit():
            QMessageBox.warning(self, "오류", "적정재고는 숫자여야 합니다.")
            return

        stockdate = self.input_stockdate.dateTime().toString("yyyy-MM-dd HH:mm")
        expdate = self.input_expdate.dateTime().toString("yyyy-MM-dd HH:mm")
        status = self.input_status.isChecked()

        ok = self.db.insert_item(
            product_code, self.store_code, name,
            int(price) if price else None,
            int(number) if number else None,
            int(min_stock) if min_stock else None,
            stockdate, expdate, status
        )
        if ok:
            QMessageBox.information(self, "완료", "상품이 등록되었습니다.")
            self.input_product_code.clear()
            self.input_name.clear()
            self.input_price.clear()
            self.input_number.clear()
            self.input_min_stock.clear()
            self.load_items()
        else:
            QMessageBox.critical(self, "실패", "등록 중 오류가 발생했습니다.")

    def on_stockdate_changed(self):
        new_expdate = self.input_stockdate.dateTime().addYears(1)
        self.input_expdate.setDateTime(new_expdate)

    # 선택한 행의 상품 정보를 팝업 폼에서 수정
    def edit_selected_item(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "오류", "수정할 상품을 선택하세요.")
            return

        items_code = int(self.table.item(selected, 0).text())
        item = self.db.fetch_item(items_code)
        if item is None:
            QMessageBox.critical(self, "오류", "해당 상품을 찾을 수 없습니다.")
            return

        dialog = EditItemDialog(self.db, item, self)
        if dialog.exec_() == EditItemDialog.Accepted:
            self.load_items()

    # 선택한 행의 상품 삭제
    def delete_selected_item(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "오류", "삭제할 상품을 선택하세요.")
            return

        items_code = self.table.item(selected, 0).text()
        ok = self.db.delete_item(items_code)
        if ok:
            QMessageBox.information(self, "완료", "상품이 삭제되었습니다.")
            self.load_items()
        else:
            QMessageBox.critical(self, "실패", "삭제 중 오류가 발생했습니다.")

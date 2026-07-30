from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox
from db_helper import DB, DB_CONFIG

MIN_STORE_CODE = 100001  # 사용 가능한 점포번호 범위 하한
MAX_STORE_CODE = 999999  # 사용 가능한 점포번호 범위 상한

class SignupDialog(QDialog):  # 회원가입 전용 창
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("회원가입")
        self.resize(500, 180)
        self.db = DB(**DB_CONFIG)

        self.store_code = QLineEdit()
        self.store_code.setPlaceholderText("100001~999999 사이로 입력")
        self.store_name = QLineEdit()
        self.id = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        self.btn_check_store_code = QPushButton("중복확인")
        self.btn_check_store_code.clicked.connect(self.check_store_code_duplicate)
        self.btn_check_id = QPushButton("중복확인")
        self.btn_check_id.clicked.connect(self.check_id_duplicate)

        store_code_row = QHBoxLayout()
        store_code_row.addWidget(self.store_code)
        store_code_row.addWidget(self.btn_check_store_code)

        id_row = QHBoxLayout()
        id_row.addWidget(self.id)
        id_row.addWidget(self.btn_check_id)

        form = QFormLayout()
        form.addRow("점포번호", store_code_row)
        form.addRow("점포명 (신규 점포일 때만)", self.store_name)
        form.addRow("아이디", id_row)
        form.addRow("비밀번호", self.password)

        self.btn_signup = QPushButton("가입하기")
        self.btn_signup.clicked.connect(self.try_signup)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_signup)
        self.setLayout(layout)

    # 점포번호가 사용 가능한 범위(100001~999999)의 숫자인지 확인
    def is_valid_store_code(self, store_code):
        return store_code.isdigit() and MIN_STORE_CODE <= int(store_code) <= MAX_STORE_CODE

    # 점포번호만 중복 여부 확인 (신규 점포번호면 등록 가능하다고 안내)
    def check_store_code_duplicate(self):
        store_code = self.store_code.text().strip()
        if not store_code:
            QMessageBox.warning(self, "오류", "점포번호를 입력하세요.")
            return
        if not self.is_valid_store_code(store_code):
            QMessageBox.warning(self, "오류", f"점포번호는 {MIN_STORE_CODE}~{MAX_STORE_CODE} 사이의 숫자여야 합니다.")
            return

        if self.db.store_has_user(store_code):
            QMessageBox.critical(self, "중복확인", "이미 사용중인 점포번호입니다.")
        else:
            QMessageBox.information(self, "중복확인", "사용 가능한 점포번호입니다.")

    # 아이디만 중복 여부 확인
    def check_id_duplicate(self):
        uid = self.id.text().strip()
        if not uid:
            QMessageBox.warning(self, "오류", "아이디를 입력하세요.")
            return

        if self.db.id_exists(uid):
            QMessageBox.critical(self, "중복확인", "이미 사용중인 아이디입니다.")
        else:
            QMessageBox.information(self, "중복확인", "사용 가능한 아이디입니다.")

    # 최종 회원가입 처리 (Stores에 없는 점포번호면 입력한 점포명으로 자동 등록)
    def try_signup(self):
        store_code = self.store_code.text().strip()
        store_name = self.store_name.text().strip()
        uid = self.id.text().strip()
        pw = self.password.text().strip()
        if not store_code or not uid or not pw:
            QMessageBox.warning(self, "오류", "점포번호, 아이디, 비밀번호를 모두 입력하세요.")
            return
        if not self.is_valid_store_code(store_code):
            QMessageBox.warning(self, "오류", f"점포번호는 {MIN_STORE_CODE}~{MAX_STORE_CODE} 사이의 숫자여야 합니다.")
            return

        if self.db.store_has_user(store_code):
            QMessageBox.critical(self, "실패", "이미 사용중인 점포번호입니다.")
            return
        if self.db.id_exists(uid):
            QMessageBox.critical(self, "실패", "이미 사용중인 아이디입니다.")
            return

        if not self.db.store_exists(store_code):
            if not store_name:
                QMessageBox.warning(self, "오류", "새로 등록할 점포명을 입력하세요.")
                return
            if not self.db.create_store(store_code, store_name):
                QMessageBox.critical(self, "실패", "점포 등록에 실패했습니다.")
                return

        ok = self.db.register_user(store_code, uid, pw)

        if ok:
            QMessageBox.information(self, "회원가입", "회원가입이 완료되었습니다. 로그인해주세요.")
            self.accept()
        else:
            QMessageBox.critical(self, "실패", "회원가입에 실패했습니다.")

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QComboBox
from db_helper import DB, DB_CONFIG
from signup_dialog import SignupDialog

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log-in")
        self.db = DB(**DB_CONFIG)

        self.store_code = QComboBox()
        self.store_code.addItem('')
        for code, name in self.db.stores():
            self.store_code.addItem(f'{code} - {name}', code)

        self.id = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("점포번호", self.store_code)
        form.addRow("아이디", self.id)
        form.addRow("비밀번호", self.password)

        self.btn_login = QPushButton("로그인")
        self.btn_login.clicked.connect(self.try_login)
        self.btn_login.setStyleSheet("background-color: #B9E0FD; color: black;")

        self.btn_signup = QPushButton("회원가입")
        self.btn_signup.clicked.connect(self.open_signup)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_signup)
        self.setLayout(layout)

    # 회원가입 창을 새로 띄움
    def open_signup(self):
        dialog = SignupDialog(self)
        dialog.exec_()

    def try_login(self):
        store_code = self.store_code.currentData()
        uid = self.id.text().strip()
        pw = self.password.text().strip()
        fields = [
            (store_code, "점포번호를 입력하세요."),
            (uid, "ID를 입력하세요."),
            (pw, "비밀번호를 입력하세요."),
        ]
        for value, message in fields:
            if not value:
                QMessageBox.warning(self, "오류", message)
                return

        if not self.db.store_has_user(store_code):
            self.sign_up(store_code, uid, pw)
            return

        ok = self.db.verify_user(store_code, uid, pw)
        if ok:
            self.logged_in_store_code = store_code
            self.accept()
        else:
            QMessageBox.critical(self, "실패", "아이디 또는 비밀번호가 올바르지 않습니다.")

    # 해당 점포에 계정이 없을 때 입력값으로 신규 등록 후 바로 로그인 처리
    def sign_up(self, store_code, uid, pw):
        if self.db.store_has_user(store_code):
            QMessageBox.critical(self, "실패", "이미 사용중인 점포번호입니다.")
            return
        if self.db.id_exists(uid):
            QMessageBox.critical(self, "실패", "이미 사용중인 아이디입니다.")
            return

        ok = self.db.register_user(store_code, uid, pw)
        if ok:
            QMessageBox.information(self, "회원가입", "회원가입이 완료되어 로그인합니다.")
            self.logged_in_store_code = store_code
            self.accept()
        else:
            QMessageBox.critical(self, "실패", "회원가입에 실패했습니다. 점포번호와 아이디를 확인해주세요.")

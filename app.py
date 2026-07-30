# app.py
import sys
from PyQt5.QtWidgets import QApplication
from login_dialog import LoginDialog
from signup_dialog import SignupDialog
from main import Mainwindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = LoginDialog()
    if login.exec_() == LoginDialog.Accepted:
        w = Mainwindow(login.logged_in_store_code)
        w.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)
# main_window_ex.py
import sys
import base64
import binascii
import traceback
import mysql.connector

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem,
    QFileDialog, QMessageBox
)
from MainWindow import Ui_MainWindow




class MainWindowEx(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.default_avatar = "images/ic_no_avatar.png"
        self.conn = None

        # state hiện tại của bản ghi (không bắt buộc phải dùng ngoài selection)
        self.id = None
        self.code = None
        self.name = None
        self.age = None
        self.avatar = None      # LƯU ý: avatar là base64-STRING (ASCII) hoặc None
        self.intro = None

    # --- Khởi tạo UI & nối signal ---
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # Nối signal
        self.tableWidgetStudent.itemSelectionChanged.connect(self.processItemSelection)
        self.pushButtonAvatar.clicked.connect(self.pickAvatar)
        self.pushButtonRemoveAvatar.clicked.connect(self.removeAvatar)
        self.pushButtonInsert.clicked.connect(self.processInsert)
        self.pushButtonUpdate.clicked.connect(self.processUpdate)
        self.pushButtonRemove.clicked.connect(self.processRemove)

        # avatar mặc định khi mở app
        self.labelAvatar.setPixmap(QPixmap(self.default_avatar))

    def show(self):
        self.MainWindow.show()

    # --- Kết nối MySQL ---
    def connectMySQL(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                port=3306,
                database="studentmanagement",
                user="YOUR_USERNAME_HERE",
                password="YOUR_PASSWORD_HERE",
                autocommit=False,
            )
        except mysql.connector.Error as e:
            QMessageBox.critical(self.MainWindow, "DB Error", f"Cannot connect MySQL:\n{e}")
            raise

    # --- Đổ bảng ---
    def selectAllStudent(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM student")
        rows = cursor.fetchall()
        cursor.close()

        self.tableWidgetStudent.setRowCount(0)
        for r in rows:
            row = self.tableWidgetStudent.rowCount()
            self.tableWidgetStudent.insertRow(row)
            self.tableWidgetStudent.setItem(row, 0, QTableWidgetItem(str(r[0]) if r[0] is not None else ""))
            self.tableWidgetStudent.setItem(row, 1, QTableWidgetItem(r[1] or ""))
            self.tableWidgetStudent.setItem(row, 2, QTableWidgetItem(r[2] or ""))
            self.tableWidgetStudent.setItem(row, 3, QTableWidgetItem(str(r[3]) if r[3] is not None else ""))

    # --- Khi chọn 1 dòng trên bảng ---
    def processItemSelection(self):
        row = self.tableWidgetStudent.currentRow()
        if row == -1:
            return
        try:
            code = self.tableWidgetStudent.item(row, 1).text() if self.tableWidgetStudent.item(row, 1) else None
            if not code:
                return
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM student WHERE code=%s", (code,))
            item = cursor.fetchone()
            cursor.close()
            if item is None:
                print("Not Found")
                return

            self.id, self.code, self.name, self.age, self.avatar, self.intro = \
                item[0], item[1], item[2], item[3], item[4], item[5]

            self.lineEditId.setText(str(self.id) if self.id is not None else "")
            self.lineEditCode.setText(self.code or "")
            self.lineEditName.setText(self.name or "")
            self.lineEditAge.setText(str(self.age) if self.age is not None else "")
            self.lineEditIntro.setText(self.intro or "")

            # Hiển thị avatar an toàn
            pix = QPixmap(self.default_avatar)
            if self.avatar:
                raw = self.avatar
                # DB có thể trả về memoryview/bytearray/bytes/str
                if isinstance(raw, memoryview):
                    raw = raw.tobytes()
                if isinstance(raw, bytearray):
                    raw = bytes(raw)
                if isinstance(raw, bytes):
                    raw = raw.decode("ascii", errors="ignore")
                if isinstance(raw, str):
                    try:
                        img_bytes = base64.b64decode(raw, validate=True)
                        tmp = QPixmap()
                        if tmp.loadFromData(img_bytes):
                            pix = tmp
                    except binascii.Error:
                        pass
            self.labelAvatar.setPixmap(pix)

        except Exception:
            traceback.print_exc()

    # --- Chọn ảnh, preview và lưu base64-string vào self.avatar ---
    def pickAvatar(self):
        filters = "Picture PNG (*.png);;Picture JPG (*.jpg *.jpeg);;All files(*)"
        filename, selected_filter = QFileDialog.getOpenFileName(self.MainWindow, filter=filters)
        if not filename:
            return

        # Preview
        pixmap = QPixmap(filename)
        if not pixmap.isNull():
            self.labelAvatar.setPixmap(pixmap)

        # Lưu base64-string (ASCII) để ghi DB
        with open(filename, "rb") as f:
            b64_bytes = base64.b64encode(f.read())
        self.avatar = b64_bytes.decode("ascii")

    # --- Xóa avatar (về mặc định) ---
    def removeAvatar(self):
        self.avatar = None
        self.labelAvatar.setPixmap(QPixmap(self.default_avatar))

    # --- Thêm mới ---
    def processInsert(self):
        try:
            cursor = self.conn.cursor()
            sql = "INSERT INTO student(Code,Name,Age,Avatar,Intro) VALUES(%s,%s,%s,%s,%s)"

            self.code = self.lineEditCode.text().strip()
            self.name = self.lineEditName.text().strip()
            self.age = int(self.lineEditAge.text()) if self.lineEditAge.text().strip() else None
            self.intro = self.lineEditIntro.text().strip()

            if not hasattr(self, "avatar"):
                self.avatar = None

            val = (self.code, self.name, self.age, self.avatar, self.intro)
            cursor.execute(sql, val)
            self.conn.commit()

            self.lineEditId.setText(str(cursor.lastrowid))
            cursor.close()
            self.selectAllStudent()
        except Exception:
            traceback.print_exc()

    # --- Cập nhật ---
    def processUpdate(self):
        try:
            cursor = self.conn.cursor()
            sql = ("UPDATE student SET Code=%s,Name=%s,Age=%s,Avatar=%s,Intro=%s "
                   "WHERE Id=%s")

            if not self.lineEditId.text().strip():
                QMessageBox.warning(self.MainWindow, "Warning", "Chưa chọn bản ghi để cập nhật.")
                cursor.close()
                return

            self.id = int(self.lineEditId.text())
            self.code = self.lineEditCode.text().strip()
            self.name = self.lineEditName.text().strip()
            self.age = int(self.lineEditAge.text()) if self.lineEditAge.text().strip() else None
            self.intro = self.lineEditIntro.text().strip()

            if not hasattr(self, "avatar"):
                self.avatar = None

            val = (self.code, self.name, self.age, self.avatar, self.intro, self.id)
            cursor.execute(sql, val)
            self.conn.commit()

            cursor.close()
            self.selectAllStudent()
        except Exception:
            traceback.print_exc()

    # --- Xóa ---
    def processRemove(self):
        dlg = QMessageBox(self.MainWindow)
        dlg.setWindowTitle("Confirmation Deleting")
        dlg.setText("Are you sure you want to delete?")
        dlg.setIcon(QMessageBox.Icon.Question)
        buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        dlg.setStandardButtons(buttons)

        if dlg.exec() == QMessageBox.StandardButton.No:
            return

        try:
            if not self.lineEditId.text().strip():
                QMessageBox.warning(self.MainWindow, "Warning", "Chưa chọn bản ghi để xóa.")
                return

            cursor = self.conn.cursor()
            sql = "DELETE FROM student WHERE Id=%s"
            val = (self.lineEditId.text().strip(),)
            cursor.execute(sql, val)
            self.conn.commit()
            cursor.close()

            self.selectAllStudent()
            self.clearData()
        except Exception:
            traceback.print_exc()

    # --- Clear form ---
    def clearData(self):
        self.lineEditId.setText("")
        self.lineEditCode.setText("")
        self.lineEditName.setText("")
        self.lineEditAge.setText("")
        self.lineEditIntro.setText("")
        self.avatar = None
        self.labelAvatar.setPixmap(QPixmap(self.default_avatar))


# --- (Tùy chọn) Hàm chạy thử nhanh file này ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = QMainWindow()
    ui = MainWindowEx()
    ui.setupUi(mw)

    # Kết nối DB & đổ dữ liệu
    try:
        ui.connectMySQL()
        ui.selectAllStudent()
    except Exception:
        pass  # đã hiện QMessageBox trong connectMySQL nếu lỗi

    ui.show()
    sys.exit(app.exec())


# MainWindowEx.py
import requests
from PyQt6.QtWidgets import QMainWindow

from Api.MainWindow import Ui_MainWindow


class MainWindowEx(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.trans)

    def trans(self):
        text = self.lineEditText.text().strip()
        source_lang = self.comboBoxSource.currentText()
        target_lang = self.comboBoxTarget.currentText()

        if not text:
            self.labelResult.setText("Please enter text.")
            return

        try:
            url = f"https://lingva.ml/api/v1/{source_lang}/{target_lang}/{text}"
            response = requests.get(url, timeout=10)
            translated_text = response.json().get("translation", "")
            self.labelResult.setText(translated_text)
        except Exception as e:
            self.labelResult.setText(f"Error: {str(e)}")


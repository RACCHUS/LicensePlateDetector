from PyQt5.QtWidgets import QMessageBox

class Notifier:
    @staticmethod
    def info(parent, message, title="Info"):
        QMessageBox.information(parent, title, message)

    @staticmethod
    def error(parent, message, title="Error"):
        QMessageBox.critical(parent, title, message)

    @staticmethod
    def warn(parent, message, title="Warning"):
        QMessageBox.warning(parent, title, message)

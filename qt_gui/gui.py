from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
import sys

from expression_processor.evaluator_wrapper import EvaluatorWrapper
from expression_processor.parsing_tasks import check_for_constraint
from samples_processor.samples_processing import fun_mnk
from samples_processor.samples_processing import Main


class MainUI(QMainWindow):
    __formula_count = 0
    __list_of_widgets = []

    def __init__(self):
        super(MainUI, self).__init__()
        loadUi("qt_gui/main_window.ui", self)
        self.resize(1280, 720)
        self.setWindowIcon(QtGui.QIcon('qt_gui/icon.ico'))
        self.setWindowTitle("Средство функционального проектирования")
        self.evaluate_pb.clicked.connect(self.__evaluate)
        self.add_expression_pb.clicked.connect(self.__add_expression)
        self.select_file_pb.clicked.connect(self.show_dialog)
        self.evaluate_pb_.clicked.connect(self.__evaluate_MNK)

        # Remove demo widget
        while self.formula_hl_demo.count():
            item = self.formula_hl_demo.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.verticalLayout_9.removeItem(self.formula_hl_demo)
        del self.formula_hl_demo

        # Add first formula
        self.__add_expression()

        # Other
        self.verticalLayout_9.setSpacing(8)

    def __evaluate(self):
        self.clear_label()
        formulas = []
        for i in range(len(self.__list_of_widgets)):
            lineEdit = self.__list_of_widgets[i]
            formulas.append(lineEdit.text())
        for i in range(len(formulas)):
            formula = formulas[i]
            answer = Main().process_formula(formula)
            if answer is None:
                if self.__list_of_widgets[i].text() == "":
                    pass
                else:
                    self.print_to_label(f"F<sub>{i}</sub> имеет неверный формат")
            else:
                if check_for_constraint(formula):
                    if bool(answer):
                        substr = "Истина"
                    else:
                        substr = "Ложь"
                    self.print_to_label(f"F<sub>{i}(ограничение)</sub> = {substr}")
                else:
                    self.print_to_label(f"F<sub>{i}</sub> = {answer}")

    def print_to_label(self, obj):
        prev_text = self.answer_label.text()
        self.answer_label.setText(prev_text + str(obj) + "<br>")

    def show_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Выбор текстового файла", "",
                                                  "Текстовые файлы (*.txt);;Все файлы (*)", options=options)
        if fileName:
            self.lineEdit_11.setText(f'{fileName}')
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    fileContent = file.read()
                    self.textBrowser.setPlainText(fileContent)
            except Exception as e:
                self.show_error("Ошибка при открытии файла: " + str(e))

    def clear_label(self):
        self.answer_label.setText("")

    def __add_expression(self):
        if (self.__formula_count >= 32):
            return
        formula_hl = QtWidgets.QHBoxLayout()
        formula_hl.setSpacing(8)
        formula_hl.setObjectName("formula_hl" + str(self.__formula_count))
        label = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        label.setFont(font)
        label.setObjectName("label_" + str(self.__formula_count))
        label.setText("F<sub>" + str(self.__formula_count) + "</sub> ↔ ")
        formula_hl.addWidget(label)
        lineEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(lineEdit.sizePolicy().hasHeightForWidth())
        lineEdit.setSizePolicy(sizePolicy)
        lineEdit.setMaximumSize(QtCore.QSize(16777215, 40))
        lineEdit.setClearButtonEnabled(True)
        font = QtGui.QFont()
        font.setFamily("Cambria Math")
        font.setPointSize(12)
        lineEdit.setFont(font)
        lineEdit.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        lineEdit.setObjectName("lineEdit_" + str(self.__formula_count))
        formula_hl.addWidget(lineEdit)
        self.__list_of_widgets.append(lineEdit)
        self.__formula_count += 1
        self.verticalLayout_9.addLayout(formula_hl)

    def __evaluate_MNK(self):
        formula = self.lineEdit_10.text()
        filename = self.lineEdit_11.text()
        try:
            parts = Main().process_mnk(formula)
        except Exception as e:
            self.show_error("Ошибка при распознавании формата формулы: " + str(e))

        if filename != "":
            try:
                coefs = fun_mnk(filename, formula)
                str1 = ""
                print(coefs)
                for i in range(len(coefs) - 1):
                    str1 += f"a{i} = {coefs[i]}" + '<br>'
                str1 += f"Свободный член = {coefs[-1]}" + '<br>'
                self.result_label.setText(str1)
            except Exception as e:
                self.show_error("Ошибка при расчете коэффициентов линейной регрессии: " + str(e))

    def show_error(self, error_text):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(error_text)
        msg_box.setWindowTitle("Ошибка")
        msg_box.exec_()

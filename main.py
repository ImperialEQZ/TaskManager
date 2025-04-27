import os
import sys
import json #json файл вместо БД
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QMessageBox, QScrollArea, QCheckBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QLinearGradient, QBrush


class TaskElement(QWidget):# отдельный элемент задачи в списке задач
    def __init__(self, text, colorID = 0, parent = None):# конструктор
        super().__init__(parent)# родительский виджет к которому будет пренадлежать TaskElement
        self.colorIndex = colorID
        self.text = text
        self.buildUi()
        self.designVisuals()

    def buildUi(self):# создание визуала
        self.layout = QHBoxLayout(self)# создание макета для размещения элементов внутри виджета
        self.layout.setContentsMargins(10, 15, 10, 15)# установка отступов (по часовой стрелке)

        self.checkbox = QCheckBox() # создание checkbox для галочки о выпонлении задачи
        self.checkbox.setFixedSize(25, 25)# фиксированный размер "точки" (флажка) о выполнении

        self.label = QLabel(self.text)# создание текста задачи
        self.label.setFont(QFont('Times New Roman', 14, QFont.Coursiv))# вид шрифта, размер, курсив

        self.delete_btn = QPushButton("✕")# создание кнопки с крестиком для удаления задачи
        self.delete_btn.setFixedSize(25, 25)# фиксированный размер

        # добавляем все в QHBoxLayout
        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)
        self.layout.addStretch() # нужно, чтобы элементы были прижаты к левой стороне, а кнопка удаления - справа
        self.layout.addWidget(self.delete_btn)

    def designVisuals(self):
        taskColors = [
            "#20B2AA", "#00FFFF", "#87CEFA", "#00008B",
            "#1E90FF", "#40E0D0", "#00CED1", "#00FF00",
            "#BB6C8A", "#8B008B", "#4B0082", "#6A5ACD",
            "#9ACD32", "#FFBCD9", "#FFAAA6", "#000080"
        ]# список с кодами цветов

        # Выбор цвета фона из списка на основе индекса цвета
        backgroundColor = taskColors[self.colorIndex % len(taskColors)]# Использование % len(task_colors) для циклического перебора цветов, если индекс цвета выходит за пределы списка


        textColor = "#343E40" if self.colorIndex % 4 < 2 else "#FFFAFA"# Определение цвет текста в зависимости от индекса цвета

        # установление css стилей для виджета
        self.setStyleSheet(f"""
            TaskItem {{
                background-color: {backgroundColor};
                border-radius: 15px;
                margin: 8px 0;
            }}
            TaskItem:hover {{
                background-color: {QColor(backgroundColor).lighter(110).name()};
            }}
            QLabel {{
                color: {textColor};
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid #00CED1;
                border-radius: 10px;
            }}
            QCheckBox::indicator:checked {{
                background-color: #3EB489;
                border: 3px solid #3EB489;
            }}
            QPushButton {{
                background-color: transparent;
                color: {textColor};
                font-size: 18px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                color: #7366BD;
            }}
        """)
class TasksContainer(QWidget):# контейнер для задач
    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)# автоматические размещение виджетов друг под другом
        self.layout.setContentsMargins(5)# отступы везде по 5px
        self.layout.setSpacing(12)# расстояние между виджетами, размещенными в макете 12 px
        self.layout.addStretch()# все виджеты задач "прилипают" к верхней части контейнера, а "остаток пространства" - внизу

    def addTaskWidget(self, widget, index):# добавление виджета в макет по указанному индексу
        self.layout.insertWidget(index, widget)

    def clearTasks(self):# очистить все виджеты задач из контейнера
        while self.layout.count() > 1:# пока есть больше 1 элемента в контейнере
            item = self.layout.takeAt(0)# извлекаем элемент с индексом 0 из контейнера (0 - виджет на самом верху)
            # предотвращение утечки памяти
            if item.widget():
                item.widget().deleteLater()# если элемент является виджетом, метод deleteLater() "планирует" удаление виджета

class MainTaskWindow(QMainWindow):# главное окно приложения
    def __init__(self, controller):# конструктор
        super().__init__()
        self.controller = controller # контролер для реализации логики
        self.WindowSetup()
        self.initializationUI()

    def WindowSetup(self):# настрояка главного виджета (окна)
        self.setWindowTitle("Task Manager")# название заголовочного окна
        self.setFixedSize(700, 700)# фиксированный размер окна
        self.setWindowIcon(QIcon("img/TaskManager.png"))# иконка окна

    def initializationUI(self):
        centralWidget = QWidget()# центральный виджет для всех элементов UI
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)# основной макет для организации всех элементов UI
        mainLayout.setContentsMargins(25)# отступы вокруг элементов
        mainLayout.setSpacing(20)# расстояние между элементами

        # Заголовок
        title = QLabel("TASK MANAGER")# создание и настраивание заголовка
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)# выравнивание по центру
        mainLayout.addWidget(title)

        # Показ статистики из менеджера задач
        self.statsLabel = QLabel("0 задач | 0 завершено")
        self.statsLabel.setObjectName("stats")
        self.statsLabel.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.statsLabel)

        # окно ввода
        inputLayout = QHBoxLayout()
        inputLayout.setSpacing(15)

        # Ввод задачи
        self.taskInput = QLineEdit()
        self.taskInput.setPlaceholderText("Введите новую задачу*")
        self.taskInput.setMinimumHeight(45)
        inputLayout.addWidget(self.taskInput)
        # кнопка добавить задачу и ее характеристики
        self.addButton = QPushButton("ДОБАВИТЬ")
        self.addButton.setFixedWidth(120)
        self.addButton.setMinimumHeight(45)
        self.addButton.clicked.connect(self.controller.addTask)
        inputLayout.addWidget(self.addButton)

        mainLayout.addLayout(inputLayout)

        # Область "прокрутки" задач
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        # контейнер с задачами
        self.tasksContainer = TasksContainer()
        scrollArea.setWidget(self.tasksContainer)

        mainLayout.addWidget(scrollArea)

        # основые кнопки
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(15)
        # кнопка очистить все
        self.clearButton = QPushButton("ОЧИСТИТЬ")
        self.clearButton.clicked.connect(self.controller.clearTasks)
        buttonLayout.addWidget(self.clearButton)

        buttonLayout.addStretch()

        # кнопка сохранения
        self.saveButton = QPushButton("СОХРАНИТЬ")
        self.saveButton.clicked.connect(self.controller.saveTasks)
        buttonLayout.addWidget(self.saveButton)

        mainLayout.addLayout(buttonLayout)
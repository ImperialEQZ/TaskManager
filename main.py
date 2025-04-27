import sys
import json  # json файл вместо БД
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QMessageBox, QScrollArea, QCheckBox)
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QIcon, QFont, QColor


class TaskElement(QWidget):  # отдельный элемент задачи в списке задач
    def __init__(self, text, parent = None):  # конструктор
        super().__init__(parent)  # родительский виджет к которому будет пренадлежать TaskElement
        self.text = text
        self.buildUi()
        self.designVisuals()

    def buildUi(self):  # создание визуала
        self.layout = QHBoxLayout(
            self)  # создание макета для размещения элементов внутри виджета
        self.layout.setContentsMargins(10, 15, 10, 15)  # установка отступов (по часовой стрелке)

        self.checkbox = QCheckBox()  # создание checkbox для галочки о выполнении задачи
        self.checkbox.setFixedSize(25, 25)  # фиксированный размер "точки" (флажка) о выполнении

        self.label = QLabel(self.text)  # создание текста задачи
        self.label.setFont(
            QFont('Times New Roman', 14))  # вид шрифта, размер

        self.delete_btn = QPushButton("❌")  # создание кнопки с крестиком для удаления задачи
        self.delete_btn.setFixedSize(25, 25)  # фиксированный размер

        # добавляем все в QHBoxLayout
        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)
        self.layout.addStretch(
        )  # нужно, чтобы элементы были прижаты к левой стороне, а кнопка удаления - справа
        self.layout.addWidget(self.delete_btn)

    def designVisuals(self):
        backgroundColor = "#00FFFF"
        textColor = "#000000"
        # установление css стилей для виджета
        self.setStyleSheet(f"""
            TaskElement {{
                background-color: {backgroundColor};
                border-radius: 10px;
                margin: 8px 0;
            }}
            TaskElement:hover {{
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
                border: 1px solid #3EB489;
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
class TasksContainer(QWidget):  # контейнер для задач
    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(
            self)  # автоматические размещение виджетов друг под другом
        self.layout.setContentsMargins(QMargins(5, 5, 5, 5))  # отступы везде по 5px
        self.layout.setSpacing(12)  # расстояние между виджетами, размещенными в макете 12 px
        self.layout.addStretch(
        )  # все виджеты задач "прилипают" к верхней части контейнера, а "остаток пространства" - внизу

    def addTaskWidget(self, widget, index):  # добавление виджета в макет по указанному индексу
        self.layout.insertWidget(index, widget)

    def clearTasks(self):  # очистить все виджеты задач из контейнера
        while self.layout.count() > 1:  # пока есть больше 1 элемента в контейнере
            item = self.layout.takeAt(0)  # извлекаем элемент с индексом 0 из контейнера (0 - виджет на самом верху)
            # предотвращение утечки памяти
            if item.widget():
                item.widget().deleteLater()  # если элемент является виджетом, метод deleteLater() "планирует" удаление виджета


class MainTaskWindow(QMainWindow):  # главное окно приложения
    def __init__(self, controller):  # конструктор
        super().__init__()
        self.controller = controller  # контролер для реализации логики
        self.WindowSetup()
        self.initializationUI()

    def WindowSetup(self):  # настрояка главного виджета (окна)
        self.setWindowTitle("Task Manager")  # название заголовочного окна
        self.resize(700, 700) # изменено, для поддержки полного окна
        self.setWindowIcon(QIcon("img/TaskManager.png"))  # иконка окна
        self.showMaximized() # сразу открываем в полное окно

    def initializationUI(self):
        centralWidget = QWidget()  # центральный виджет для всех элементов UI
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(
            centralWidget)  # основной макет для организации всех элементов UI
        mainLayout.setContentsMargins(QMargins(25,25,25,25))  # отступы вокруг элементов
        mainLayout.setSpacing(20)  # расстояние между элементами

        # Заголовок
        title = QLabel("Управление задачами")  # создание и настраивание заголовка
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)  # выравнивание по центру
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
        self.addButton.clicked.connect(self.controller.add_task)
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
        self.clearButton.clicked.connect(self.controller.clear_tasks)
        buttonLayout.addWidget(self.clearButton)

        buttonLayout.addStretch()

        # кнопка сохранения
        self.saveButton = QPushButton("СОХРАНИТЬ")
        self.saveButton.clicked.connect(self.controller.save_tasks)
        buttonLayout.addWidget(self.saveButton)

        mainLayout.addLayout(buttonLayout)


class TaskData:
    def __init__(self):  # конструктор
        self.tasks = []  # Инициализация пустого список для хранения словарей задач
        self.taskCounter = 0  # счетчик задач

    def addTask(self, text):  # добавление задачи
        self.tasks.append({
            "text": text,  # добавляем текст
            "completed": False,  # статус выполнения по умолчанию False
        })
        self.taskCounter += 1  # обновляем счетчик задач

    def toggleTaskCompletion(self, index, completed):
        if 0 <= index < len(self.tasks):  # является ли индекс допустимым
            self.tasks[index]["completed"] = completed  # Обновляет статус выполнения задачи

    def deleteTask(self, index):  # удаление задачи
        if 0 <= index < len(self.tasks):  # является ли индекс допустимым
            self.tasks.pop(index)  # удаление по указанному индексу

    def clearTasks(self):  # очищает список задач и сбрасывает счетчик
        self.tasks = []
        self.taskCounter = 0

    def saveTasks(self):  # сохраняет данные о задачах в tasks.json
        try:
            with open('tasks.json', 'w', encoding='utf-8') as f:  # открытие файла
                json.dump({  # сериализует данные в формат JSON
                    "tasks": self.tasks,
                    "counter": self.taskCounter
                },
                          f,
                          ensure_ascii=False,
                          indent = 4)
        except Exception as e:
            print(f"Ошибка сохранения задачи: {e}")

    def loadTasks(self):  # загружает данные о задачах из файла tasks.json
        try:
            with open('tasks.json', 'r', encoding = 'utf-8') as f:
                data = json.load(f)
                self.tasks = data.get("tasks", [])
                self.taskCounter = data.get("counter", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []
            self.taskCounter = 0


class TaskManagerController:
    def __init__(self):
        self.model = TaskData() # экземпляр класса TaskData, который управляет данными о задачах.
        self.view = MainTaskWindow(self) # экземпляр класса MainTaskWindow, представляющего главное окно приложения
        self.setupStyles() # применение стилей к представлению
        self.model.loadTasks() # загрузка данных о задачах из JSON файла
        self.update_tasks_display() # Обновляет отображение задач в окне на основе данных, загруженных из модели.

    def setupStyles(self):
        mainColor = "#4169E1" # основной цвет (фон)
        surroundingsColor = "#40E0D0" # цвет окружения
        warningColor = "#FF4500" # цвет кнопки предупреждения

        self.view.setStyleSheet(f"""
            QMainWindow {{
                background: {mainColor};
            }}
            QPushButton {{
                background-color: {surroundingsColor};
                color: #FFFAFA;
                border: none;
                border-radius: 15px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #00CED1;
            }}
            QPushButton:pressed {{
                background-color: #4682B4;
            }}
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid {surroundingsColor};
                border-radius: 12px;
                padding: 10px 15px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                selection-background-color: {surroundingsColor};
            }}
            QLineEdit:focus {{
                border: 2px solid {surroundingsColor};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: rgba(255, 255, 255, 0.1);
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {surroundingsColor};
                min-height: 30px;
                border-radius: 5px;
            }}
            QLabel#title {{
                font-size: 32px;
                font-weight: bold;
                color: white;
                padding: 10px 0;
            }}
            QLabel#stats {{
                font-size: 14px;
                color: rgba(255, 255, 255, 0.8);
                padding: 5px 0;
                font-weight: bold;
            }}
        """)
        self.view.clearButton.setStyleSheet(f"""
    QPushButton {{
        background-color: {warningColor};
        color: white;
        border: none;
        border-radius: 15px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: bold;
        min-width: 100px;
    }}
    QPushButton:hover {{
        background-color: #FF6347;
    }}
    QPushButton:pressed {{
        background-color: #E53935;
        padding: 12px 18px 8px 22px;
    }}
""")

    def add_task(self):
        task_text = self.view.taskInput.text().strip() # получение текста задачи из поля ввода (с удалением лишних пробелов)
        if task_text:
            self.model.addTask(task_text)
            self.view.taskInput.clear()
            self.update_tasks_display()
        else:
            # изменнено!
            # Показываем предупреждение
            QMessageBox.warning(
                self.view,
                "Предупреждение!",
                "Задача не может быть без названия!",
                QMessageBox.Ok,
                QMessageBox.Ok
            )
            self.view.taskInput.setFocus()  # Возвращаем фокус в поле ввода задачи

    def update_tasks_display(self):
        self.view.tasksContainer.clearTasks()

        for i, task in enumerate(self.model.tasks):
            item = TaskElement(task["text"])
            item.checkbox.setChecked(task["completed"])
            item.checkbox.stateChanged.connect(
                lambda state, idx=i: self.toggle_task_completion(idx, state))
            item.delete_btn.clicked.connect(
                lambda _, idx=i: self.delete_task(idx))

            if task["completed"]:
                item.label.setStyleSheet("text-decoration: line-through;")

            self.view.tasksContainer.addTaskWidget(item, i)
        # переработана система выполнения задач, теперь есть и процентное соотошение
        completed = sum(1 for task in self.model.tasks if task["completed"])
        total = len(self.model.tasks)
        if total == 0:
            self.view.statsLabel.setText("Нет задач")# нет задач, если ничего не добавлено
        elif completed == total:
            self.view.statsLabel.setText(f"Все задачи выполнены ({total}) Вы молодец!")
        else:
            self.view.statsLabel.setText(f"Задач: {total} | Выполнено: {completed} ({completed / total:.0%})")# выполнение в процентах

    def toggle_task_completion(self, index, state):
        self.model.toggleTaskCompletion(index, state == Qt.Checked)
        self.update_tasks_display()

    def delete_task(self, index):
        self.model.deleteTask(index)
        self.update_tasks_display()

    def clear_tasks(self):
        if self.model.tasks:
            reply = QMessageBox.question(
                self.view,
                'Подтверждение',
                'Вы уверены, что хотите удалить все задачи?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No) # тут к сожалению не могу по русски сделать

            if reply == QMessageBox.Yes:
                self.model.clearTasks()
                self.update_tasks_display()

    def save_tasks(self):
        try:
            self.model.saveTasks()
            QMessageBox.information(self.view, "Сохранено",
                                    "Задачи успешно сохранены!")
        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка",
                                 f"Не удалось сохранить задачи: {str(e)}")

    def closeEvent(self, event):
        self.save_tasks()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    controller = TaskManagerController()
    controller.view.show()
    sys.exit(app.exec_())

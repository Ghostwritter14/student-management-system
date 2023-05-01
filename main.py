import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QComboBox, QToolBar, QStatusBar, QMessageBox
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Contact-number"))
        self.table.verticalHeader().setVisible(False)  # to remove the index column which is not required
        self.setCentralWidget(self.table)

        # Create toolbar and its elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        # Adding the functionality
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and add its elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # detect a call from user
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)  # to avoid duplication of data
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created by Soham Chakraborty while learning Python
        """
        self.setText(content)


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are sure you want to delete the record?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get selected row and student id
        index = student_system.table.currentRow()
        student_id = student_system.table.item(index, 0).text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        student_system.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success! ")
        confirmation_widget.setText("The record was deleted successfully! ")
        confirmation_widget.exec()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Window Title and dimensions
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # get student name
        index = student_system.table.currentRow()
        student_name = student_system.table.item(index, 1).text()  # index row and column

        # get id
        self.student_id = student_system.table.item(index, 0).text()

        # Add student_name widgets
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add ComboBox of courses
        course_name = student_system.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Computer Science", "Physics", "Economics", "History", "Astronomy"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Add phone number widget
        mobile = student_system.table.item(index, 3).text()
        self.contact_number = QLineEdit(mobile)
        self.contact_number.setPlaceholderText("Contact-Number")
        layout.addWidget(self.contact_number)

        # Add submit button
        button = QPushButton("Update Student")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course =?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.contact_number.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        student_system.load_data()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Window Title and dimensions
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student_name widgets
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add ComboBox of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Computer Science", "Physics", "Economics", "History", "Astronomy"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add phone number widget
        self.contact_number = QLineEdit()
        self.contact_number.setPlaceholderText("Contact-Number")
        layout.addWidget(self.contact_number)

        # Add submit button
        button = QPushButton("Register Student")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()  # extract text from variable
        course = self.course_name.itemText(self.course_name.currentIndex())  # item text for combo-boxes
        phone = self.contact_number.text()  #
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES(?, ?, ?)",
                       (name, course, phone))
        connection.commit()
        cursor.close()
        connection.close()
        student_system.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set the title and size
        self.setWindowTitle("Search Student by Name")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create the layout
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)

        # matching the search with the exact item
        items = student_system.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            # get the index of the item and index of the column
            student_system.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
student_system = MainWindow()
student_system.show()
student_system.load_data()
sys.exit(app.exec())

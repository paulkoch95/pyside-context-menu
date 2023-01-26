import sys
from PySide6 import QtGui, QtWidgets, QtCore
from PySide6.QtGui import QKeySequence, QShortcut, QCursor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QGraphicsView


class GraphicsView(QGraphicsView):
    def mousePressEvent(self, event):
        p = event.pos() # relative to widget
        gp = self.mapToGlobal(p) # relative to screen
        rw = self.window().mapFromGlobal(gp) # relative to window
        print("position relative to window: ", rw)
        super(GraphicsView, self).mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        scene = QtWidgets.QGraphicsScene(self)
        view = GraphicsView(scene, self)
        self.setCentralWidget(view)
        QShortcut(QKeySequence(Qt.Key.Key_Tab), self, activated=self.toggle_menu)

    def toggle_menu(self):
        print("Toggle context menu at ")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.resize(500, 500)
    main_window.show()
    sys.exit(app.exec_())
from PySide2 import QtWidgets, QtCore, QtGui
import sys

class MyView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(MyView, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Tab:
            print("Tab")
            return True


app = QtWidgets.QApplication(sys.argv)

scene = QtWidgets.QGraphicsScene(0, 0, 400, 200)

view = MyView(scene)

view.show()
sys.exit(app.exec_())
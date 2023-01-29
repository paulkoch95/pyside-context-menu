import os
os.environ['QT_MAC_WANTS_LAYER'] = '1'

from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QPushButton , QGraphicsView, QGraphicsItem, QShortcut, QWidget, QVBoxLayout, QLabel, QLineEdit, QMenu, QGridLayout, QAction, QLayout
from PySide2.QtGui import QBrush, QPen, QFont, QKeySequence, QCursor, QPalette, QColor, QIcon
from PySide2.QtCore import Qt, Slot, QDir, QFileInfo
import sys
import difflib

class RichContextMenu(QWidget):

    def __init__(self, parent=None):
        super(RichContextMenu, self).__init__(parent)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.options = []
        self.icons = self.load_icons()
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(128,128,128))

        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.menue_style_sheet = """
                                QMenu {
                                    background: #555555;
                                }
                                QMenu:item:selected {
                                    background: darkGray;
                                }
                                QMenu:item {
                                    color: white;
                                    padding: 4px;
                                }
                                """

        self.search_menu = QLineEdit()
        self.search_menu.setPlaceholderText("search...")
        self.search_menu.setStyleSheet("QLineEdit { border: 2px solid black; background-color: white;}")

        self.search_menu.textChanged[str].connect(self.search_results)

        self.primary_menue = QMenu()
        self.primary_menue.setStyleSheet(self.menue_style_sheet)

        self.primary_menue.aboutToHide.connect(lambda: self.prevent_deletion(self.primary_menue))

        self.primary_menue.triggered.connect(self.act_on_action)

        self.sub_m = QMenu(self.primary_menue)
        self.sub_m.aboutToHide.connect(lambda: self.sub_prevent_closing(self.sub_m))

        self.sub_m.setTitle("Blocks")
        self.sub_m.addAction("Arm")
        self.sub_m.addAction("Leg")
        self.sub_m.addAction("Spine")
        self.sub_m.addAction("Root")

        self.sub_menue_nodes = QMenu(self.primary_menue)
        self.sub_menue_nodes.aboutToHide.connect(lambda: self.sub_prevent_closing(self.sub_menue_nodes))

        self.sub_menue_nodes.setTitle("Post Build Nodes")
        self.sub_menue_nodes.addAction("Auto weights")
        self.sub_menue_nodes.addAction("Constraints")

        self.sub_menue_all = QMenu(self.primary_menue)
        self.sub_menue_all.aboutToHide.connect(lambda: self.sub_prevent_closing(self.sub_menue_all))

        self.sub_menue_all.setTitle("All")
        for action_icon in self.icons:
            temp_action = QAction(action_icon[0], str(action_icon[1]), self.primary_menue)
            self.sub_menue_all.addAction(temp_action)

        self.primary_menue.addMenu(self.sub_m)
        self.primary_menue.addMenu(self.sub_menue_nodes)
        self.primary_menue.addSeparator()
        self.primary_menue.addMenu(self.sub_menue_all)
        self.primary_menue.updateGeometry()


        self.search_results_menu = QMenu()
        self.search_results_menu.setStyleSheet(self.menue_style_sheet)

        # self.layout.addWidget(self.label)
        self.layout.addWidget(self.search_menu, 0,0)
        self.layout.addWidget(self.primary_menue, 1, 0)
        self.layout.addWidget(self.search_results_menu,0,1, 0, 2)

        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(self.layout)
        self.setFixedSize(self.layout.sizeHint())
    @Slot(QAction)
    def act_on_action(self, action: QAction):
        print("Entry was clicked!", action.text())
        self.primary_menue.setVisible(True)

    def load_icons(self):
        self.icon_dir = QDir("./total_icons")
        self.icon_files = self.icon_dir.entryInfoList(["*.png"])

        icons = []
        file_info: QFileInfo
        for file_info in self.icon_files:
            file_path = file_info.absoluteFilePath()
            icons.append([QIcon(file_path), file_info.fileName().split(".")[0].capitalize() ])
        self.options = [item[1] for item in icons]
        print(self.options)
        return icons

    @Slot(str)
    def search_results(self, text):
        res = difflib.get_close_matches(text, self.options)
        if len(res)==0:
            self.search_results_menu.setVisible(False)
            return
        else:
            self.search_results_menu.setVisible(True)

        self.search_results_menu.clear()
        acts = [opt for opt in self.icons if opt[1] in res]

        for opt in acts:
            self.search_results_menu.addAction(opt[0], opt[1])

        self.updateGeometry()
        self.search_results_menu.updateGeometry()
        self.primary_menue.updateGeometry()

    def prevent_deletion(self, menu):
        menu.setAttribute(Qt.WA_DeleteOnClose, False)

    def sub_prevent_closing(self, menu):
        menu.setAttribute(Qt.WA_DontShowOnScreen, False)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pyside2 QGraphic View")
        self.setGeometry(300,200,640,520)

        scene = QGraphicsScene(self)
        scene.addText("Fiverr | paulkoch219", QFont("Sanserif", 15))
        self.view = QGraphicsView(scene, self)
        self.view.setGeometry(0, 0, 640, 440)

        self.rcm = RichContextMenu(self)
        self.rcm.setVisible(False)

        self.msgSc = QShortcut(QKeySequence('Tab'), self)
        self.msgSc.activated.connect(self.toggle_context_menu)
        vbox = QVBoxLayout()
        vbox.addWidget(self.view)
        vbox.addWidget(self.rcm)
        self.setLayout(vbox)
        self.show()

    def toggle_context_menu(self):
        mouse_position = self.mapFromGlobal(QCursor.pos())
        if self.rcm.isVisible() == False:
            self.rcm.setVisible(True)
            self.rcm.move(mouse_position)
            self.rcm.primary_menue.setVisible(True)
        else:
            self.rcm.setVisible(False)

app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())
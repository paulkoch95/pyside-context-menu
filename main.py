import os
# MacOS Specific Fix, not necessary on version < BigSur and other Posix
# os.environ['QT_MAC_WANTS_LAYER'] = '1'

from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QShortcut, QWidget, QVBoxLayout, QLineEdit, QMenu, QGridLayout, QAction, QLayout
from PySide2.QtGui import QFont, QKeySequence, QCursor, QIcon
from PySide2.QtCore import Qt, Slot, QDir, QFileInfo
import sys
import difflib

class RichContextMenu(QWidget):

    def __init__(self, parent=None):

        #################
        # Initial Setup #
        #################
        super(RichContextMenu, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.options = []
        self.block_icons = self.load_icons("./total_icons/blocks")
        self.node_icons = self.load_icons("./total_icons/nodes")
        self.all_icons = self.load_icons("./total_icons/all")
        self.layout = QGridLayout()
        self.layout.setSpacing(0)

        self.menue_style_sheet = """
                                QMenu {
                                    background: #555555;
                                }
                                QMenu:item:selected {
                                    background: darkGray;
                                }
                                QMenu:item {
                                    color: white;
                                    padding: 5px;
                                }
                                """
        ####################
        # Setup Search bar #
        ####################
        self.search_menu = QLineEdit()
        self.search_menu.setPlaceholderText("search...")
        self.search_menu.setStyleSheet("QLineEdit { border: 2px solid black; background-color: white;}")
        self.search_menu.textChanged[str].connect(self.search_results)

        ##################################
        # Populate Context Menue Entries #
        ##################################
        self.load_menue_structure()

        ########################################
        # Setup Extra Menue for Search results #
        ########################################
        self.search_results_menu = QMenu()
        self.search_results_menu.setStyleSheet(self.menue_style_sheet)
        self.search_results_menu.triggered.connect(self.act_on_action)
        ################
        # Layut Widget #
        ################
        self.layout.addWidget(self.search_menu, 0,0)
        self.layout.addWidget(self.primary_menue, 1, 0)
        self.layout.addWidget(self.search_results_menu,0,1, 0, 2)

        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(self.layout)
        self.setFixedSize(self.layout.sizeHint())

    def load_menue_structure(self) -> None:
        self.primary_menue = QMenu()
        self.primary_menue.setStyleSheet(self.menue_style_sheet)

        self.primary_menue.aboutToHide.connect(lambda: self.prevent_deletion(self.primary_menue))

        self.primary_menue.triggered.connect(self.act_on_action)

        self.sub_m = QMenu(self.primary_menue)
        self.sub_m.aboutToHide.connect(lambda: self.sub_prevent_closing(self.sub_m))

        self.sub_m.setTitle("Blocks")
        self.blocks_menue_items = self.block_icons
        self.sub_m.addActions([QAction(action_icon[0], str(action_icon[1]), self.primary_menue) for action_icon in self.blocks_menue_items])

        self.sub_menue_nodes = QMenu(self.primary_menue)
        self.sub_menue_nodes.aboutToHide.connect(lambda: self.sub_prevent_closing(self.sub_menue_nodes))

        self.sub_menue_nodes.setTitle("Post Build Nodes")
        self.sub_menue_nodes_items = self.node_icons
        self.sub_menue_nodes.addActions([QAction(action_icon[0], str(action_icon[1]), self.primary_menue) for action_icon in self.sub_menue_nodes_items])

        self.sub_menue_all = QMenu(self.primary_menue)
        self.sub_menue_all.aboutToHide.connect(lambda: self.sub_prevent_closing(self.sub_menue_all))

        self.sub_menue_all.setTitle("All")
        self.sub_menue_all.addActions([QAction(action_icon[0], str(action_icon[1]), self.primary_menue) for action_icon in self.all_icons])

        self.sub_menue_all.setContentsMargins(5, 0, 0, 0)

        self.primary_menue.addMenu(self.sub_m)
        self.primary_menue.addMenu(self.sub_menue_nodes)
        self.primary_menue.addSeparator()
        self.primary_menue.addMenu(self.sub_menue_all)
        self.primary_menue.setFixedWidth(150)

        self.sub_menue_nodes.setStyleSheet("""QMenu:item {margin-left: 8px;}""")
        self.sub_m.setStyleSheet("""QMenu:item {margin-left: 8px;}""")
        self.sub_menue_all.setStyleSheet("""QMenu:item {margin-left: 8px;}""")

    def showEvent(self, event):
        self.search_menu.setText("")
        super().showEvent(event)

    @Slot(QAction)
    def act_on_action(self, action: QAction) -> None:
        """ Here you can add logic for what to do when an entry was clicked. """
        self.setVisible(False)
        self.primary_menue.setVisible(True)

        print("Entry was clicked!", action.text())

    def load_icons(self, dir: str) -> list[list[QIcon, str]]:
        """ Load images and extract entry names from Image Names"""
        self.icon_dir = QDir(dir)
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
    def search_results(self, text: str) -> None:
        """ Search in loaded menue entry options using SequenceMatching """
        res = difflib.get_close_matches(text, self.options)
        if len(res)==0:
            self.search_results_menu.setVisible(False)
            return
        else:
            self.search_results_menu.setVisible(True)

        self.search_results_menu.clear()
        acts = self.filter_icon_list_by_name(self.icons, res)

        for opt in acts:
            self.search_results_menu.addAction(opt[0], opt[1])

        self.updateGeometry()
        self.search_results_menu.updateGeometry()
        self.primary_menue.updateGeometry()

    def prevent_deletion(self, menu: QMenu) -> None:
        """ Prevent Qmenu from closing """
        menu.setAttribute(Qt.WA_DeleteOnClose, False)

    def sub_prevent_closing(self, menu: QMenu) -> None:
        """ Prevent SubMenu Items from being closed in QMenu """
        menu.setAttribute(Qt.WA_DontShowOnScreen, False)

    def filter_icon_list_by_name(self, icon_list: list[list[QIcon, str]], filter: list[str]):
        """ Find QIcon in List of QIcons and Strings based on List of desired results """
        return [opt for opt in icon_list if opt[1] in filter]

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Example App, simpel QGraphicsScene and Viewer Setup
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
        """ Toggle Widget Visibility """
        # Note: This could be changed and moved inside of the Widget itsel, but since I dont know if the
        # widget maybe triggered by other actions I would suggest external triggering.
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
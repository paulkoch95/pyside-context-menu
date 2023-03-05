import os
# MacOS Specific Fix, not necessary on version < BigSur and other Posix
os.environ['QT_MAC_WANTS_LAYER'] = '1'

from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QShortcut, QWidget, QVBoxLayout, QLineEdit, QMenu, QGridLayout, QAction, QLayout, QCompleter
from PySide2.QtGui import QFont, QKeySequence, QCursor, QIcon
from PySide2.QtCore import Qt, Slot, QDir, QFileInfo, QEvent
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
        # self.all_icons = self.load_icons(["./total_icons"])
        self.loaded_icons = self.load_icons_dict("./total_icons")

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

        ##################################
        # Populate Context Menue Entries #
        ##################################
        menu = {"Blocks": ["arm", "leg", "spine", "root"], "Post Build Nodes": ["constraint", "autoWeights"], "Arbitrary Nodes": ["hand", "flateye", "brow"]}
        self.options = [item for sublist in menu.values() for item in sublist]
        print("All options: ", self.options)
        self.build_dynamic_menu(menu)

        ####################
        # Setup Search bar #
        ####################
        self.search_menu = QLineEdit()
        self.search_menu.setPlaceholderText("search...")
        self.search_menu.setStyleSheet("QLineEdit { border: 2px solid black; background-color: white;}")
        self.search_menu.textChanged[str].connect(self.search_results)
        self.search_menu.installEventFilter(self)

        self.text_completer = QCompleter([lit.capitalize() for lit in self.options], self)
        print("opt", self.options)
        self.text_completer.setCaseSensitivity(Qt.CaseInsensitive)
        # self.search_menu.setCompleter(self.text_completer)


        ########################################
        # Setup Extra Menue for Search results #
        ########################################
        self.search_results_menu = QMenu()
        self.search_results_menu.setStyleSheet(self.menue_style_sheet)
        self.search_results_menu.triggered.connect(self.act_action)

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

    def build_dynamic_menu(self, menu_struct: dict[str, list[str]]):
        print("loaded icons", self.loaded_icons)

        self.primary_menue = QMenu()
        self.primary_menue.setStyleSheet(self.menue_style_sheet)
        self.primary_menue.aboutToHide.connect(lambda: self.prevent_deletion(self.primary_menue))
        #

        all_actions = []

        for title, submenu in menu_struct.items():
            m_sub = QMenu(self.primary_menue)
            m_sub.setTitle(title)
            m_sub.triggered.connect(self.act_action)

            opt = []
            for entry in submenu:
                if entry != "*":
                    if entry in self.loaded_icons.keys():
                        temp_act = QAction(self.loaded_icons.get(entry).get("icon"), entry.capitalize(), self.primary_menue)
                        m_sub.addAction(temp_act)
                        all_actions.append(temp_act)

                    else:
                        temp_act = QAction(QIcon(), entry.capitalize(), self.primary_menue)
                        m_sub.addAction(temp_act)
                        all_actions.append(temp_act)

            m_sub.updateGeometry()
            m_sub.installEventFilter(self)
            self.primary_menue.addMenu(m_sub)

            m_sub.setStyleSheet("""QMenu:item {margin-left: 8px;}""")

        self.primary_menue.setFixedWidth(150)
        self.primary_menue.addSeparator()
        self.all_menu = QMenu(self.primary_menue)
        self.all_menu.setTitle("All")
        self.all_menu.addActions(all_actions)
        self.all_menu.setFixedWidth(150)
        self.all_menu.installEventFilter(self)
        self.primary_menue.addMenu(self.all_menu)

        self.installEventFilter(self)

        self.search_term = ""
    def showEvent(self, event):
        self.search_menu.setText("")
        super().showEvent(event)

    # @Slot(QAction)
    def act_action(self, action: QAction) -> None:
        """ Here you can add logic for what to do when an entry was clicked. """
        self.setVisible(False)
        self.primary_menue.setVisible(True)
        print("Entry was clicked!", action.text())

    def load_icons_dict(self, dir):
        icons = {}
        icon_dir = QDir(dir)
        icon_files = icon_dir.entryInfoList(["*.png"])

        file_info: QFileInfo
        for file_info in icon_files:
            file_path = file_info.absoluteFilePath()
            icons[file_info.fileName().split(".")[0].lower()] = {
                "icon" : QIcon(file_path)
            }
        # self.options = icons.keys()
        return icons

    def load_icons(self, dir: list[str]) -> list[list[QIcon, str]]:
        """ Load images and extract entry names from Image Names"""

        icons = []
        for directory in dir:
            icon_dir = QDir(directory)
            icon_files = icon_dir.entryInfoList(["*.png"])

            dir_icons = []
            file_info: QFileInfo
            for file_info in icon_files:
                file_path = file_info.absoluteFilePath()
                dir_icons.append([QIcon(file_path), file_info.fileName().split(".")[0].capitalize()])
            icons.extend(dir_icons)
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
        for result in res:
            if result in self.loaded_icons:
                self.search_results_menu.addAction(self.loaded_icons.get(result).get("icon"), result.capitalize())
            else:
                self.search_results_menu.addAction(QIcon(), result.capitalize())
        self.hide_all_expanded_subentries(self.primary_menue)
        # print("Actions: ", self.search_results_menu.actions())
        try:
            self.search_results_menu.setFocus()
            self.search_results_menu.setActiveAction(self.search_results_menu.actions()[0])
            self.search_results_menu.popup()
        except Exception as e:
            pass

        self.updateGeometry()
        self.search_results_menu.updateGeometry()
        self.primary_menue.updateGeometry()
        self.search_results_menu.setFocus()

    def prevent_deletion(self, menu: QMenu) -> None:
        """ Prevent Qmenu from closing """
        menu.setAttribute(Qt.WA_DeleteOnClose, False)

    def sub_prevent_closing(self, menu: QMenu) -> None:
        """ Prevent SubMenu Items from being closed in QMenu """
        menu.setAttribute(Qt.WA_DontShowOnScreen, False)

    def filter_icon_list_by_name(self, icon_list: list[list[QIcon, str]], filter: list[str]):
        """ Find QIcon in List of QIcons and Strings based on List of desired results """
        return [opt for opt in icon_list if opt[1].lower() in filter]

    def hide_all_expanded_subentries(self, menu: QMenu) -> None:
        """ Helper function to hide all expanded submenus in a QMenu instance.
        Used by the autocomplete function to collapse exapnded submenus """
        for entry in menu.actions():
            try:
                entry.menu().hide()
            except AttributeError as e:
                pass

    def eventFilter(self, obj, event):
        """ Event filter responsible for the navigation of the Qmenu """
        if event.type() == QEvent.KeyRelease:
            # check if any key has been pressed
            if event.key() != Qt.Key_Left and event.key() != Qt.Key_Right and event.key() != Qt.Key_Up and event.key() \
                    != Qt.Key_Down:
                # there is not text in the search bar? lets add it!
                if len(self.search_menu.text()) >= 0 and event.key() != Qt.Key_Tab:
                    self.search_menu.setText(self.search_menu.text() + event.text())
                # convenient delete function of the search entry. als eliminates strange behaviour
                # with non alpha characters.
                if len(self.search_menu.text()) > 0 and event.key() == Qt.Key_Backspace:
                    self.search_menu.setText("")
                return True
            elif len(self.search_menu.text()) > 0 and len(self.search_results_menu.actions()) > 0 and \
                    event.key() == Qt.Key_Right:
                # focus search results menu when there are results
                self.search_results_menu.setFocus()
                return True
            elif len(self.search_menu.text()) > 0 and len(self.search_results_menu.actions()) and \
                    event.key() == Qt.Key_Left:
                # navigate back to the primary menue when left key was pressed.
                self.search_results_menu.setVisible(False)
                self.primary_menue.setFocus()
                return True
            elif len(self.search_menu.text()) == 0:
                self.primary_menue.setFocus()

        return super().eventFilter(obj, event)


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

            self.rcm.primary_menue.setFocus()
            # self.active_action = self.rcm.primary_menue.actions()[0]
            # self.rcm.primary_menue.setActiveAction(self.active_action)

            # self.active_action.menu().setVisible(False)
            # print("Type: ", type(self.active_action))
            # self.active_action.hide()

        else:
            self.rcm.setVisible(False)

app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())
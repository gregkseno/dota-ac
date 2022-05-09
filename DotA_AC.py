# -*- coding: utf-8 -*-
# TODO: Edit heroes window design
# TODO: Edit names of heroes
import os
import sys
import time
# TODO: Change
import keyboard
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QKeyEvent, QIcon
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QStyle, QAction, QMenu, qApp, QListWidget, QListView, \
    QListWidgetItem, QVBoxLayout
from PyQt5.QtCore import QThread, QEvent, QSize
from pynput.keyboard import Key, Listener

import game_info
import gsi_server
from game_info import GameStates, GameHeroes


class KeyMonitor(QtCore.QObject):

    def __init__(self, parent=None):
        super(KeyMonitor, self).__init__(parent)
        self.listener = Listener(on_release=self.on_release)

    def on_release(self, key):
        if key == Key.f10:
            event = QKeyEvent(QEvent.KeyPress, QtCore.Qt.Key_F10, QtCore.Qt.NoModifier, 0, 0, 0)
            self.parent().key_event(event)

    def stop_monitoring(self):
        self.listener.stop()

    def start_monitoring(self):
        self.listener.start()


class AutomationThread(QThread):
    # _vx_default = 0.3
    # _vy_default = 0.3347
    # _vw_default = 0.4
    # _vh_default = 0.2361
    # _aspect_default = 16 / 9
    # _threshold = 0.8
    def __init__(self, game, hero_names):
        super().__init__()
        self.game = game
        self.hero_names = hero_names

    def run(self):
        while self.auto_clicking():
            if self.isInterruptionRequested():
                return
            print("waiting")

        if self.hero_names:  # if heroes are selected
            # waiting DOTA_GAMERULES_STATE_HERO_SELECTION
            while self.game.map.game_state != GameStates.DOTA_GAMERULES_STATE_HERO_SELECTION.name:
                if self.isInterruptionRequested():
                    return
                print("waiting hero selection phase")
                # if game abandoned map setts None
                if self.game.isEmpty():
                    print("game abandoned")
                    return
            self.hero_select(self.hero_names)

    # def feature_matching(self, orb, bf, img, btn_tmp, btn_kp, btn_des):
    #     # Objects for feature detection and homography of screenshot
    #     img_kp, img_des = orb.detectAndCompute(img, None)
    #     matches = bf.match(btn_des, img_des)
    #     if matches:
    #         matches = sorted(matches, key=lambda x: x.distance)
    #         if len(matches) > 10:
    #             src_pts = np.float32([btn_kp[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    #             dst_pts = np.float32([img_kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    #             _, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    #             mask = mask.ravel().tolist()
    #             unique, counts = np.unique(np.array(mask), return_counts=True)
    #             count = dict(zip(unique, counts))
    #             print(count[1]/len(mask))
    #             if count[1]/len(mask) >= self._threshold:
    #                 return True
    #     return False

    # def get_region(self, resolution):
    #     aspect = resolution[0]/resolution[1]
    #     x = int(resolution[0] * aspect / self._aspect_default * self._vx_default)
    #     y = int(resolution[1] * aspect / self._aspect_default * self._vy_default)
    #     w = int(resolution[0] * aspect / self._aspect_default * self._vw_default)
    #     h = int(resolution[1] * aspect / self._aspect_default * self._vh_default)
    #     return x, y, w, h

    def auto_clicking(self):
        # resolution = pyautogui.size()
        # region = self.get_region(resolution)
        # btn_tmp = cv2.imread('accept_button.png', cv2.IMREAD_GRAYSCALE)
        #
        # # Objects for feature detection and homography of template image
        # orb = cv2.ORB_create()
        # btn_kp, btn_des = orb.detectAndCompute(btn_tmp, None)
        # bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        # screenshot = pyautogui.screenshot(region=region)
        # img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
        #
        # accept = self.feature_matching(orb, bf, img, btn_tmp, btn_kp, btn_des)
        keyboard.send("enter")
        if self.game.map.game_state in (GameStates.DOTA_GAMERULES_STATE_WAIT_FOR_PLAYERS_TO_LOAD.name,
                                        GameStates.DOTA_GAMERULES_STATE_HERO_SELECTION.name):
            print("accepted")
            return False
        time.sleep(2)
        return True

    def hero_select(self, hero_names):
        for hero_name in hero_names:
            hero = list(filter(lambda x: hero_name == x.name_loc, GameHeroes))[0]
            if self.isInterruptionRequested():
                return
            keyboard.send("\\")
            keyboard.write("dota_select_hero npc_dota_hero_" + hero.name, delay=0.01)
            time.sleep(0.2)
            keyboard.send("enter")
            keyboard.send("\\")

            # TODO: select new hero if previous was banned
            if True:  # self.is_selected():
                break


class MainWindow(QMainWindow):
    selected_heroes = []

    def __init__(self, server):
        QMainWindow.__init__(self)
        self.hero_window = HeroWindow(self)

        """ Setting up event listener on F10 button """
        self.monitor = KeyMonitor(self)
        self.monitor.start_monitoring()
        self.server = server

        self.setupUi()

        self.AutomationThread_instance = AutomationThread(self.server.game, self.selected_heroes)
        self.stopping_thread = QtCore.QProcess()
        self.AutomationThread_instance.finished.connect(self.show_start)

    def key_event(self, e):
        if e.key() == QtCore.Qt.Key_F10:
            if self.AutomationThread_instance.isRunning():
                self.show_start()
                self.stop_autoclick()
            else:
                self.show_stop()
                self.start_autoclick()

    def setupUi(self):
        # TODO: Make a new design
        # Setting up window
        self.setObjectName("MainWindow")
        self.setWindowTitle("DotA Autoclick")
        self.setMinimumSize(QtCore.QSize(220, 210))
        self.setMaximumSize(QtCore.QSize(220, 210))

        # Setting up center widget
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # Setting up start button
        self.selectHeroButton = QtWidgets.QPushButton(self.centralwidget)
        self.selectHeroButton.setGeometry(QtCore.QRect(55, 50, 110, 40))
        self.selectHeroButton.setObjectName("selectHeroButton")
        self.selectHeroButton.setText("Select heroes")
        self.selectHeroButton.clicked.connect(self.hero_window.show)

        # Setting up start button
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(55, 120, 110, 40))
        self.startButton.setObjectName("startButton")
        self.startButton.setText("START")
        self.startButton.clicked.connect(self.start_autoclick)
        self.startButton.clicked.connect(self.show_stop)

        # Setting up stop button
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setGeometry(QtCore.QRect(55, 120, 110, 40))
        self.stopButton.setObjectName("stopButton")
        self.stopButton.setText("STOP")
        self.stopButton.hide()
        self.stopButton.clicked.connect(self.stop_autoclick)
        self.stopButton.clicked.connect(self.show_start)

        # Setting up menu
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 220, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        # TODO: Make a new changeable icon changes
        # Setting up tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.activated.connect(self.tray_icon_doubleclick)

        # Setting up tray icon actions
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(qApp.quit)

        # Setting up tray icon menu
        tray_menu = QMenu()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def start_autoclick(self):
        self.AutomationThread_instance.start()
        print("Started")
        if self.isHidden():
            self.tray_icon.showMessage(
                "DotA Autoclick",
                "Autoclick started",
                QSystemTrayIcon.Information,
                200
            )

    def stop_autoclick(self):
        self.AutomationThread_instance.requestInterruption()
        print("Stopped")
        if self.isHidden():
            self.tray_icon.showMessage(
                "DotA Autoclick",
                "Autoclick stopped",
                QSystemTrayIcon.Information,
                200
            )

    def tray_icon_doubleclick(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isHidden():
                self.show()
            elif self.isMinimized():
                self.showNormal()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "DotA Autoclick",
            "Application was hidden to tray",
            QSystemTrayIcon.Information,
            2000
        )

    def show_start(self):
        self.startButton.show()
        self.stopButton.hide()

    def show_stop(self):
        self.stopButton.show()
        self.startButton.hide()


class HeroWindow(QMainWindow):
    def __init__(self, parent):
        QMainWindow.__init__(self)
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        self.setStyleSheet('''
            QWidget {
                background-image: url(images/background.png);
                background-repeat: no-repeat; 
                background-position: center;
            }
            QListWidget {
                margin: 5px;
                background: transparent;
                color: rgb(211,211,211);
            }
            QListWidget::item {
                border-radius: 1px;
            }
            QListWidget::item:selected {
                box-shadow: 10px 5px 5px black;
                background: rgb(150,160,180);
                color: rgb(60,60,60);
            }
            QListWidget::item:hover {
                box-shadow: 10px 5px 5px black;
                background: rgb(150,160,180);
                color: rgb(60,60,60);
            }
        ''')
        # Setting up center widget
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        # Setting up window
        self.setObjectName("HeroWindow")
        self.setWindowTitle("DotA Heroes")
        self.setMinimumSize(QtCore.QSize(1066, 537))
        self.setMaximumSize(QtCore.QSize(1066, 537))
        self.setMinimumSize(self.size())

        self.strength = QListWidget()
        self.strength.setObjectName("strength")
        self.agility = QListWidget()
        self.agility.setObjectName("agility")
        self.intelligence = QListWidget()
        self.intelligence.setObjectName("intelligence")
        self.heroes_lists = [self.strength, self.agility, self.intelligence]

        self.heroes = QVBoxLayout(self)
        self.centralwidget.setLayout(self.heroes)
        for hero_list in self.heroes_lists:
            hero_list.setViewMode(QListView.IconMode)
            hero_list.setFrameShape(QListView.NoFrame)
            hero_list.setIconSize(QSize(64, 36))
            hero_list.setMovement(False)
            hero_list.setResizeMode(QListView.Adjust)
            hero_list.setSelectionMode(QListView.MultiSelection)
            hero_list.itemSelectionChanged.connect(self.selectionChanged)
            self.heroes.addWidget(hero_list)
        self.addheroes()

    def addheroes(self):
        # Read thumbnail
        for hero_list in self.heroes_lists:
            files = os.listdir("heroes/" + hero_list.objectName())
            for file in files:
                hero_name_loc = game_info.find_hero_by_name(file.split('.')[0]).name_loc
                item = QListWidgetItem(QIcon("heroes/" + hero_list.objectName() + '/' + file), hero_name_loc)
                item.setSizeHint(QSize(68, 53))
                hero_list.addItem(item)

    def selectionChanged(self):
        self.parent.selected_heroes.clear()
        for hero_list in self.heroes_lists:
            self.parent.selected_heroes += [hero.text() for hero in hero_list.selectedItems()]
        # TODO: Make number in order of selected heroes
        # for i ,hero in enumerate(self.parent.selected_heroes):
        #     for hero_list in self.heroes_lists:
        #         for hero_item in hero_list:
        #             if
        print(self.parent.selected_heroes)


def main():
    try:
        server = gsi_server.GSIServer(server_address=("localhost", 59228))
        server.start_server()
    except Exception as e:
        print(e)
        return
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(server)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

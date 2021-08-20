# -*- coding: utf-8 -*-
# TODO: Begin new or end stop
import time
import cv2
# TODO: Change
import imutils
import pyautogui
from PIL import ImageGrab
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QStyle, QAction, QMenu, qApp
from PyQt5.QtCore import QThread, QEvent
import pygame
from pynput.keyboard import Key, Listener


class KeyMonitor(QtCore.QObject):
    # keyPressed = QtCore.pyqtSignal(QKeyEvent)

    def __init__(self, parent=None):
        super(KeyMonitor, self).__init__(parent)
        self.listener = Listener(on_release=self.on_release)

    def on_release(self, key):
        if key == Key.f10:
            event = QKeyEvent(QEvent.KeyPress, QtCore.Qt.Key_F10, QtCore.Qt.NoModifier, 0, 0, 0)
            # self.keyPressed.emit(event)
            self.parent().key_event(event)

    def stop_monitoring(self):
        self.listener.stop()

    def start_monitoring(self):
        self.listener.start()


class AutoClickerThread(QThread):
    _working = False

    def __init__(self, mainwindow, parent=None):
        super().__init__()
        self.mainwindow = mainwindow

    def run(self):
        self._working = True
        resolution = self.mainwindow.comboBox.currentText()
        screen_height = int(resolution.split("x")[0])
        screen_width = int(resolution.split("x")[1])
        btn_tmp = cv2.imread(resolution + '.jpg')
        btn_tmp = cv2.cvtColor(btn_tmp, cv2.COLOR_BGR2GRAY)
        btn_tmp = cv2.Canny(btn_tmp, 50, 200)
        if resolution == "1360x768":
            btn_tmp = imutils.resize(btn_tmp, width=int(btn_tmp.shape[1] * 1360/1920))
        w, h = btn_tmp.shape[::-1]

        while self._working:
            screenshot = ImageGrab.grab(bbox=(0, 0, screen_height, screen_width))
            screenshot.save('accept_screen.jpg')
            print("Trying to find button...")
            img = cv2.imread('old/accept_screen.jpg')
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.Canny(img, 50, 200)
            res = cv2.matchTemplate(img, btn_tmp, cv2.TM_CCOEFF_NORMED)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(res)
            print(maxVal)
            if maxVal >= 0.8:
                (startX, startY) = (int(maxLoc[0]), int(maxLoc[1]))
                (endX, endY) = (int(maxLoc[0] + w), int(maxLoc[1] + h))
                (x, y) = ((startX + endX) / 2, (startY + endY) / 2)

                pyautogui.moveTo(x, y)
                pyautogui.mouseDown()
                time.sleep(0.1)
                pyautogui.mouseUp()
                print("Accepted")
                self.stop()
            time.sleep(2)

            """for tmp_scale in np.linspace(0.2, 1.0, 100)[::-1]:
                resized = imutils.resize(btn_tmp, width=int(btn_tmp.shape[1] * tmp_scale))
                r = btn_tmp.shape[1] / float(resized.shape[1])
                if resized.shape[0] < h or resized.shape[1] < w:
                    break

                res = cv2.matchTemplate(img, resized, cv2.TM_CCOEFF_NORMED)
                (_, maxVal, _, maxLoc) = cv2.minMaxLoc(res)
                clone = np.dstack([resized, resized, resized])
                cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                              (maxLoc[0] + w, maxLoc[1] + h), (0, 0, 255), 2)
                cv2.imshow("22", clone)
                cv2.waitKey(0)
                if maxVal >= 0.8:
                    scale = tmp_scale
                    found = (maxVal, maxLoc, r)
                    break

                if found is None or maxVal > found[0]:
                    scale = tmp_scale
                    found = (maxVal, maxLoc, r)
            if found[0] >= 0.8:
                (_, maxLoc, r) = found
                (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
                (endX, endY) = (int((maxLoc[0] + w) * r), int((maxLoc[1] + h) * r))
                (x, y) = ((startX + endX) / 2, (startY + endY) / 2)

                pyautogui.moveTo(x, y)
                pyautogui.mouseDown()
                time.sleep(0.1)
                pyautogui.mouseUp()
                print("Accepted")
            time.sleep(2)"""

    def stop(self):
        self._working = False

    def is_working(self):
        return self._working


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi()
        self.monitor = KeyMonitor(self)
        self.monitor.start_monitoring()
        self.AutoClickThread_instance = AutoClickerThread(mainwindow=self)

    def key_event(self, e):
        if e.key() == QtCore.Qt.Key_F10:
            if self.AutoClickThread_instance.is_working():
                self.stop_autoclick()
            else:
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
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(55, 120, 110, 40))
        self.startButton.setObjectName("startButton")
        self.startButton.setText("START")
        self.startButton.clicked.connect(self.start_autoclick)

        # Setting up stop button
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setGeometry(QtCore.QRect(55, 120, 110, 40))
        self.stopButton.setObjectName("stopButton")
        self.stopButton.setText("STOP")
        self.stopButton.hide()
        self.stopButton.clicked.connect(self.stop_autoclick)

        # Setting up comboBox with screen resolutions
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(54, 50, 112, 20))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItems(resolutions)

        # Setting up menu
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 220, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        # TODO: Make a new changeable icon changes by isWorking status
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
        self.comboBox.setEnabled(False)
        self.startButton.hide()
        self.stopButton.show()
        self.AutoClickThread_instance.start()
        print("Started")
        if self.isHidden():
            self.tray_icon.showMessage(
                "DotA Autoclick",
                "Autoclick started",
                QSystemTrayIcon.Information,
                200
            )

    def stop_autoclick(self):
        self.startButton.show()
        self.stopButton.hide()
        self.comboBox.setEnabled(True)
        self.AutoClickThread_instance.stop()
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


def normalize_resolutions(resols):
    ress = []
    for res in resols:
        temp = str(res[0]) + "x" + str(res[1])
        if temp not in ress:
            ress.append(temp)
    return ress


if __name__ == "__main__":
    import sys
    pygame.init()
    resolutions = pygame.display.list_modes()
    resolutions = normalize_resolutions(resolutions)
    pygame.quit()

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




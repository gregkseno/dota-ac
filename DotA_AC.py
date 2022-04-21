# -*- coding: utf-8 -*-
# TODO: Begin new or end stop
import time
import cv2
# TODO: Change
import numpy as np
import pyautogui
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QStyle, QAction, QMenu, qApp
from PyQt5.QtCore import QThread, QEvent
from pynput.keyboard import Key, Listener
from playsound import playsound


# import matplotlib.pyplot as plt


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


class AutoClickerThread(QThread):
    _working = False
    _vx_default = 0.3
    _vy_default = 0.3347
    _vw_default = 0.4
    _vh_default = 0.2361
    _aspect_default = 16 / 9
    _threshold = 0.8

    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow

    def run(self):
        self._working = True
        resolution = pyautogui.size()
        region = self.get_region(resolution)
        btn_tmp = cv2.imread('accept_button.jpg', cv2.IMREAD_GRAYSCALE)

        # Objects for feature detection and homography of template image
        orb = cv2.ORB_create()
        btn_kp, btn_des = orb.detectAndCompute(btn_tmp, None)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        while self._working:
            screenshot = pyautogui.screenshot(region=region)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

            accept = self.feature_matching(orb, bf, img, btn_tmp, btn_kp, btn_des)
            if accept:
                pyautogui.press("enter")
                print("accepted")
                playsound('ne_nado.mp3')
                if self.is_accepted():
                    break
            time.sleep(2)
        self.heroe_select(self.mainwindow.get_heroes())

    def hero_select(self, heroes):
        for hero in heroes:
            pyautogui.write(hero, interval=0.25)
            if self.is_selected():
                break

    def feature_matching(self, orb, bf, img, btn_tmp, btn_kp, btn_des):
        # Objects for feature detection and homography of screenshot
        img_kp, img_des = orb.detectAndCompute(img, None)
        matches = bf.match(btn_des, img_des)
        if matches:
            matches = sorted(matches, key=lambda x: x.distance)
            if len(matches) > 10:
                src_pts = np.float32([btn_kp[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([img_kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                _, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                mask = mask.ravel().tolist()
                unique, counts = np.unique(np.array(mask), return_counts=True)
                count = dict(zip(unique, counts))
                print(count[1]/len(mask))
                if count[1]/len(mask) >= self._threshold:
                    return True
        return False

    def get_region(self, resolution):
        aspect = resolution[0]/resolution[1]
        x = int(resolution[0] * aspect / self._aspect_default * self._vx_default)
        y = int(resolution[1] * aspect / self._aspect_default * self._vy_default)
        w = int(resolution[0] * aspect / self._aspect_default * self._vw_default)
        h = int(resolution[1] * aspect / self._aspect_default * self._vh_default)
        return x, y, w, h

    def is_accepted(self):
        return True

    def is_selected(self):
        return True

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

    def get_heroes(self):
        pass

    def start_autoclick(self):
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


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

import cv2
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QMainWindow, QLabel, QSlider, QGroupBox, QVBoxLayout, QLineEdit
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.uic.properties import QtCore


class ImageWindow(QMainWindow):

    def __init__(self, main_loop):
        super().__init__()
        self.main_loop = main_loop
        self.central_widget = QWidget(self)
        self.setWindowTitle("Color extraction")

        self.main_loop.window = self

        self.ver_layout = QVBoxLayout()
        self.layout = QGridLayout()

        self.h_text = QLabel("0")
        self.s_text = QLabel("0")
        self.v_text = QLabel("0")

        self.layout.addWidget(self.h_text, 0, 0)
        self.layout.addWidget(self.s_text, 0, 1)
        self.layout.addWidget(self.v_text, 0, 2)

        self.start_button = QPushButton("Add mask")
        self.start_button.clicked.connect(self.addMask)
        self.layout.addWidget(self.start_button, 3, 0)

        self.update_button = QPushButton("Show current mask")
        self.update_button.clicked.connect(self.show_current)
        self.layout.addWidget(self.update_button, 2, 1)

        self.print_masks_button = QPushButton("Print masks")
        self.print_masks_button.clicked.connect(self.print_masks)
        self.layout.addWidget(self.print_masks_button, 2, 2)

        self.stop_button = QPushButton("Next Frame")
        self.stop_button.clicked.connect(self.next_frame)
        self.layout.addWidget(self.stop_button, 1, 0)

        self.prev_button = QPushButton("Prev Frame")
        self.prev_button.clicked.connect(self.prev_frame)
        self.layout.addWidget(self.prev_button, 1, 1)

        self.save_images_button = QPushButton("Save mask")
        self.save_images_button.clicked.connect(self.save_mask)
        self.layout.addWidget(self.save_images_button, 2, 0)

        self.maskID = QLineEdit()
        self.layout.addWidget(self.maskID, 3, 1)

        self.delete_button = QPushButton("Delete mask")
        self.delete_button.clicked.connect(self.delete_mask)
        self.layout.addWidget(self.delete_button, 3, 2)

        self.values = QLabel("Min: (0,0,0) Max: (255,255,255)")

        self.masksInfo = QLabel("Masks:")
        self.masksLabel = QLabel()

        self.ver_layout.addWidget(self.values)

        self.ver_layout.addWidget(self.masksInfo)
        self.ver_layout.addWidget(self.masksLabel)


        self.sliders = []
        for i in range(6):
            s = QSlider(Qt.Horizontal)
            s.setMinimum(0)
            s.setMaximum(255)
            if i < 3:
                s.setValue(0)
            else:
                s.setValue(255)
            s.setTickPosition(QSlider.TicksBelow)
            s.setTickInterval(1)

            self.sliders.append(s)

        self.sliderInfoMin = QLabel("Min:")
        self.ver_layout.addWidget(self.sliderInfoMin)
        for ind, sli in enumerate(self.sliders):
            if ind == 3:
                self.sliderInfoMax = QLabel("Max:")
                self.ver_layout.addWidget(self.sliderInfoMax)
            self.ver_layout.addWidget(sli)
            sli.valueChanged.connect(self.valuechange)

        self.ver_layout.addLayout(self.layout)

        self.central_widget.setLayout(self.ver_layout)
        self.setCentralWidget(self.central_widget)




    def valuechange(self):
        h_min = self.sliders[0].value()
        s_min = self.sliders[1].value()
        v_min = self.sliders[2].value()
        h_max = self.sliders[3].value()
        s_max = self.sliders[4].value()
        v_max = self.sliders[5].value()
        self.main_loop.min_hsv = (h_min, s_min, v_min)
        self.main_loop.max_hsv = (h_max, s_max, v_max)
        self.values.setText("Min: " + str((h_min, s_min, v_min)) + " Max: " + str((h_max, s_max, v_max)))

    def start(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.show_values())
        self.timer.start(20)

    def show_values(self):
        self.h_text.setText(str(self.main_loop.h))
        self.s_text.setText(str(self.main_loop.s))
        self.v_text.setText(str(self.main_loop.v))
        text = ""
        for mask in self.main_loop.masks:
            text += str(mask[0]) + "   " + str(mask[1]) + "\n"
        self.masksLabel.setText(text)

    @pyqtSlot()
    def print_masks(self):
        for mask in self.main_loop.masks:
            print(mask)

    @pyqtSlot()
    def delete_mask(self):
        text = self.maskID.text()

        if text != "" and text.isnumeric():
            self.main_loop.masks.pop(int(text))

            self.show_values()


    @pyqtSlot()
    def save_mask(self):
        self.main_loop.save_mask()


    @pyqtSlot()
    def prev_frame(self):
        self.main_loop.id -= 1

    @pyqtSlot()
    def next_frame(self):
        self.main_loop.id += 1

    @pyqtSlot()
    def addMask(self):
        h_min = self.sliders[0].value()
        s_min = self.sliders[1].value()
        v_min = self.sliders[2].value()
        h_max = self.sliders[3].value()
        s_max = self.sliders[4].value()
        v_max = self.sliders[5].value()

        m = [(h_min, s_min, v_min), (h_max, s_max, v_max)]
        self.main_loop.masks.append(m)

    @pyqtSlot()
    def show_current(self):
        self.main_loop.show_current = not self.main_loop.show_current

    def flush(self):
        pass

    def closeEvent(self, event):
        print("Image window closed!")
        self.main_loop.close()

    def keyPressEvent(self, event):

        if event.key() == 78:
            self.main_loop.id += 1

        if event.key() == 66:
            self.main_loop.id -= 1


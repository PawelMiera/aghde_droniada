import sys
from PyQt5.QtWidgets import QApplication

from tests.ImageWindow.ImageWindow import ImageWindow

from tests.MainLoop.MainLoop import MainLoop


if __name__ == '__main__':

    main_loop = MainLoop()
    main_loop.start()

    app = QApplication(sys.argv)
    imageWindow = ImageWindow(main_loop)
    imageWindow.show()
    imageWindow.start()
    sys.exit(app.exec_())
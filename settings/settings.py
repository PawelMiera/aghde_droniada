

class Values:

    MODE = 1  # 0 - pc test, 1 - c# python save, 2 - c# python mission

    PRINT_FPS = True
    SAVED_IMAGES_DIRECTORY = 'D:/mission_images'

    WRITE_TO_FILE = True

    WEATHER_MODE = 0            # 0 - pochmurno,

    MAX_AREA_DIFF = 0.2
    MAX_LONG_LAT_DIFF = 0.00004
    MIN_AREA = 300
    MIN_ALTITUDE = 4

    BOX_COLOR = (0, 0, 255)
    BOX_SIZE_INCREASE = 10

    CAMERA = 1

    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    CAMERA_WIDTH_HALF = CAMERA_WIDTH / 2
    CAMERA_HEIGHT_HALF = CAMERA_HEIGHT / 2

    MAX_PIXEL_AREA = CAMERA_WIDTH * CAMERA_HEIGHT

    TRIANGLE = 0
    SQUARE = 1
    CIRCLE = 2

    WHITE = 0
    ORANGE = 1
    BROWN = 2

    COLORS = [(188, 213, 213), (77, 152, 189), (91, 124, 149)]      #BGR

    HORIZONTAL_ANGLE = 60

    VERTICAL_ANGLE = 36

    IMAGES_PATH = "saved_detections_images"



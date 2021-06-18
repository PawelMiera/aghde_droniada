

class Values:

    MODE = 0 # 0 - pc test, 1 - c# python save, 2 - c# python mission

    PRINT_FPS = True
    SAVED_IMAGES_DIRECTORY = 'D:/mission_images'    #8000iso400

    WRITE_TO_FILE = True

    SHOW_MASKS = True

    SHOW_BROWN_MASK = False
    SHOW_ORANGE_MASK = False
    SHOW_WHITE_MASK = False

    TELEMETRY_UPDATE_TIME = 1

    MAX_AREA_DIFF = 0.5
    MAX_LONG_LAT_DIFF = 0.00007
    MIN_AREA = 220
    MAX_AREA = 12200
    MIN_ALTITUDE = 15

    MIN_NOT_WHITE = 8

    BOX_COLOR = (0, 0, 255)
    BOX_SIZE_INCREASE = 10

    CAMERA = 0

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

    EXECUTING = 7

    COLORS = [(188, 213, 213), (77, 152, 189), (91, 124, 149)]      #BGR

    HORIZONTAL_ANGLE = 60

    VERTICAL_ANGLE = 36

    IMAGES_PATH = "saved_detections_images"

    QUEUED = 0
    ELIMINATED = 1
    NOT_ELIMINATED = 2
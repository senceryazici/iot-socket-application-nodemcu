import logging
import time

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the foreground with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def formatter_message(message, use_color=True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class ColoredFormatter(logging.Formatter):

    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


class IotServerLogger(logging.Logger):
    FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
    COLOR_FORMAT = formatter_message(FORMAT, True)
    STANDARD_FORMAT = "[%(asctime)s][%(levelname)-18s] %(message)s"

    def __init__(self, name, log_path):
        logging.Logger.__init__(self, name, logging.DEBUG)

        color_formatter = ColoredFormatter(self.COLOR_FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        time_string = time.strftime("iot-host-%d-%m-%Y-%H:%M:%S", time.localtime())
        t = time.time()
        millisecond = (t - int(t)) * 1000
        time_string += ":" + str(millisecond)
        import os
        a = os.path.abspath(log_path)
        print(a)
        if not os.path.exists(log_path + "/log"):
            os.system("mkdir -p " + log_path + "/log")
        fh = logging.FileHandler(log_path + "/log/" + time_string + '.log')
        file_formatter = logging.Formatter(self.STANDARD_FORMAT)
        fh.setFormatter(file_formatter)
        fh.setLevel(logging.DEBUG)

        self.addHandler(fh)
        self.addHandler(console)
        return


class IotClientLogger(logging.Logger):
    FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
    COLOR_FORMAT = formatter_message(FORMAT, True)
    STANDARD_FORMAT = "[%(asctime)s][%(levelname)-18s] %(message)s"

    def __init__(self, name, log_path):
        logging.Logger.__init__(self, name, logging.DEBUG)

        color_formatter = ColoredFormatter(self.COLOR_FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        time_string = time.strftime(name + "-%d-%m-%Y-%H:%M:%S", time.localtime())
        t = time.time()
        millisecond = (t - int(t)) * 1000
        time_string += ":" + str(millisecond)
        import os
        if not os.path.exists(log_path + "/log"):
            os.system("mkdir -p " + log_path + "/log")
        fh = logging.FileHandler(log_path + "/log/" + time_string + '.log')
        file_formatter = logging.Formatter(self.STANDARD_FORMAT)
        fh.setFormatter(file_formatter)
        fh.setLevel(logging.DEBUG)

        self.addHandler(fh)
        self.addHandler(console)
        return

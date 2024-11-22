class cc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class status_str:
    CHECK_STR = " " + cc.WARNING + "CHCK" + cc.ENDC + " "
    OK_STR = "  " + cc.OKGREEN + "OK" + cc.ENDC + "  "
    DEAD_STR = " " + cc.FAIL + "DEAD" + cc.ENDC + " "
    MISM_STR = " " + cc.WARNING + "MISM" + cc.ENDC + " "
    WARN_STR = " " + cc.WARNING + "WARN" + cc.ENDC + " "


def read_binary(uri):
    in_file = open(uri, "rb")  # opening for [r]eading as [b]inary
    data = in_file.read()  # if you only wanted to read 512 bytes, do .read(512)
    in_file.close()

    return data

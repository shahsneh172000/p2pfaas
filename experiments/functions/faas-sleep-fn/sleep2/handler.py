import time


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    out = ""

    for i in range(10):
        time.sleep(1)
        out += "Count... " + str(i) + "\n"

    out += "\n\n" + str(req)
    return out

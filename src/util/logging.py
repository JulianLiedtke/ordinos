import logging

log = logging.getLogger(__name__)

setup = False


def setup_logging(level=None):
    global setup
    if not setup:
        root = logging.getLogger()
        if level is None:
            root.setLevel(logging.INFO)
        else:
            root.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        root.addHandler(stream_handler)

        setup = True

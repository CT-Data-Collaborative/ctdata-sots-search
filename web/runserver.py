import logging
from logging import StreamHandler

from sots import app
if __name__ == "__main__":
    handler = StreamHandler()
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)
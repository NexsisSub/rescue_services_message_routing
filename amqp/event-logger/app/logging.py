import logging
from logstash_async.handler import AsynchronousLogstashHandler


host = 'localhost'
port = 5000


test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.DEBUG)
async_handler = AsynchronousLogstashHandler(host, port, database_path=None)
test_logger.addHandler(async_handler)
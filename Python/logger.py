import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
# Create a formatter for the log messages
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Set the formatter for the console handler
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# logging.basicConfig(level=logging.INFO,
# format='%(asctime)-15s %(levelname)8s %(name)s %(message)s')

# for name in ('blender_id', 'blender_cloud'):
#    logging.getLogger(name).setLevel(logging.DEBUG)


def register():
    pass

import logging
import logging.config
import datetime
import sys # Para salida a consola

now = datetime.datetime.now()
now_formatted = now.strftime("%Y%m%d_%H%M%S")

def setup_logging():
    """Configura el logging para la aplicación."""

    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')

    LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d (%(funcName)s) - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout,
        },
        'file_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'filename': f'logs/log_{now_formatted}.log',
            'encoding': 'utf-8',
        }
    },
    'loggers': {
        '': { # Root Logger
            'handlers': ['console', 'file_info'],
            'level': 'INFO',
            'propagate': True 
        }
    }
    }
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("Logging configurado exitosamente.")
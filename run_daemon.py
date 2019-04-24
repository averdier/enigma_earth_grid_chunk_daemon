# coding: utf-8

import os
from app import ChunkDaemon

if __name__ == '__main__':
    daemon = ChunkDaemon(os.environ.get('APP_CONFIG', 'default'))

    try:
        while True:
            daemon.loop()
    except KeyboardInterrupt:
        pass
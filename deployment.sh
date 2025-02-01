#!/bin/sh
. ./meow/bin/activate

fastapi dev ./services/facade_service.py --port 8001 &
fastapi dev ./services/logging_service.py --port 8002 &
fastapi dev ./services/messages_service.py --port 8003 &
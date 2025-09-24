#!/bin/bash

# Simple LED Control Script
VENV_PATH="/home/capstone/MotorPass/myvenv"

case "$1" in
    start)
        echo "🚀 Starting LED daemon..."
        sudo "$VENV_PATH/bin/python3" led_system/led_daemon.py &
        sleep 2
        if [ -e /tmp/motorpass_led.sock ]; then
            echo "✅ LED daemon started"
        else
            echo "❌ Failed to start"
        fi
        ;;
    stop)
        echo "🛑 Stopping LED daemon..."
        sudo pkill -f "led_system/led_daemon.py"
        [ -e /tmp/motorpass_led.sock ] && rm -f /tmp/motorpass_led.sock
        echo "✅ Stopped"
        ;;
    status)
        if pgrep -f "led_system/led_daemon.py" > /dev/null; then
            echo "✅ Daemon: RUNNING"
        else
            echo "❌ Daemon: NOT RUNNING"
        fi
        if [ -e /tmp/motorpass_led.sock ]; then
            echo "✅ Socket: EXISTS"
        else
            echo "❌ Socket: MISSING"
        fi
        ;;
    test)
        echo "🧪 Testing LEDs..."
        python3 led_control_client.py
        ;;
    *)
        echo "Usage: $0 {start|stop|status|test}"
        echo ""
        echo "Commands:"
        echo "  start  - Start LED daemon"
        echo "  stop   - Stop LED daemon"  
        echo "  status - Check status"
        echo "  test   - Test LEDs"
        ;;
esac

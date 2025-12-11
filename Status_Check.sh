#!/bin/bash
echo "🔍 Checking System Status..."
echo "============================"
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool
echo "============================"
echo "Press any key to close..."
read -n 1

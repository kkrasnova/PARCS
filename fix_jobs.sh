#!/bin/bash
# Скрипт для диагностики и исправления проблемы с job'ами

echo "=== Диагностика PARCS ==="
echo ""
echo "1. Проверка workers на master..."
gcloud compute ssh master --zone=europe-north1-a --command="docker exec klt-master-qzxy python -c \"
from parcs_py.node import MasterNode
from parcs_py.parcs import Config
import sys
# Это не сработает напрямую, но можно проверить через API
\""

echo ""
echo "2. Проверка API workers..."
gcloud compute ssh master --zone=europe-north1-a --command="curl -s http://localhost:8080/api/worker | python -m json.tool"

echo ""
echo "3. Проверка логов последней job..."
gcloud compute ssh master --zone=europe-north1-a --command="docker logs klt-master-qzxy 2>&1 | grep -A 20 'Job.*enqueued\|Starting workers\|Unable to find workers' | tail -n 30"

echo ""
echo "=== Готово ==="


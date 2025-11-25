#!/bin/bash
# Скрипт для применения исправленного scheduler.py в контейнере

echo "Применение исправления scheduler.py..."

# Сначала загрузим файл на master VM
echo "1. Загрузка файла на master VM..."
gcloud compute scp parcs-python/parcs_py/scheduler.py master:/tmp/scheduler.py --zone=europe-north1-a

# Затем скопируем в контейнер
echo "2. Копирование файла в контейнер..."
gcloud compute ssh master --zone=europe-north1-a --command="docker cp /tmp/scheduler.py klt-master-qzxy:/app/parcs_py/scheduler.py"

# Перезапустим контейнер
echo "3. Перезапуск контейнера..."
gcloud compute ssh master --zone=europe-north1-a --command="docker restart klt-master-qzxy"

echo "4. Ожидание запуска контейнера (10 секунд)..."
sleep 10

echo "5. Проверка логов..."
gcloud compute ssh master --zone=europe-north1-a --command="docker logs klt-master-qzxy 2>&1 | tail -n 20"

echo ""
echo "=== Готово! ==="
echo "Теперь создайте новую job и проверьте логи для детальной диагностики."


#!/bin/bash
# Скрипт для настройки и запуска PARCS на Google Cloud Platform

set -e

ZONE=${1:-"europe-north1-a"}
REGION="europe-north1"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Настройка PARCS на Google Cloud Platform                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Зона: $ZONE"
echo "Регион: $REGION"
echo ""

# Проверка настройки gcloud
echo "1. Проверка настройки gcloud..."
gcloud config set compute/zone "$ZONE" 2>/dev/null || true
gcloud config set compute/region "$REGION" 2>/dev/null || true

# Проверка существования master
echo ""
echo "2. Проверка существования master инстанса..."
MASTER_EXISTS=false
if gcloud compute instances describe master --zone="$ZONE" &>/dev/null; then
    MASTER_EXISTS=true
    echo "✓ Master инстанс существует"
    
    # Получаем внутренний IP master
    MASTER_INTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" --format="get(networkInterfaces[0].networkIP)" 2>/dev/null || echo "")
    if [ -z "$MASTER_INTERNAL_IP" ]; then
        echo "⚠ Не удалось получить внутренний IP master"
        echo "  Попробуйте запустить: gcloud compute instances start master --zone=$ZONE"
        MASTER_INTERNAL_IP="10.166.0.2"  # Примерный IP по умолчанию
    else
        echo "  Внутренний IP master: $MASTER_INTERNAL_IP"
    fi
else
    echo "✗ Master инстанс не найден"
    echo ""
    echo "Создание master инстанса..."
    gcloud compute instances create-with-container master \
        --zone="$ZONE" \
        --container-image=registry.hub.docker.com/hummer12007/parcs-node \
        --container-env PARCS_ARGS="master" \
        --machine-type=n1-standard-1
    
    echo "Ожидание запуска master (30 секунд)..."
    sleep 30
    
    MASTER_INTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" --format="get(networkInterfaces[0].networkIP)" 2>/dev/null || echo "10.166.0.2")
    echo "✓ Master создан, внутренний IP: $MASTER_INTERNAL_IP"
fi

# Проверка и создание worker инстансов
echo ""
echo "3. Проверка worker инстансов..."
WORKERS_TO_CREATE=()

for i in 1 2 3; do
    WORKER_NAME="worker$i"
    if gcloud compute instances describe "$WORKER_NAME" --zone="$ZONE" &>/dev/null; then
        echo "✓ $WORKER_NAME существует"
    else
        echo "✗ $WORKER_NAME не найден"
        WORKERS_TO_CREATE+=("$WORKER_NAME")
    fi
done

# Создание недостающих worker инстансов
if [ ${#WORKERS_TO_CREATE[@]} -gt 0 ]; then
    echo ""
    echo "4. Создание worker инстансов: ${WORKERS_TO_CREATE[*]}"
    echo "   Используется внутренний IP master: $MASTER_INTERNAL_IP"
    
    gcloud compute instances create-with-container "${WORKERS_TO_CREATE[@]}" \
        --zone="$ZONE" \
        --container-image=registry.hub.docker.com/hummer12007/parcs-node \
        --container-env PARCS_ARGS="worker $MASTER_INTERNAL_IP" \
        --machine-type=n1-standard-1
    
    echo "Ожидание запуска workers (30 секунд)..."
    sleep 30
    echo "✓ Workers созданы"
else
    echo "✓ Все worker инстансы существуют"
fi

# Запуск всех инстансов
echo ""
echo "5. Запуск всех инстансов..."
./start_instances.sh "$ZONE"

# Получение внешнего IP master
echo ""
echo "6. Получение информации о master..."
MASTER_EXTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" --format="get(networkInterfaces[0].accessConfigs[0].natIP)" 2>/dev/null || echo "")

if [ -n "$MASTER_EXTERNAL_IP" ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   PARCS готов к использованию!                             ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Веб-интерфейс PARCS доступен по адресу:"
    echo "  http://$MASTER_EXTERNAL_IP:8080"
    echo ""
    echo "Для создания job:"
    echo "  1. Откройте веб-интерфейс в браузере"
    echo "  2. Загрузите файл prime_solution.py"
    echo "  3. Загрузите входной файл (например, prime_input_10000.txt)"
    echo "  4. Создайте job"
    echo ""
else
    echo "⚠ Не удалось получить внешний IP master"
    echo "  Проверьте статус: gcloud compute instances list --zones=$ZONE"
fi


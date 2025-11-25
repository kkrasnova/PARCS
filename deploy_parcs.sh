#!/bin/bash
# Полный скрипт для развертывания PARCS на Google Cloud Platform

set -e

ZONE=${1:-"europe-north1-a"}
REGION="europe-north1"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Развертывание PARCS на Google Cloud Platform             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Зона: $ZONE"
echo "Регион: $REGION"
echo ""

# Настройка gcloud
echo "1. Настройка gcloud..."
gcloud config set compute/zone "$ZONE" 2>/dev/null || true
gcloud config set compute/region "$REGION" 2>/dev/null || true

# Проверка firewall правил
echo ""
echo "2. Проверка firewall правил..."
if gcloud compute firewall-rules describe allow-all &>/dev/null; then
    echo "✓ Firewall правило 'allow-all' существует"
else
    echo "Создание firewall правила..."
    gcloud compute firewall-rules create allow-all \
        --direction=INGRESS \
        --priority=1000 \
        --network=default \
        --action=ALLOW \
        --rules=all \
        --source-ranges=0.0.0.0/0 || echo "⚠ Не удалось создать firewall правило (возможно, уже существует)"
fi

# Проверка и создание master
echo ""
echo "3. Проверка master инстанса..."
MASTER_EXISTS=false
MASTER_INTERNAL_IP=""

if gcloud compute instances describe master --zone="$ZONE" &>/dev/null 2>&1; then
    MASTER_EXISTS=true
    echo "✓ Master инстанс существует"
    MASTER_INTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" \
        --format="get(networkInterfaces[0].networkIP)" 2>/dev/null || echo "")
    
    if [ -z "$MASTER_INTERNAL_IP" ]; then
        echo "⚠ Не удалось получить внутренний IP, используем стандартный"
        MASTER_INTERNAL_IP="10.166.0.2"
    else
        echo "  Внутренний IP: $MASTER_INTERNAL_IP"
    fi
else
    echo "✗ Master инстанс не найден"
    echo "  Создание master инстанса..."
    
    gcloud compute instances create-with-container master \
        --zone="$ZONE" \
        --container-image=registry.hub.docker.com/hummer12007/parcs-node \
        --container-env PARCS_ARGS="master" \
        --machine-type=n1-standard-1
    
    echo "  Ожидание запуска master (40 секунд)..."
    sleep 40
    
    MASTER_INTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" \
        --format="get(networkInterfaces[0].networkIP)" 2>/dev/null || echo "10.166.0.2")
    
    echo "✓ Master создан"
    echo "  Внутренний IP: $MASTER_INTERNAL_IP"
fi

# Проверка и создание workers
echo ""
echo "4. Проверка worker инстансов..."
WORKERS_TO_CREATE=()

for i in 1 2 3; do
    WORKER_NAME="worker$i"
    if gcloud compute instances describe "$WORKER_NAME" --zone="$ZONE" &>/dev/null 2>&1; then
        echo "✓ $WORKER_NAME существует"
    else
        echo "✗ $WORKER_NAME не найден"
        WORKERS_TO_CREATE+=("$WORKER_NAME")
    fi
done

if [ ${#WORKERS_TO_CREATE[@]} -gt 0 ]; then
    echo ""
    echo "5. Создание worker инстансов: ${WORKERS_TO_CREATE[*]}"
    echo "   Внутренний IP master: $MASTER_INTERNAL_IP"
    
    gcloud compute instances create-with-container "${WORKERS_TO_CREATE[@]}" \
        --zone="$ZONE" \
        --container-image=registry.hub.docker.com/hummer12007/parcs-node \
        --container-env PARCS_ARGS="worker $MASTER_INTERNAL_IP" \
        --machine-type=n1-standard-1
    
    echo "  Ожидание запуска workers (40 секунд)..."
    sleep 40
    echo "✓ Workers созданы"
else
    echo "✓ Все worker инстансы существуют"
fi

# Запуск всех инстансов
echo ""
echo "6. Запуск всех инстансов..."
gcloud compute instances start master --zone="$ZONE" 2>/dev/null || echo "Master уже запущен"

for i in 1 2 3; do
    WORKER_NAME="worker$i"
    if gcloud compute instances describe "$WORKER_NAME" --zone="$ZONE" &>/dev/null 2>&1; then
        gcloud compute instances start "$WORKER_NAME" --zone="$ZONE" 2>/dev/null || echo "$WORKER_NAME уже запущен"
    fi
done

echo "  Ожидание готовности (30 секунд)..."
sleep 30

# Получение информации
echo ""
echo "7. Получение информации о развертывании..."
MASTER_EXTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" \
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)" 2>/dev/null || echo "")

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   PARCS успешно развернут!                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ -n "$MASTER_EXTERNAL_IP" ]; then
    echo "🌐 Веб-интерфейс PARCS:"
    echo "   http://$MASTER_EXTERNAL_IP:8080"
    echo ""
fi

echo "📋 Следующие шаги:"
echo "   1. Откройте веб-интерфейс в браузере"
echo "   2. Перейдите в раздел 'Add Job'"
echo "   3. Загрузите файл: prime_solution.py"
echo "   4. Загрузите входной файл (например, prime_input_10000.txt)"
echo "   5. Создайте job и дождитесь выполнения"
echo ""
echo "📁 Файлы для загрузки:"
echo "   - prime_solution.py (solution file)"
echo "   - prime_input_10000.txt (input file)"
echo "   - prime_input_100000.txt (input file)"
echo "   - prime_input_1000000.txt (input file)"
echo ""
echo "🔧 Полезные команды:"
echo "   ./list_instances.sh          - список инстансов"
echo "   ./start_instances.sh         - запуск всех инстансов"
echo "   ./stop_instances.sh          - остановка всех инстансов"
echo "   ./get_master_ip.sh           - информация о master"
echo ""


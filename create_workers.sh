#!/bin/bash
# Скрипт для создания worker инстансов для PARCS

ZONE=${1:-"europe-north1-a"}

echo "Создание worker инстансов в зоне $ZONE..."
echo ""

# Пытаемся получить внутренний IP master
echo "Получение внутреннего IP master..."
MASTER_INTERNAL_IP=""

# Пробуем несколько способов получить IP
if gcloud compute instances describe master --zone="$ZONE" &>/dev/null; then
    MASTER_INTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" \
        --format="get(networkInterfaces[0].networkIP)" 2>/dev/null || echo "")
fi

# Если не получилось, используем стандартный IP или запрашиваем у пользователя
if [ -z "$MASTER_INTERNAL_IP" ]; then
    echo "⚠ Не удалось автоматически получить IP master"
    echo ""
    echo "Пожалуйста, введите внутренний IP адрес master инстанса"
    echo "Вы можете найти его командой:"
    echo "  gcloud compute instances describe master --zone=$ZONE --format='get(networkInterfaces[0].networkIP)'"
    echo ""
    read -p "Внутренний IP master (или нажмите Enter для использования 10.166.0.2): " MASTER_INTERNAL_IP
    MASTER_INTERNAL_IP=${MASTER_INTERNAL_IP:-"10.166.0.2"}
fi

echo "Используется внутренний IP master: $MASTER_INTERNAL_IP"
echo ""

# Проверяем, какие workers нужно создать
WORKERS_TO_CREATE=()
for i in 1 2 3; do
    WORKER_NAME="worker$i"
    if gcloud compute instances describe "$WORKER_NAME" --zone="$ZONE" &>/dev/null 2>&1; then
        echo "✓ $WORKER_NAME уже существует"
    else
        echo "✗ $WORKER_NAME не найден, будет создан"
        WORKERS_TO_CREATE+=("$WORKER_NAME")
    fi
done

if [ ${#WORKERS_TO_CREATE[@]} -eq 0 ]; then
    echo ""
    echo "Все worker инстансы уже существуют!"
    exit 0
fi

echo ""
echo "Создание worker инстансов: ${WORKERS_TO_CREATE[*]}"
echo ""

# Создаем workers
gcloud compute instances create-with-container "${WORKERS_TO_CREATE[@]}" \
    --zone="$ZONE" \
    --container-image=registry.hub.docker.com/hummer12007/parcs-node \
    --container-env PARCS_ARGS="worker $MASTER_INTERNAL_IP" \
    --machine-type=n1-standard-1

echo ""
echo "Ожидание запуска workers (30 секунд)..."
sleep 30

echo ""
echo "✓ Worker инстансы созданы!"
echo ""
echo "Теперь запустите все инстансы:"
echo "  ./start_instances.sh"


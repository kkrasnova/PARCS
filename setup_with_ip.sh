#!/bin/bash
# Скрипт для настройки workers, если известен IP master

ZONE=${1:-"europe-north1-a"}

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Настройка PARCS workers                                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Пытаемся получить IP автоматически
MASTER_INTERNAL_IP=""

echo "Попытка автоматического определения IP master..."
if gcloud compute instances describe master --zone="$ZONE" &>/dev/null 2>&1; then
    MASTER_INTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" \
        --format="get(networkInterfaces[0].networkIP)" 2>/dev/null || echo "")
    
    if [ -n "$MASTER_INTERNAL_IP" ]; then
        echo "✓ Найден внутренний IP master: $MASTER_INTERNAL_IP"
    fi
fi

# Если не получилось, запрашиваем у пользователя
if [ -z "$MASTER_INTERNAL_IP" ]; then
    echo ""
    echo "Не удалось автоматически определить IP master."
    echo ""
    echo "Пожалуйста, введите внутренний IP адрес master инстанса."
    echo "Вы можете найти его:"
    echo "  1. В Google Cloud Console: Compute Engine > VM instances"
    echo "  2. Или выполните: gcloud compute instances describe master --zone=$ZONE"
    echo ""
    read -p "Внутренний IP master: " MASTER_INTERNAL_IP
    
    if [ -z "$MASTER_INTERNAL_IP" ]; then
        echo "Ошибка: IP адрес не может быть пустым"
        exit 1
    fi
fi

echo ""
echo "Используется внутренний IP master: $MASTER_INTERNAL_IP"
echo ""

# Проверяем существующие workers
echo "Проверка существующих worker инстансов..."
WORKERS_TO_CREATE=()

for i in 1 2 3; do
    WORKER_NAME="worker$i"
    if gcloud compute instances describe "$WORKER_NAME" --zone="$ZONE" &>/dev/null 2>&1; then
        echo "✓ $WORKER_NAME уже существует"
    else
        echo "✗ $WORKER_NAME не найден"
        WORKERS_TO_CREATE+=("$WORKER_NAME")
    fi
done

if [ ${#WORKERS_TO_CREATE[@]} -eq 0 ]; then
    echo ""
    echo "✓ Все worker инстансы уже существуют!"
    echo ""
    echo "Запуск всех инстансов..."
    ./start_instances.sh "$ZONE"
    exit 0
fi

echo ""
echo "Создание worker инстансов: ${WORKERS_TO_CREATE[*]}"
echo ""

# Создаем workers
if gcloud compute instances create-with-container "${WORKERS_TO_CREATE[@]}" \
    --zone="$ZONE" \
    --container-image=registry.hub.docker.com/hummer12007/parcs-node \
    --container-env PARCS_ARGS="worker $MASTER_INTERNAL_IP" \
    --machine-type=n1-standard-1; then
    
    echo ""
    echo "✓ Worker инстансы созданы!"
    echo "Ожидание запуска (30 секунд)..."
    sleep 30
    
    echo ""
    echo "Запуск всех инстансов..."
    ./start_instances.sh "$ZONE"
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   PARCS настроен!                                          ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Получите внешний IP master для доступа к веб-интерфейсу:"
    echo "  ./get_master_ip.sh"
    echo ""
else
    echo ""
    echo "✗ Ошибка при создании worker инстансов"
    echo ""
    echo "Возможные причины:"
    echo "  1. Недостаточно прав (требуется compute.instances.create)"
    echo "  2. Неверный IP адрес master"
    echo "  3. Проблемы с сетью"
    echo ""
    echo "Попробуйте:"
    echo "  1. Проверить права доступа"
    echo "  2. Создать инстансы через веб-консоль Google Cloud"
    echo "  3. Обратиться к администратору проекта"
    exit 1
fi


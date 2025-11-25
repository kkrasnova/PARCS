#!/bin/bash
# Скрипт для перезапуска всех PARCS инстансов в Google Cloud

ZONE=${1:-"europe-north1-a"}

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Перезапуск всех PARCS инстансов                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Зона: $ZONE"
echo ""

# Список всех инстансов
INSTANCES=("master" "worker1" "worker2" "worker3")

echo "1. Остановка всех инстансов..."
echo "-------------------------------------------------------------------"

for instance in "${INSTANCES[@]}"; do
    if gcloud compute instances describe "$instance" --zone="$ZONE" &>/dev/null 2>&1; then
        STATUS=$(gcloud compute instances describe "$instance" --zone="$ZONE" \
            --format="get(status)" 2>/dev/null || echo "UNKNOWN")
        
        if [ "$STATUS" = "RUNNING" ]; then
            echo "Остановка $instance..."
            gcloud compute instances stop "$instance" --zone="$ZONE" 2>&1 | grep -v "WARNING" || true
        else
            echo "$instance уже остановлен (статус: $STATUS)"
        fi
    else
        echo "⚠ $instance не найден, пропускаем"
    fi
done

echo ""
echo "Ожидание полной остановки (20 секунд)..."
sleep 20

echo ""
echo "2. Запуск всех инстансов..."
echo "-------------------------------------------------------------------"

for instance in "${INSTANCES[@]}"; do
    if gcloud compute instances describe "$instance" --zone="$ZONE" &>/dev/null 2>&1; then
        echo "Запуск $instance..."
        gcloud compute instances start "$instance" --zone="$ZONE" 2>&1 | grep -v "WARNING" || true
    fi
done

echo ""
echo "Ожидание запуска инстансов (40 секунд)..."
sleep 40

echo ""
echo "3. Проверка статуса инстансов..."
echo "-------------------------------------------------------------------"

for instance in "${INSTANCES[@]}"; do
    if gcloud compute instances describe "$instance" --zone="$ZONE" &>/dev/null 2>&1; then
        STATUS=$(gcloud compute instances describe "$instance" --zone="$ZONE" \
            --format="get(status)" 2>/dev/null || echo "UNKNOWN")
        
        INTERNAL_IP=$(gcloud compute instances describe "$instance" --zone="$ZONE" \
            --format="get(networkInterfaces[0].networkIP)" 2>/dev/null || echo "N/A")
        
        EXTERNAL_IP=$(gcloud compute instances describe "$instance" --zone="$ZONE" \
            --format="get(networkInterfaces[0].accessConfigs[0].natIP)" 2>/dev/null || echo "N/A")
        
        if [ "$STATUS" = "RUNNING" ]; then
            echo "✓ $instance: RUNNING"
            echo "  Internal IP: $INTERNAL_IP"
            if [ "$EXTERNAL_IP" != "N/A" ] && [ -n "$EXTERNAL_IP" ]; then
                echo "  External IP: $EXTERNAL_IP"
            fi
        else
            echo "✗ $instance: $STATUS"
        fi
    else
        echo "✗ $instance: не найден"
    fi
    echo ""
done

# Получаем информацию о master для веб-интерфейса
echo "4. Информация для доступа к PARCS..."
echo "-------------------------------------------------------------------"

MASTER_EXTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" \
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)" 2>/dev/null || echo "")

MASTER_INTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" \
    --format="get(networkInterfaces[0].networkIP)" 2>/dev/null || echo "")

if [ -n "$MASTER_EXTERNAL_IP" ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   PARCS готов к использованию!                             ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 Веб-интерфейс PARCS:"
    echo "   http://$MASTER_EXTERNAL_IP:8080"
    echo ""
    echo "📋 Внутренний IP master (для workers):"
    echo "   $MASTER_INTERNAL_IP"
    echo ""
    echo "📁 Файлы для загрузки в веб-интерфейсе:"
    echo "   - prime_solution.py (Solution File)"
    echo "   - prime_input_10000.txt (Input File)"
    echo "   - prime_input_100000.txt (Input File)"
    echo "   - prime_input_1000000.txt (Input File)"
    echo ""
else
    echo "⚠ Не удалось получить внешний IP master"
    echo "   Проверьте статус инстансов вручную"
fi

echo ""
echo "✓ Перезапуск завершен!"


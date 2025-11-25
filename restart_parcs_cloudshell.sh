#!/bin/bash
# Скрипт для выполнения в Google Cloud Shell
# Останавливает и перезапускает все PARCS инстансы

ZONE="europe-north1-a"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Перезапуск всех PARCS инстансов                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Зона: $ZONE"
echo ""

# 1. Остановка всех инстансов
echo "1. Остановка всех инстансов..."
echo "-------------------------------------------------------------------"
gcloud compute instances stop master worker1 worker2 worker3 --zone=$ZONE

echo ""
echo "Ожидание полной остановки (20 секунд)..."
sleep 20

# 2. Запуск всех инстансов
echo ""
echo "2. Запуск всех инстансов..."
echo "-------------------------------------------------------------------"
gcloud compute instances start master worker1 worker2 worker3 --zone=$ZONE

echo ""
echo "Ожидание запуска инстансов (40 секунд)..."
sleep 40

# 3. Проверка статуса
echo ""
echo "3. Проверка статуса инстансов..."
echo "-------------------------------------------------------------------"
gcloud compute instances list --zones=$ZONE --format="table(name,zone,status,networkInterfaces[0].networkIP:label=INTERNAL_IP,networkInterfaces[0].accessConfigs[0].natIP:label=EXTERNAL_IP)"

# 4. Получение IP master
echo ""
echo "4. Информация для доступа к PARCS..."
echo "-------------------------------------------------------------------"
MASTER_IP=$(gcloud compute instances describe master --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)" 2>/dev/null || echo "")

if [ -n "$MASTER_IP" ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   PARCS готов к использованию!                             ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 Веб-интерфейс PARCS:"
    echo "   http://$MASTER_IP:8080"
    echo ""
    echo "📋 Важно: После перезапуска загрузите обновленный"
    echo "   prime_solution.py через веб-интерфейс при создании нового job!"
    echo ""
else
    echo "⚠ Не удалось получить внешний IP master"
fi

echo ""
echo "✓ Перезапуск завершен!"


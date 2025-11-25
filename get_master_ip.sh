#!/bin/bash
# Скрипт для получения IP адресов master инстанса

ZONE=${1:-"europe-north1-a"}

echo "Получение информации о master инстансе..."
echo ""

if gcloud compute instances describe master --zone="$ZONE" &>/dev/null; then
    echo "✓ Master инстанс найден"
    echo ""
    
    INTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" \
        --format="get(networkInterfaces[0].networkIP)" 2>/dev/null || echo "не удалось получить")
    
    EXTERNAL_IP=$(gcloud compute instances describe master --zone="$ZONE" \
        --format="get(networkInterfaces[0].accessConfigs[0].natIP)" 2>/dev/null || echo "не удалось получить")
    
    STATUS=$(gcloud compute instances describe master --zone="$ZONE" \
        --format="get(status)" 2>/dev/null || echo "неизвестно")
    
    echo "Статус: $STATUS"
    echo "Внутренний IP: $INTERNAL_IP"
    echo "Внешний IP: $EXTERNAL_IP"
    echo ""
    
    if [ "$EXTERNAL_IP" != "не удалось получить" ] && [ -n "$EXTERNAL_IP" ]; then
        echo "Веб-интерфейс PARCS:"
        echo "  http://$EXTERNAL_IP:8080"
        echo ""
    fi
    
    if [ "$INTERNAL_IP" != "не удалось получить" ] && [ -n "$INTERNAL_IP" ]; then
        echo "Для создания workers используйте:"
        echo "  ./create_workers.sh"
        echo ""
        echo "Или вручную:"
        echo "  gcloud compute instances create-with-container worker1 worker2 worker3 \\"
        echo "    --zone=$ZONE \\"
        echo "    --container-image=registry.hub.docker.com/hummer12007/parcs-node \\"
        echo "    --container-env PARCS_ARGS=\"worker $INTERNAL_IP\" \\"
        echo "    --machine-type=n1-standard-1"
    fi
else
    echo "✗ Master инстанс не найден в зоне $ZONE"
    echo ""
    echo "Создайте master инстанс командой:"
    echo "  gcloud compute instances create-with-container master \\"
    echo "    --zone=$ZONE \\"
    echo "    --container-image=registry.hub.docker.com/hummer12007/parcs-node \\"
    echo "    --container-env PARCS_ARGS=\"master\" \\"
    echo "    --machine-type=n1-standard-1"
fi


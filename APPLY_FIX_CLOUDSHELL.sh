#!/bin/bash
# Команды для выполнения в Cloud Shell для применения исправления

# 1. Подключиться к master
gcloud compute ssh master --zone=europe-north1-a

# Затем на master выполнить:
# docker exec -i klt-master-qzxy bash -c 'cat > /app/parcs_py/scheduler.py' < parcs-python/parcs_py/scheduler.py

# ИЛИ проще - создать файл прямо в контейнере через Python:

cat << 'EOF' | gcloud compute ssh master --zone=europe-north1-a --command="docker exec -i klt-master-qzxy python -c \"
import sys
code = '''$(cat parcs-python/parcs_py/scheduler.py | python -c 'import sys; print(repr(sys.stdin.read()))')'''
with open('/app/parcs_py/scheduler.py', 'w') as f:
    f.write(code)
print('File updated')
\""
EOF

# Но проще всего - скопировать файл через docker cp после загрузки на VM


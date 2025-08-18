# LDAP Groups Sync

Сервис для синхронизации групп пользователей между LDAP и OpenWebUI.

## 🚀 Быстрый старт

### 1. Запуск всех сервисов

```bash
# Запуск всех сервисов
docker compose up -d

# Проверка статуса
docker compose ps
```

### 2. Автоматическая настройка OpenWebUI

Система автоматически:
- ✅ Генерирует API ключ для OpenWebUI
- ✅ Обновляет конфигурацию с реальным API ключом
- ✅ Запускает sync сервис с правильными настройками

### 3. Проверка работы

```bash
# Проверка метрик sync сервиса
curl http://localhost:8000/metrics

# Проверка health endpoints
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

## 📋 Ручная настройка OpenWebUI (если нужно)

Если автоматическая настройка не работает, выполните следующие шаги:

### 1. Откройте OpenWebUI в браузере
```
http://localhost:8080
```

### 2. Создайте админ аккаунт
- **Email**: `admin@example.com`
- **Password**: `adminpassword`

### 3. Создайте API ключ
1. Перейдите в **Settings > Account**
2. Создайте новый API ключ
3. Скопируйте ключ

### 4. Обновите конфигурацию
```bash
# Сохраните API ключ в файл
echo "YOUR_API_KEY_HERE" > .owui_api_key

# Обновите конфигурацию
python3 scripts/update_config.py
```

## 🔧 Конфигурация

### Переменные окружения (.env)

```bash
# LDAP Configuration
LDAP_URL=ldap://openldap:1389
LDAP_BIND_DN=cn=admin,dc=example,dc=com
LDAP_BIND_PASSWORD=adminpassword
LDAP_VERIFY_TLS=false
VERIFY_TLS=false

# OpenWebUI Configuration
OWUI_BASE_URL=http://openwebui:8080
OWUI_ADMIN_EMAIL=admin@example.com
OWUI_ADMIN_PASSWORD=adminpassword
OWUI_ADMIN_NAME=Admin User
```

### Маппинг групп (config/config.yaml)

```yaml
group_mappings:
  - ldap_group_dn: "cn=dep1,ou=groups,dc=example,dc=com"
    target_group_name: "Demo Group A"
  - ldap_group_dn: "cn=dep2,ou=groups,dc=example,dc=com"
    target_group_name: "Demo Group B"
```

## 📊 Мониторинг

### Метрики Prometheus

```bash
# Получить все метрики
curl http://localhost:8000/metrics

# Ключевые метрики:
# - sync_iterations_total - количество итераций синхронизации
# - external_request_seconds - время запросов к внешним сервисам
# - owui_http_errors_total - ошибки HTTP запросов к OpenWebUI
# - ldap_lookup_errors_total - ошибки поиска в LDAP
```

### Health Checks

```bash
# Проверка готовности
curl http://localhost:8000/readyz

# Проверка здоровья
curl http://localhost:8000/healthz
```

## 🏗️ Архитектура

### Сервисы

1. **OpenLDAP** - источник данных о пользователях и группах
2. **OpenWebUI** - целевая система для синхронизации
3. **Sync Service** - основной сервис синхронизации
4. **Mock API** - тестовый API для разработки

### Компоненты

- **LDAP Provider** - подключение к LDAP
- **OpenWebUI Adapter** - взаимодействие с OpenWebUI API
- **Sync Engine** - логика синхронизации
- **Metrics** - метрики Prometheus

## 🧪 Тестирование

### Запуск тестов

```bash
# Unit тесты
pytest tests/

# Интеграционные тесты
pytest tests/integration/
```

### Тестовые данные

Демо данные загружаются автоматически в OpenLDAP:
- Пользователь: `demo@example.com`
- Группы: `dep1`, `dep2`

## 🔍 Отладка

### Логи сервисов

```bash
# Логи sync сервиса
docker compose logs sync

# Логи OpenWebUI
docker compose logs openwebui

# Логи OpenLDAP
docker compose logs openldap
```

### Проверка подключений

```bash
# Проверка LDAP
docker compose exec sync ldapsearch -H ldap://openldap:1389 -D "cn=admin,dc=example,dc=com" -w adminpassword -b "dc=example,dc=com"

# Проверка OpenWebUI API
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8080/api/v1/groups
```

## 📝 Разработка

### Структура проекта

```
├── sync_service/          # Основной код
│   ├── adapters/         # Адаптеры для внешних сервисов
│   ├── domain/           # Доменные модели
│   ├── services/         # Бизнес-логика
│   └── utils/            # Утилиты
├── scripts/              # Скрипты настройки
├── config/               # Конфигурация
├── tests/                # Тесты
└── compose.yaml          # Docker Compose
```

### Добавление нового сервиса

1. Создайте адаптер в `sync_service/adapters/`
2. Добавьте конфигурацию в `config/config.yaml`
3. Обновите `sync_service/services/sync_engine.py`
4. Добавьте тесты

## 🚨 Устранение неполадок

### Проблемы с OpenWebUI

1. **OpenWebUI не отвечает**
   ```bash
   # Проверьте статус
   docker compose ps openwebui
   
   # Проверьте логи
   docker compose logs openwebui
   ```

2. **API ключ не работает**
   ```bash
   # Перегенерируйте ключ
   python3 scripts/generate_api_key.py
   
   # Обновите конфигурацию
   python3 scripts/update_config.py
   ```

### Проблемы с LDAP

1. **Не удается подключиться к LDAP**
   ```bash
   # Проверьте переменные окружения
   cat .env
   
   # Проверьте подключение
   docker compose exec sync ldapsearch -H ldap://openldap:1389 -D "cn=admin,dc=example,dc=com" -w adminpassword -b "dc=example,dc=com"
   ```

### Проблемы с синхронизацией

1. **Sync сервис не запускается**
   ```bash
   # Проверьте логи
   docker compose logs sync
   
   # Проверьте конфигурацию
   cat config/config.yaml
   ```

## 📄 Лицензия

MIT License

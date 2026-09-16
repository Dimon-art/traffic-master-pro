# TrafficMaster Pro
Нейро-тренер для экспертов по продвижению в Telegram.

## Быстрый старт
1. cp .env.example .env
2. Задайте POSTGRES_PASSWORD в .env
3. cp secrets/openai_key.txt.example secrets/openai_key.txt
4. cp secrets/google_service_account.json.example secrets/google_service_account.json
5. docker compose up -d --build

## Доступ
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/api/docs

## Остановка
- docker compose down
- Полная очистка (удалить БД): docker compose down -v

## Тренировки
Доступен первый режим — «Знание продукта».

1. Примените миграции: `docker compose exec backend alembic upgrade head`
2. Банк вопросов: `knowledge_base_volume/product_knowledge/questions.json`
3. В интерфейсе: «Начать тренировку» → режим «Знание продукта»
4. История: пункт «Мои тренировки» в шапке (нужен вход)

Оценка пока моковая: совпадение ключевых слов, без вызова OpenAI.

## Бэкапы и восстановление данных

### ⚠️ Главное правило

НИКОГДА не запускайте `docker compose down -v` без явного намерения.
Ключ `-v` (volumes) УДАЛЯЕТ ВСЕ ДАННЫЕ:
- Postgres (пользователи, заявки, тренировки)
- Redis (кэш)

Безопасные команды:
    docker compose down          # ✅ без -v, данные сохранятся
    docker compose stop          # ✅ ещё безопаснее
    docker compose restart       # ✅ перезапуск

### Создание бэкапа

    powershell -ExecutionPolicy Bypass -File scripts/backup_db.ps1

Результат: `backups/backup_YYYY-MM-DD_HH-mm-ss.sql` (полный дамп Postgres).

Старые дампы (>30 дней) удаляются автоматически.

### Восстановление из бэкапа

    powershell -ExecutionPolicy Bypass -File scripts/restore_db.ps1 -BackupFile backups/backup_XXXX.sql

⚠️ Восстановление ПЕРЕЗАПИШЕТ текущую БД. Скрипт запросит подтверждение.

### Рекомендации

- Делать бэкап **перед** любыми рискованными операциями (миграции, `down -v`).
- Хранить 2-3 последних бэкапа локально.
- **Раз в неделю** копировать свежий дамп на внешний носитель или в облако.
- Пароль от Postgres и SECRET_KEY — в менеджере паролей.

### Восстановление пароля Postgres

Если забыли пароль:
    docker compose exec db psql -U trainer -d traffic_master -c "ALTER USER trainer WITH PASSWORD 'новый_пароль';"
И затем обновить значение в `.env`.


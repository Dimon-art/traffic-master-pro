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

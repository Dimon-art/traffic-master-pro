# Бэкапы базы данных

## Создать бэкап
    powershell -ExecutionPolicy Bypass -File scripts/backup_db.ps1

Дамп сохранится в `backups/backup_YYYY-MM-DD_HH-mm-ss.sql`.

## Восстановить из бэкапа
    powershell -ExecutionPolicy Bypass -File scripts/restore_db.ps1 -BackupFile backups/backup_2026-09-16_20-00-00.sql

⚠️ Восстановление ПЕРЕЗАПИШЕТ текущую БД. Запросит подтверждение.

## Рекомендации
- Делать бэкап перед каждым `docker compose down -v` (или избегать его).
- Хранить 2-3 последних бэкапа локально.
- Раз в неделю — копировать свежий дамп на внешний носитель или в облако.

# Деплой

Проект полностью контейнеризирован (`Dockerfile` + `docker-compose.yml`), поэтому подходит
для любой платформы с поддержкой Docker. Ниже — два самых простых варианта для пет/коммерческого
проекта такого масштаба.

## Вариант 1: Render.com (бесплатный тир, проще всего)

1. Зарегистрируйтесь на render.com и подключите GitHub-репозиторий.
2. Создайте **PostgreSQL** (New → PostgreSQL) — Render сам выдаст `DATABASE_URL`.
3. Создайте **Redis** (New → Redis) — понадобится для Celery.
4. Создайте **Web Service** из репозитория:
   - Environment: Docker
   - Добавьте переменные окружения из `.env.example`, подставив реальные значения
     (`POSTGRES_*` — из шага 2, `CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND` — из шага 3)
   - Start command уже задан в `Dockerfile`/`docker-compose.yml`
5. (опционально) создайте **Background Worker** с командой `celery -A config worker --loglevel=info`
   и **Cron Job** или ещё один Background Worker для `celery -A config beat --loglevel=info`.
6. Для бота — ещё один Background Worker с командой `python -m bot.main` и переменной `TELEGRAM_BOT_TOKEN`.

## Вариант 2: любой VPS (Timeweb, Selectel, Yandex Cloud и т.п.)

```bash
git clone <repo-url>
cd booking-crm
cp .env.example .env   # заполнить реальными значениями, USE_SQLITE_FOR_TESTS=False
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Дальше — Nginx как reverse-proxy перед `web` (порт 8000) и Let's Encrypt для HTTPS.

## Чек-лист перед продакшеном

- [ ] `DJANGO_DEBUG=False`
- [ ] Сгенерирован новый `DJANGO_SECRET_KEY` (не тот, что в `.env.example`)
- [ ] `DJANGO_ALLOWED_HOSTS` содержит реальный домен
- [ ] Настроен реальный `TELEGRAM_BOT_TOKEN` (получить у @BotFather)
- [ ] Регулярный бэкап базы Postgres

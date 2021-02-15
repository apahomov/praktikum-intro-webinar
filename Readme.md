# Запуск

## Подготовка

Ставим docker: https://docs.docker.com/get-docker/

Копируем `.env_example` файлы в аналогичные `.env`

**В файле `bot.env` не хватает ключа, его можно получить через BotFather**

## Старт

Билд:
```bash
make build
```

Запуск:
```bash
make run
```

Заливаем данные:
```bash
make load_data
```
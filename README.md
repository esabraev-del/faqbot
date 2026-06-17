# 🤖 Telegram FAQ-бот факультета ФКиНВП

Двуязычный бот (рус/каз) с inline-кнопками и FAQ из JSON-файла.

---

## 📁 Структура файлов

```
tgbot/
├── bot.py          — основной код бота
├── faq.json        — вопросы и ответы (редактируйте этот файл)
├── requirements.txt
└── README.md
```

---

## 🚀 Установка и запуск

### 1. Получите токен бота
1. Откройте Telegram, найдите [@BotFather](https://t.me/BotFather)
2. Отправьте `/newbot`, придумайте имя и username
3. Скопируйте токен вида `1234567890:ABCdef...`

### 2. Установите Python и зависимости
```bash
pip install -r requirements.txt
```

### 3. Вставьте токен в `bot.py`
Найдите строку:
```python
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬТЕ_ВАШ_ТОКЕН_ЗДЕСЬ")
```
Замените `ВСТАВЬТЕ_ВАШ_ТОКЕН_ЗДЕСЬ` на ваш токен.

**Или** задайте переменную окружения (рекомендуется):
```bash
export BOT_TOKEN="ваш_токен_здесь"
```

### 4. Запустите бота
```bash
python bot.py
```

---

## ✏️ Как редактировать FAQ

Откройте `faq.json`. Структура простая:

```json
{
  "categories": [
    {
      "id": "уникальный_id",
      "ru": "🏷️ Название на русском",
      "kz": "🏷️ Атауы қазақша",
      "questions": [
        {
          "id": "уникальный_id_вопроса",
          "ru_q": "Вопрос на русском?",
          "kz_q": "Сұрақ қазақша?",
          "ru_a": "Ответ на русском.",
          "kz_a": "Жауап қазақша."
        }
      ]
    }
  ]
}
```

### Что можно менять:
- ➕ Добавить категорию — скопируйте блок `{...}` в `"categories"`
- ➕ Добавить вопрос — скопируйте блок `{...}` в `"questions"` нужной категории
- ✏️ Изменить текст — просто отредактируйте `ru_a` / `kz_a`
- ❌ Удалить — удалите блок

> ⚠️ **Важно:** у каждого `id` должно быть уникальное значение. После изменений бот перечитывает JSON автоматически — перезапускать не нужно!

---

## 🌐 Деплой на сервер (опционально)

### Вариант 1: Запуск в фоне (Linux)
```bash
nohup python bot.py &
```

### Вариант 2: systemd-сервис
Создайте файл `/etc/systemd/system/faqbot.service`:
```ini
[Unit]
Description=FAQ Telegram Bot

[Service]
WorkingDirectory=/путь/к/tgbot
ExecStart=/usr/bin/python3 bot.py
Environment=BOT_TOKEN=ваш_токен
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
systemctl enable faqbot && systemctl start faqbot
```

### Вариант 3: Бесплатный хостинг
- [Railway.app](https://railway.app) — просто загрузите папку
- [Render.com](https://render.com) — бесплатный план
- [PythonAnywhere](https://pythonanywhere.com) — бесплатный план

---

## 💬 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Запустить / вернуться в главное меню |
| `/help`  | Справка |

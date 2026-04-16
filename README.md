# DevStudio - Сайт для приема заявок на разработку

Современный веб-сервис для приема заказов на разработку программного обеспечения с интеграцией платежной системы YooKassa.

## Возможности

- 📦 **Каталог услуг** - Красочный каталог с услугами по разработке
- 🔐 **Регистрация/Авторизация** - Система регистрации и входа через email
- 💳 **Интеграция YooKassa** - Прием платежей через популярную российскую платежную систему
- 👤 **Личный кабинет** - Профиль пользователя с историей заказов
- 🎨 **Современный дизайн** - Темная тема с градиентными элементами
- 📱 **Адаптивность** - Корректное отображение на всех устройствах

## Технологии

- **Backend**: Flask (Python)
- **Database**: SQLite (по умолчанию), поддержка PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Payments**: YooKassa SDK
- **Frontend**: HTML5, CSS3, JavaScript

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения (создайте файл `.env`):
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///devsite.db
YOOKASSA_ACCOUNT_ID=your_account_id
YOOKASSA_SECRET_KEY=your_secret_key
```

3. Запустите приложение:
```bash
python app.py
```

4. Откройте браузер и перейдите по адресу:
```
http://localhost:5000
```

## Структура проекта

```
/workspace
├── app.py                 # Основное приложение Flask
├── requirements.txt       # Зависимости Python
├── templates/             # HTML шаблоны
│   ├── base.html         # Базовый шаблон
│   ├── index.html        # Главная страница
│   ├── register.html     # Регистрация
│   ├── login.html        # Вход
│   ├── order.html        # Оформление заказа
│   ├── order_success.html # Успех заказа
│   ├── payment_success.html # Успех оплаты
│   └── profile.html      # Личный кабинет
└── static/
    ├── css/
    │   └── style.css     # Стили
    └── js/
        └── main.js       # JavaScript
```

## Настройка YooKassa

1. Зарегистрируйтесь в [YooKassa](https://yookassa.ru/)
2. Получите `account_id` и `secret_key` в личном кабинете
3. Добавьте их в переменные окружения

## Тестовые услуги

При первом запуске автоматически создаются следующие услуги:

- Telegram Бот - 15 000 ₽
- Веб-сайт - 50 000 ₽
- Веб-сервис - 100 000 ₽
- Десктопное приложение - 80 000 ₽
- API Разработка - 40 000 ₽
- Консультация - 5 000 ₽

# Використовуємо базовий образ Python
FROM python:3.8

# Встановлюємо бібліотеки
RUN pip install http.server

# Створюємо каталог додатку
WORKDIR /app

# Копіюємо файли у контейнер
COPY . /app

# Виконуємо команду для запуску серверів
CMD ["python", "main.py"]
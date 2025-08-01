CREATE TABLE "users" (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    username TEXT
);

CREATE TABLE "tasks" (
    task_id             INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный ID задачи
    short_description   TEXT NOT NULL,                     -- Краткое описание задачи
    description         TEXT,                              -- Полное описание того, что нужно сделать
    deadline            DATE                               -- Дедлайн в стандартном формате ГГГГ-ММ-ДД
);

CREATE TABLE "user_tasks" (
    user_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, task_id), -- Составной первичный ключ
    FOREIGN KEY (user_id) REFERENCES "users" (user_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES "tasks" (task_id) ON DELETE CASCADE
);

Заполнение тестовыми данными
INSERT INTO "users" (user_id, full_name, username, is_admin) VALUES
(1, 'Иван Администратор', 'admin_ivan', TRUE),
(2, 'Анна Работник', 'worker_anna', FALSE),
(3, 'Петр Работник', 'worker_petr', FALSE);

-- Добавление задач
-- Даты дедлайнов указаны в формате 'ГГГГ-ММ-ДД', подходящем для типа DATE
INSERT INTO "tasks" (task_id, short_description, description, deadline) VALUES
(101, 'Завершить отчет по проекту', 'Подготовить и сдать финальный отчет по проекту "Альфа" до конца недели.', '2025-08-10'),
(102, 'Разработать новую функцию', 'Реализовать функцию импорта данных из CSV-файлов для модуля "Статистика".', '2025-08-20'),
(103, 'Настроить CI/CD пайплайн', 'Оптимизировать и протестировать пайплайн непрерывной интеграции/доставки для нового сервиса.', '2025-09-01');

-- Привязка пользователей к задачам
INSERT INTO "user_tasks" (user_id, task_id) VALUES
-- Задача 101: на одном работнике (Анна Работник)
(2, 101),
-- Задача 102: на двух работниках (Анна Работник и Петр Работник)
(2, 102),
(3, 102),
-- Задача 103: на админе (Иван Администратор)
(1, 103);

#Изменил пользователей на себя, себя и Влада


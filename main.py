from datetime import datetime
from pathlib import Path
from typing import Optional
import json

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Academy AI Demo", description="Демо-система для студентов и менеджеров")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Демоданные. В реальном проекте эти данные будут храниться в PostgreSQL.
students = [
    {"id": 101, "name": "Айжан Осмонова", "group": "Python-24", "phone": "+996 700 111 222", "email": "aijan@example.com", "course": "Python Backend"},
    {"id": 102, "name": "Нурбек Асанов", "group": "Python-24", "phone": "+996 555 333 444", "email": "nurbek@example.com", "course": "Python Backend"},
    {"id": 103, "name": "Мээрим Жумабекова", "group": "AI-12", "phone": "+996 770 555 666", "email": "meerim@example.com", "course": "AI / ML"},
]
progress = {
    "ООП": {"score": 42, "terms": ["класс и объект", "наследование", "инкапсуляция"], "videos": ["ООП простыми словами", "Классы и объекты на Python"]},
    "SQL": {"score": 86, "terms": ["JOIN", "GROUP BY"], "videos": ["SQL JOIN на примерах"]},
    "FastAPI": {"score": 63, "terms": ["Pydantic", "Depends"], "videos": ["FastAPI: основы и зависимости"]},
}

class ProgressRequest(BaseModel):
    student_id: int = 101
    topic: str = "ООП"
    score: int = 42

class TaskRequest(BaseModel):
    technology: str = "Python"
    level: str = "Junior"
    topic: str = "REST API"

class StudentRequest(BaseModel):
    name: str
    group: str
    phone: str = ""
    email: str = ""
    course: str = "Python Backend"

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/api/students")
def get_students():
    return students

@app.get("/api/progress")
def get_progress():
    return progress

@app.post("/api/diagnose")
def diagnose(data: ProgressRequest):
    topic = data.topic.strip() or "ООП"
    score = max(0, min(100, data.score))
    if score < 50:
        level = "Нужно повторить"
        message = f"Похоже, тема «{topic}» пока даётся непросто. Рекомендуем повторить основные термины и посмотреть видео."
        terms = progress.get(topic, progress["ООП"])["terms"]
        videos = progress.get(topic, progress["ООП"])["videos"]
        actions = ["Повторить термины: " + ", ".join(terms), "Посмотреть: " + " и ".join(videos), "Пройти короткий тест ещё раз"]
    elif score < 75:
        level = "Есть пробелы"
        message = f"Тема «{topic}» в целом понятна, но некоторые моменты стоит закрепить."
        terms = progress.get(topic, progress["FastAPI"])["terms"]
        videos = progress.get(topic, progress["FastAPI"])["videos"]
        actions = ["Повторить: " + ", ".join(terms), "Посмотреть видео: " + " и ".join(videos), "Решить 2 практические задачи"]
    else:
        level = "Хороший результат"
        message = f"Отлично! По теме «{topic}» результат хороший. Попробуйте практическую задачу повышенной сложности."
        actions = ["Перейти к практической задаче уровня выше", "Объяснить тему своими словами"]
    return {"student_id": data.student_id, "topic": topic, "score": score, "level": level, "message": message, "actions": actions}

@app.post("/api/generate-task")
def generate_task(data: TaskRequest):
    tech = data.technology.strip() or "Python"
    level = data.level
    topic = data.topic.strip() or "REST API"
    tasks = {
        "Python": f"Создайте консольное приложение на Python для учёта заявок. Реализуйте добавление, просмотр, поиск и изменение статуса заявки. Уровень: {level}.",
        "FastAPI": f"Разработайте REST API на FastAPI для сущности «{topic}». Добавьте CRUD-эндпоинты, Pydantic-схемы, валидацию и обработку ошибок. Уровень: {level}.",
        "SQL": f"Спроектируйте таблицы для задачи «{topic}», напишите SQL-запросы с JOIN, GROUP BY и сортировкой. Уровень: {level}.",
        "Django": f"Создайте Django-приложение по теме «{topic}»: модели, миграции, представления и проверку входных данных. Уровень: {level}.",
    }
    description = tasks.get(tech, f"Выполните практическую задачу по теме «{topic}» с использованием {tech}. Уровень: {level}.")
    return {
        "title": f"Практическое задание: {topic}",
        "technology": tech,
        "level": level,
        "description": description,
        "requirements": [
            "Разделить код на логичные функции или модули",
            "Проверить корректность входных данных",
            "Добавить обработку ошибок",
            "Подготовить README с инструкцией запуска",
        ],
        "acceptance": ["Приложение запускается без ошибок", "Основной сценарий работает", "Код читаемый и проверен на примерах"],
        "note": "Демо-генерация по шаблонам. В полной версии AI будет создавать задания на основе актуальных вакансий и требований работодателей."
    }

@app.post("/api/students")
def create_student(data: StudentRequest):
    next_id = max([s["id"] for s in students], default=100) + 1
    student = {"id": next_id, **data.model_dump()}
    students.append(student)
    return {"message": "Анкета студента создана", "student": student}

@app.get("/api/export")
def export_students():
    return {"generated_at": datetime.now().isoformat(timespec="seconds"), "count": len(students), "students": students}

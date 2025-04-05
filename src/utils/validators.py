from datetime import datetime

def validate_deadline(date_str: str) -> datetime:
    """Проверяет корректность даты выполнения."""
    try:
        deadline = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        if deadline < datetime.now():
            raise ValueError("Срок выполнения не может быть в прошлом.")
        return deadline
    except ValueError:
        raise ValueError("Некорректный формат даты. Используйте ГГГГ-ММ-ДД ЧЧ:ММ.")
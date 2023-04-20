from typing import List


class Poll:
    """
    self.poll_id - ID опроса. Изменится после отправки от имени бота
    self.question - Текст вопроса
    self.options - "Распакованное" содержимое массива m_options в массив options
    self.owner - Владелец опроса
    self.chat_id - Чат, в котором опубликован опрос
    """
    type: str = "poll"

    def __init__(self, poll_id, question, options, owner_id):
        self.poll_id: str = poll_id   # ID опроса. Изменится после отправки от имени бота
        self.question: str = question  # Текст вопроса
        self.options: List[str] = [*options] # "Распакованное" содержимое массива m_options в массив options
        self.owner: int = owner_id  # Владелец опроса
        self.chat_id: int = 0  # Чат, в котором опубликован опрос
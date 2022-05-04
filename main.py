import os
from datetime import datetime
import requests
import time
from tqdm import tqdm


class API:
    url_users: str = "https://json.medrating.org/users"
    url_todos: str = "https://json.medrating.org/todos"

    def users(self):
        try:
            users_request = requests.get(self.url_users)
            users = users_request.json()
            return users
        except requests.exceptions.ConnectionError:
            print("Не удалось получить список пользователей.")
            return None

    def get_user(self, user_id: int):
        try:
            user_request = requests.get(f"{self.url_users}/{user_id}")
            user = user_request.json()
            return user
        except requests.exceptions.ConnectionError:
            return None

    def user_todos(self, user_id: int):
        try:
            user_todos = requests.get(f"{self.url_todos}/?userId={user_id}")
            todos = user_todos.json()
            return todos
        except requests.exceptions.ConnectionError:
            print("Не удалось получить список задач.")
            return None


class Write:
    def __init__(self, directory_name: str = "tasks"):
        self.users = None
        self.directory_name = directory_name
        self.api_hand = API()
        self.set_users()

    def mkdir(self):
        try:
            if not os.path.exists(self.directory_name):
                os.mkdir(self.directory_name)
            return True
        except OSError:
            print("Ошибка при создании директории.")
            return False

    def set_users(self):
        self.users = self.api_hand.users()

    def todo(self, user):
        user_todos = self.api_hand.user_todos(user['id'])
        completed_todos = list(filter(lambda todo: todo['completed'], user_todos))
        uncompleted_todos = list(filter(lambda todo: not todo['completed'], user_todos))
        return user_todos, completed_todos, uncompleted_todos

    @staticmethod
    def todo_title(todo: dict):
        if len(todo['title']) > 48:
            todo['title'] = f"{todo['title'][:48]}..."
        return todo['title']

    def user_record(self, user: dict):
        user_todos, completed_todos, uncompleted_todos = self.todo(user)

        record = f"Отчёт {user['company']['name']}.\n"
        record += f"{user['name']} <{user['email']}> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        record += f"Всего задач: {len(user_todos)}\n\n"

        record += f"Завершённые задачи ({len(completed_todos)}):\n"

        for completed_todo in completed_todos:
            record += f"{self.todo_title(completed_todo)}\n"
        record += "\n"
        record += f"Оставшиеся задачи ({len(uncompleted_todos)}):\n"

        for uncompleted_todo in uncompleted_todos:
            record += f"{self.todo_title(uncompleted_todo)}\n"

        return record

    def user_file_name(self, user: dict):
        filename = f"{user['username']}"

        if os.path.exists(f"{self.directory_name}/{filename}.txt"):
            created_at = os.path.getmtime(f"{self.directory_name}/{filename}.txt")
            created_at = datetime.strptime(time.ctime(created_at), "%a %b %d %H:%M:%S %Y")
            os.renames(f"{self.directory_name}/{filename}.txt",
                       f"{self.directory_name}/old_{filename}_{created_at.strftime('%Y-%m-%dT%H-%M-%S')}.txt")

        return f"{filename}.txt"

    def write(self):
        if self.mkdir():
            for user in self.users:
                with open(
                        f"{self.directory_name}/{self.user_file_name(user)}", 'w', encoding="utf-8"
                ) as user_file:
                    record = self.user_record(user)
                    user_file.write(record)

    def run(self):
        self.write()


if __name__ == "__main__":
    writ = Write()
    writ.run()
    mylist = [1, 2, 3, 4, 5]
    for i in tqdm(mylist):
        time.sleep(1)
    print('Задача выполнена, смотрите папку tasks\n'
          'Всего хорошего и до новых встреч!')

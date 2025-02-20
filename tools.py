import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Union
import pytz  # Added for proper time zone handling

# Define timezone for proper daylight saving handling
PST = pytz.timezone("America/Los_Angeles")

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

class Objective:
    def __init__(self, name: str, deadline: datetime, urgency: int):
        self.name = name
        self.deadline = deadline.astimezone(pytz.utc)  # Store deadlines in UTC
        self.urgency = urgency  

    def to_dict(self) -> Dict[str, Union[str, int]]:
        return {
            "name": self.name, 
            "deadline": self.deadline.strftime('%Y-%m-%d %H:%M:%S %Z'),
            "urgency": self.urgency
        }

    @staticmethod
    def from_dict(data: Dict[str, Union[str, int]]) -> 'Objective':
        # Convert stored UTC time back to a localized PST time
        deadline_utc = datetime.strptime(data["deadline"], '%Y-%m-%d %H:%M:%S %Z')
        deadline_pst = PST.normalize(pytz.utc.localize(deadline_utc).astimezone(PST))
        return Objective(data["name"], deadline_pst, data["urgency"])

class ToDoList:
    def __init__(self, filename: str = "tasks.json", undoname: str = "undo.json"):
        self.filename = filename
        self.undoname = undoname
        self.tasks: List[Objective] = self.load_tasks()
        self.sort_tasks()

    def load_tasks(self) -> List[Objective]:
        filepath = os.path.join(os.path.dirname(__file__), self.filename)
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                return [Objective.from_dict(task) for task in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_tasks(self):
        filepath = os.path.join(os.path.dirname(__file__), self.filename)
        undopath = os.path.join(os.path.dirname(__file__), self.undoname)

        #Save tasks.json as undo.json as a backup before updating
        with open(undopath, "w", encoding="utf-8") as file:
            #gather old tasks before resetting
            old_tasks = self.load_tasks()
            #save old tasks
            json.dump([task.to_dict() for task in old_tasks], file, indent=4)

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump([task.to_dict() for task in self.tasks], file, indent=4)

    def sort_tasks(self):
        self.tasks.sort(key=lambda x: x.deadline)

    def add_task(self, name: str, day_hour: str, urgency: int):
        if not self.validate_day_hour(day_hour) or not isinstance(urgency, int):
            raise ValueError("Invalid input: Ensure correct day-hour format (DD HH) and integer urgency.")
        deadline = self.format_deadline(day_hour)
        self.tasks.append(Objective(name, deadline, urgency))
        self.sort_tasks()
        self.save_tasks()

    def remove_task(self, identifier: Union[str, int]):
        if isinstance(identifier, int):
            if 0 <= identifier < len(self.tasks):
                del self.tasks[identifier]
            else:
                raise ValueError("Invalid remove_task index number.")
        else:
            name_lower = identifier.lower()
            self.tasks = [task for task in self.tasks if task.name.lower() != name_lower]
        self.save_tasks()

    def update_task(self, identifier: Union[str, int], new_name: str = None, new_day_hour: str = None, new_urgency: int = None):
        task = self.get_task(identifier)
        if new_name:
            task.name = new_name
        if new_day_hour: 
            task.deadline = self.format_deadline(new_day_hour)
        if new_urgency:
            task.urgency = new_urgency
        self.sort_tasks()
        self.save_tasks()

    def get_task(self, identifier: Union[str, int]) -> Union[Objective, None]:
        if isinstance(identifier, int) and 0 <= identifier < len(self.tasks):
            return self.tasks[identifier]
        elif isinstance(identifier, str):
            name_lower = identifier.lower()
            for task in self.tasks:
                if task.name.lower() == name_lower:
                    return task
        return None

    def validate_identifier(self, identifier: Union[str, int]) -> bool:
        """Check if the identifier is a valid index or task name."""
        if isinstance(identifier, int):
            return 0 <= identifier < len(self.tasks)
        elif isinstance(identifier, str):
            return any(task.name.lower() == identifier.lower() for task in self.tasks)
        return False

    @staticmethod
    def validate_day_hour(day_hour: str) -> bool:
        try:
            day, hour = map(int, day_hour.split())
            _ = ToDoList.format_deadline(day_hour)
            return True
        except ValueError:
            pass
        return False

    @staticmethod
    def get_now() -> datetime:
        """Get current time in PST, properly handling daylight savings."""
        return datetime.now(PST)

    @staticmethod
    def format_deadline(day_hour: str) -> datetime:
        """Convert the given day and hour into a proper PST deadline and store in UTC."""
        now = ToDoList.get_now()
        day, hour = map(int, day_hour.split())
        
        # Construct a naive datetime object in the current month and year
        deadline = datetime(now.year, now.month, day, hour, 0)
        
        # Convert to PST and adjust for DST automatically
        deadline_pst = PST.localize(deadline, is_dst=None)

        # If deadline is in the past, assume next month
        if deadline_pst < now - timedelta(days=1):
            if now.month == 12:
                deadline_pst = PST.localize(datetime(now.year + 1, 1, day, hour, 0), is_dst=None)
            else:
                deadline_pst = PST.localize(datetime(now.year, now.month + 1, day, hour, 0), is_dst=None)

        # Convert to UTC for storage
        return deadline_pst.astimezone(pytz.utc)

    def undo(self):
        filepath = os.path.join(os.path.dirname(__file__), self.undoname)
        #check if path exists or the json file is just an empty list
        print(os.path.getsize(filepath))
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 2:
            return False
        
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.tasks = [Objective.from_dict(task) for task in data]
                self.sort_tasks()
                self.save_tasks()
                #empty out undo file so that 2 undos cannot happen back to back
                with open(filepath, "w", encoding="utf-8") as file:
                    json.dump([], file, indent=4)
                return True
            
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def display_tasks(self):
        clear_console()
        if not self.tasks:
            print("No tasks available.")
            return
        
        now_utc = self.get_now().astimezone(pytz.utc)
        past_deadlines = []
        upcoming_tasks = []
        
        for i, task in enumerate(self.tasks):
            task_deadline_pst = task.deadline.astimezone(PST)
            if task.deadline < now_utc:
                past_deadlines.append((i, task, task_deadline_pst))
            else:
                upcoming_tasks.append((i, task, task_deadline_pst))

        def print_tasks(title, tasks):
            if tasks:
                print(f"\n{title}:")
                print(f"{'Index':<10}{'Task Name':<60}{'Deadline (PST)':<25}{'Urgency':<10}")
                print("-" * 110)
                for i, task, task_deadline_pst in sorted(tasks, key=lambda x: x[2]):
                    urgency_color = "\033[92m"  # Green
                    if task.urgency == 2:
                        urgency_color = "\033[38;5;192m"  # Yellow-green mix
                    elif task.urgency == 3:
                        urgency_color = "\033[38;5;226m"  # More saturated highlighter yellow
                    elif task.urgency == 4:
                        urgency_color = "\033[38;5;214m"  # Orange
                    elif task.urgency == 5:
                        urgency_color = "\033[91m"  # Red
                    reset_color = "\033[0m"
                    print(f"{urgency_color}[{str(i) + ']':<6} {task.name:<60} {task_deadline_pst.strftime('%m-%d %A %H:00'):<25} {task.urgency:<10}{reset_color}")

        print_tasks("Overdue Tasks", past_deadlines)
        print_tasks("Upcoming Tasks", upcoming_tasks)

if __name__ == "__main__":
    todo = ToDoList()
    todo.display_tasks()

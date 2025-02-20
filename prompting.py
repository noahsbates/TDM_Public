from tools import ToDoList

def basic_action(options = ['a', 'r', 'u', 'l', 'f', 'h', 'q']):
    action = input("\nChoose an action: ").strip().lower()
    if action in options:
        return action
    else:
        print("Invalid option. Try again.")
        return basic_action(options)

def add_task():
    while True:
        name = input("Task name: ")
        if name:
            break
        print("Task name cannot be empty.")

    while True:
        day_hour = input("Deadline (DD HH): ")
        if day_hour and ToDoList.validate_day_hour(day_hour):
            break
        print("Please try again.")
    
    while True:
        urgency = input("Urgency (1-5): ")
        if urgency and urgency.isdigit() and 1 <= int(urgency) <= 5:
            break
        print("Invalid urgency level. Try again.")
    
    return name, day_hour, int(urgency)

def update_task():
    name = input("Task name (blank -> keep): ")

    while True:
        day_hour = input("Deadline (DD HH) (blank -> keep): ")
        if day_hour == "":
            break
        if ToDoList.validate_day_hour(day_hour):
            break
        print("Date does not exist or is not formatted correctly. Please try again.")
    
    while True:
        urgency = input("Urgency (1-5) (blank -> keep): ")
        if urgency == "":
            break
        if urgency and urgency.isdigit() and 1 <= int(urgency) <= 5:
            break
        print("Please try again.")
    
    return name, day_hour, int(urgency) if urgency else None

def find_task(message, todo: ToDoList):
    while True:
        identifierRaw = input(message)
        identifier = int(identifierRaw) if identifierRaw.isdigit() else identifierRaw
        if todo.validate_identifier(identifier):
            return identifier
        print("Please try again.")
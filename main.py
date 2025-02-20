from tools import ToDoList
import prompting

def main():
    todo = ToDoList()
    todo.display_tasks()
    print("\n\t=== Welcome! Type 'h' for help. ===")
    
    while True:
        action = prompting.basic_action(['a', 'r', 'u', 'l', 'z', 'h', 'q'])

        if action == 'a':
            name, day_hour, urgency = prompting.add_task()
            todo.add_task(name, day_hour, urgency)
            todo.display_tasks()
            print("\n\t=== Task added successfully. ===")

        elif action == 'r':
            identifier = prompting.find_task("Enter task name or number to remove: ", todo)
            todo.remove_task(identifier)
            todo.display_tasks()
            print("\n\t=== Task removed successfully. ===")

        elif action == 'u':
            identifier = prompting.find_task("Enter task name or number to update: ", todo)
            new_name, new_day_hour, new_urgency = prompting.update_task()
            todo.update_task(identifier, new_name, new_day_hour, new_urgency)
            todo.display_tasks()
            print("\n\t=== Task updated successfully. ===")

        elif action == 'l':
            todo.display_tasks()
        
        elif action == 'z':
            changed = todo.undo()
            todo.display_tasks()
            if changed:
                print("\n\t=== Last action undone. ===")
            else:
                print("\n\t=== No actions to undo. ===")

        elif action == 'h':
            todo.display_tasks()
            print()

            print("""
            Controls:
            a - Add task
            r - Remove task
            u - Update task
            l - List tasks
            z - undo
            h - Help (show controls)
            q - Quit
            """)

        elif action == 'q':
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
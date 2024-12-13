def error_for_list_title(title, lists):
    if not 1 <= len(title) <= 100:
        return "The title must be between 1 and 100 characters"
    elif any(lst['title'] == title for lst in lists):
        return "The title must be unique."
    else:
        return None

def error_for_todo(name):
    if 1 <= len(name) <= 100:
        return None

    return "Todo name must be between 1 and 100 characters"

def find_list_by_id(list_id, lists):
    return next((lst for lst in lists if lst['id'] == list_id), None)

def find_todo_by_id(todo_id, todos):
    return next((todo for todo in todos if todo['id'] == todo_id), None)

def is_list_completed(lst):
    return len(lst['todos']) > 0 and todos_remaining(lst) == 0

def is_todo_completed(todo):
    return todo['completed']

def mark_all_completed(lst):
    for todo in lst['todos']:
        todo['completed'] = True

    return None

def delete_todo_by_id(todo_id, lst):
    lst['todos'] = [todo for todo in lst['todos'] if todo['id'] != todo_id]
    return None

def sort_items(items, select_completed):
    sorted_items = sorted(items, key=lambda item: item['title'].lower())

    incomplete_items = [item for item in sorted_items
                        if not select_completed(item)]
    complete_items = [item for item in sorted_items
                      if select_completed(item)]

    return incomplete_items + complete_items

def todos_remaining(lst):
    return sum(1 for todo in lst['todos'] if not todo['completed'])

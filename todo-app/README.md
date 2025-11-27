# Todo App

A beautiful Django todo application with a modern dark-themed UI.

## Features

- ✅ Create, edit, and delete todos
- 📅 Assign due dates to tasks
- ✔️ Mark todos as resolved/completed
- 🔍 Filter by status (All, Active, Done)
- 🎨 Modern dark UI with gradient accents

## Quick Start

### Prerequisites

- Python 3.8+
- uv (Python package manager)

### Installation

```bash
# Navigate to the project directory
cd todo-app

# Install dependencies (already done if you cloned)
uv sync

# Run migrations
uv run python manage.py migrate

# Start the development server
uv run python manage.py runserver
```

### Access the App

Open your browser and go to: **http://localhost:8000**

## Project Structure

```
todo-app/
├── todoproject/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── todos/                # Todo app
│   ├── models.py         # Todo model
│   ├── views.py          # CRUD views
│   ├── forms.py          # Todo form
│   ├── urls.py           # URL routing
│   ├── templates/        # HTML templates
│   └── templatetags/     # Custom filters
├── manage.py
├── pyproject.toml
└── uv.lock
```

## Usage

1. **Create a Todo**: Click "+ New Task" button
2. **Edit a Todo**: Click the ✏️ icon on any task
3. **Delete a Todo**: Click the 🗑️ icon on any task
4. **Toggle Complete**: Click the circle checkbox to mark as done
5. **Filter Tasks**: Use the tabs to filter by All/Active/Done

## Preview
![preview_todo_app](/images/01_todo_app.png)



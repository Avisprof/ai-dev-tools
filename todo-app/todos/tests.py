from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from .models import Todo
from .forms import TodoForm


class TodoModelTests(TestCase):
    """Tests for the Todo model."""

    def test_create_todo(self):
        """Test that a todo can be created with correct fields."""
        todo = Todo.objects.create(
            title="Test Todo",
            description="Test description",
            due_date=date.today() + timedelta(days=7)
        )
        self.assertEqual(todo.title, "Test Todo")
        self.assertEqual(todo.description, "Test description")
        self.assertEqual(todo.due_date, date.today() + timedelta(days=7))
        self.assertFalse(todo.resolved)

    def test_string_representation(self):
        """Test that __str__ returns the title."""
        todo = Todo.objects.create(title="My Task")
        self.assertEqual(str(todo), "My Task")

    def test_default_resolved_is_false(self):
        """Test that new todos have resolved=False by default."""
        todo = Todo.objects.create(title="New Task")
        self.assertFalse(todo.resolved)

    def test_timestamps_auto_set(self):
        """Test that created_at and updated_at are automatically set."""
        todo = Todo.objects.create(title="Timestamp Test")
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)

    def test_ordering(self):
        """Test that todos are ordered by resolved, due_date, created_at."""
        # Create todos in specific order
        todo_resolved = Todo.objects.create(
            title="Resolved",
            resolved=True,
            due_date=date.today()
        )
        todo_active_soon = Todo.objects.create(
            title="Active due soon",
            resolved=False,
            due_date=date.today() + timedelta(days=1)
        )
        todo_active_later = Todo.objects.create(
            title="Active due later",
            resolved=False,
            due_date=date.today() + timedelta(days=7)
        )
        
        todos = list(Todo.objects.all())
        # Active todos should come before resolved (resolved=False < resolved=True)
        # Among active, earlier due dates come first
        self.assertEqual(todos[0], todo_active_soon)   # Active, due sooner
        self.assertEqual(todos[1], todo_active_later)  # Active, due later
        self.assertEqual(todos[2], todo_resolved)      # Resolved at the end


class TodoFormTests(TestCase):
    """Tests for the TodoForm."""

    def test_valid_form(self):
        """Test that form accepts valid data."""
        form_data = {
            'title': 'Valid Task',
            'description': 'Some description',
            'due_date': date.today() + timedelta(days=5),
            'resolved': False
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_title_invalid(self):
        """Test that form rejects empty title."""
        form_data = {
            'title': '',
            'description': 'Description without title',
        }
        form = TodoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_optional_fields(self):
        """Test that description and due_date can be blank."""
        form_data = {
            'title': 'Minimal Task',
            'description': '',
            'due_date': '',
            'resolved': False
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_date_format(self):
        """Test that due_date accepts valid date."""
        form_data = {
            'title': 'Task with date',
            'due_date': '2025-12-31',
            'resolved': False
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())


class TodoListViewTests(TestCase):
    """Tests for the TodoListView."""

    def setUp(self):
        self.client = Client()
        self.list_url = reverse('todos:list')

    def test_list_view_displays_todos(self):
        """Test that GET /todos/ shows all todos."""
        Todo.objects.create(title="Task 1")
        Todo.objects.create(title="Task 2")
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 2")

    def test_list_view_filter_active(self):
        """Test that ?filter=active shows only unresolved todos."""
        Todo.objects.create(title="Active Task", resolved=False)
        Todo.objects.create(title="Done Task", resolved=True)
        
        response = self.client.get(f"{self.list_url}?filter=active")
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Task")
        self.assertNotContains(response, "Done Task")

    def test_list_view_filter_resolved(self):
        """Test that ?filter=resolved shows only completed todos."""
        Todo.objects.create(title="Active Task", resolved=False)
        Todo.objects.create(title="Done Task", resolved=True)
        
        response = self.client.get(f"{self.list_url}?filter=resolved")
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Active Task")
        self.assertContains(response, "Done Task")

    def test_list_view_empty_state(self):
        """Test that empty state message shows when no todos exist."""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No tasks yet")

    def test_list_view_context_counts(self):
        """Test that context includes correct counts."""
        Todo.objects.create(title="Active 1", resolved=False)
        Todo.objects.create(title="Active 2", resolved=False)
        Todo.objects.create(title="Done 1", resolved=True)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.context['total_count'], 3)
        self.assertEqual(response.context['active_count'], 2)
        self.assertEqual(response.context['resolved_count'], 1)


class TodoCreateViewTests(TestCase):
    """Tests for the TodoCreateView."""

    def setUp(self):
        self.client = Client()
        self.create_url = reverse('todos:create')

    def test_create_view_get(self):
        """Test that GET shows empty form."""
        response = self.client.get(self.create_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create New Task")
        self.assertIsInstance(response.context['form'], TodoForm)

    def test_create_view_post_valid(self):
        """Test that POST with valid data creates todo and redirects."""
        form_data = {
            'title': 'New Task',
            'description': 'Task description',
            'due_date': '2025-12-31',
            'resolved': False
        }
        
        response = self.client.post(self.create_url, form_data)
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Todo.objects.count(), 1)
        self.assertEqual(Todo.objects.first().title, 'New Task')

    def test_create_view_post_invalid(self):
        """Test that POST with invalid data shows errors."""
        form_data = {
            'title': '',  # Required field empty
            'description': 'Description',
        }
        
        response = self.client.post(self.create_url, form_data)
        
        self.assertEqual(response.status_code, 200)  # Re-renders form
        self.assertEqual(Todo.objects.count(), 0)  # No todo created
        self.assertFormError(response, 'form', 'title', 'This field is required.')


class TodoUpdateViewTests(TestCase):
    """Tests for the TodoUpdateView."""

    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(
            title="Original Title",
            description="Original description"
        )
        self.update_url = reverse('todos:edit', kwargs={'pk': self.todo.pk})

    def test_update_view_get(self):
        """Test that GET shows form with existing data."""
        response = self.client.get(self.update_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Task")
        self.assertContains(response, "Original Title")

    def test_update_view_post_valid(self):
        """Test that POST with valid data updates todo and redirects."""
        form_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'due_date': '',
            'resolved': True
        }
        
        response = self.client.post(self.update_url, form_data)
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Title')
        self.assertTrue(self.todo.resolved)


class TodoDeleteViewTests(TestCase):
    """Tests for the TodoDeleteView."""

    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(title="Task to Delete")
        self.delete_url = reverse('todos:delete', kwargs={'pk': self.todo.pk})

    def test_delete_view_get(self):
        """Test that GET shows confirmation page."""
        response = self.client.get(self.delete_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Task")
        self.assertContains(response, "Task to Delete")
        self.assertContains(response, "Are you sure")

    def test_delete_view_post(self):
        """Test that POST deletes todo and redirects."""
        response = self.client.post(self.delete_url)
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Todo.objects.count(), 0)


class TodoToggleViewTests(TestCase):
    """Tests for the toggle_resolved view."""

    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(title="Toggle Test", resolved=False)
        self.toggle_url = reverse('todos:toggle', kwargs={'pk': self.todo.pk})

    def test_toggle_resolved_to_true(self):
        """Test that toggle changes resolved from False to True."""
        response = self.client.get(self.toggle_url)
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.resolved)

    def test_toggle_resolved_to_false(self):
        """Test that toggle changes resolved from True to False."""
        self.todo.resolved = True
        self.todo.save()
        
        response = self.client.get(self.toggle_url)
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.resolved)

    def test_toggle_redirects_to_next(self):
        """Test that toggle redirects to 'next' parameter if provided."""
        next_url = '/todos/?filter=active'
        response = self.client.get(f"{self.toggle_url}?next={next_url}")
        
        self.assertRedirects(response, next_url)

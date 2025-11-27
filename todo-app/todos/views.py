from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .models import Todo
from .forms import TodoForm


class TodoListView(ListView):
    model = Todo
    template_name = 'todos/todo_list.html'
    context_object_name = 'todos'

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_type = self.request.GET.get('filter', 'all')
        
        if filter_type == 'active':
            queryset = queryset.filter(resolved=False)
        elif filter_type == 'resolved':
            queryset = queryset.filter(resolved=True)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'all')
        context['total_count'] = Todo.objects.count()
        context['active_count'] = Todo.objects.filter(resolved=False).count()
        context['resolved_count'] = Todo.objects.filter(resolved=True).count()
        return context


class TodoCreateView(CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todos:list')


class TodoUpdateView(UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todos:list')


class TodoDeleteView(DeleteView):
    model = Todo
    template_name = 'todos/todo_confirm_delete.html'
    success_url = reverse_lazy('todos:list')


def toggle_resolved(request, pk):
    """Toggle the resolved status of a todo."""
    todo = get_object_or_404(Todo, pk=pk)
    todo.resolved = not todo.resolved
    todo.save()
    
    # Redirect back to the referring page or the list
    next_url = request.GET.get('next', reverse_lazy('todos:list'))
    return HttpResponseRedirect(next_url)

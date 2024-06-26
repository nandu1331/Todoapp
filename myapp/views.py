from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import tasks
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

# Create your views here.
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ""
        self.fields['password2'].help_text = ""
        self.fields['username'].help_text = ""
@login_required
def main(request):
    alltasks = tasks.objects.filter(user=request.user)
    template = loader.get_template('index.html')
    query = request.GET.get('q')
    if query:
        alltasks = alltasks.filter(task_name__istartswith=query)
    welcome_message_shown = request.session.get('welcome_message_shown', False)
    if not welcome_message_shown:
        # Set the session variable to indicate the welcome message has been shown
        request.session['welcome_message_shown'] = True

    context = {
        'alltasks' : alltasks,
        'username' : request.user.username,
        'welcome_message_shown' : welcome_message_shown
    }
    return HttpResponse(template.render(context, request))

@login_required
def markedcomplete(request, task_id):
    task = get_object_or_404(tasks, id=task_id, user=request.user)
    task.completed = True
    task.save()
    return redirect('/')

@login_required
def addtask(request):
    success = None
    error = None
    if request.method == 'POST':
        taskName = request.POST.get('task_name')
        taskDesc = request.POST.get('task_description')
        taskDate = request.POST.get('task_date')
        taskStartTime = request.POST.get('task_start_time')
        taskEndTime = request.POST.get('task_end_time')
        try:
            task_start_datetime = datetime.strptime(f"{taskDate} {taskStartTime}", '%Y-%m-%d %H:%M')
            task_end_datetime = datetime.strptime(f"{taskDate} {taskEndTime}", '%Y-%m-%d %H:%M')
        except ValueError as e:
            error = f'Invalid date/time format: {e}'
            return render(request, 'addtask.html', {'error': error})

        # Check for overlapping tasks
        overlapping_tasks = tasks.objects.filter(
        Q(task_date=taskDate) & (
            (Q(task_start_time__lt=task_end_datetime.time()) & Q(task_end_time__gt=task_start_datetime.time())) |
            (Q(task_start_time__gte=task_start_datetime.time(), task_end_time__lte=task_end_datetime.time())) |
            (Q(task_start_time__lte=task_start_datetime.time(), task_end_time__gte=task_end_datetime.time()))
        ),
        user=request.user   
    )


        if overlapping_tasks.exists():
            overlap_msg = ""
            for task in overlapping_tasks:
                overlap_msg += f"Task '{task.task_name}' overlaps ({task.task_start_time} to {task.task_end_time})\n"
            error_message = f"Cannot add task. Overlaps with existing tasks:\n{overlap_msg}"
            return render(request, 'addtask.html', {'error': error_message})
        
        if taskName and taskDate and taskStartTime and taskEndTime:
            try:
                task_date_obj = datetime.strptime(taskDate, '%Y-%m-%d').date()
                task_start_time_obj = datetime.strptime(taskStartTime, '%H:%M').time()
                task_end_time_obj = datetime.strptime(taskEndTime, '%H:%M').time()
                cur_dateTime = datetime.now()
                if task_date_obj < cur_dateTime.date():
                    error = 'Task date is in the past!!'
                elif task_date_obj == cur_dateTime.date() and task_start_time_obj < cur_dateTime.time():
                    error = 'Task time is in the past!!'
                elif task_end_time_obj <= task_start_time_obj:
                    error = 'Task end time is before task start time'
                else:
                    task = tasks(
                        task_name = taskName,
                        task_description = taskDesc,
                        task_date = taskDate,
                        task_start_time = taskStartTime,
                        task_end_time = taskEndTime,
                    )
                    task.user = request.user
                    task.save()
                    success = 'Task added successfully'
            except ValueError as e:
                error = f'Invalid date/time format: {e}'
        else:
            error = 'Task addition failed'
            

    return render(request, 'addtask.html',{
        'success': success,
        'error': error,
    })

@login_required
def removetask(request, task_id):
    task = get_object_or_404(tasks, id=task_id, user=request.user)
    task.delete()
    return redirect('/')

@login_required
def taskdetails(request, task_id):
    task = get_object_or_404(tasks, id=task_id, user=request.user)
    return render(request, 'taskdetails.html', {'task':task})

@login_required
def taskupdate(request, task_id):
    task = get_object_or_404(tasks, id=task_id, user=request.user)
    success = None
    if request.method == 'POST':# Debug print
        task_name = request.POST.get('task_name')
        task_description = request.POST.get('task_description')
        task_date = request.POST.get('task_date')
        task_start_time = request.POST.get('task_start_time')
        task_end_time = request.POST.get('task_end_time')
        task_completed = request.POST.get('task_completed') == 'on'

        if task_name:  # Check if task_name is not None or empty
            task.task_name = task_name
            task.task_description = task_description
            task.task_date = task_date
            task.task_start_time = task_start_time
            task.task_end_time = task_end_time
            task.completed = task_completed
            task.save()
            success = 'Task Updated successfully!!'
    
    return render(request, 'taskupdate.html', {'task': task,'success' : success})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None :
                login(request, user)
                return redirect('/')
            else:
                return render(request, 'login.html', {'form':form, 'error':'Invalid username/password'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form':form})

def singup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form':form})

def logout_view(request):
    logout(request)
    return redirect('login')



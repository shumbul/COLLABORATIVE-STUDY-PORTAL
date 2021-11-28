from . forms import *
from django.core.checks import messages
from django.shortcuts import redirect, render
from django import contrib
from django.contrib import messages # for posting messages, fixed forbidden csrf token issue
from django.views import generic
import wikipedia #used in Wikipedia
import random
from django.contrib.auth.decorators import login_required
from youtubesearchpython import VideosSearch # for playing Youtube videos
import requests # used in books for searching


# Create your views here.
def home(request):
    return render(request, 'dashboard/home.html')

class NotesDetailView(generic.DetailView):
    model = Notes

@login_required
def notes(request):
    # this function is used to make notes while studying - update, delete, mark as done are it's functionalities
    if(request.method == "POST"):
        form = NoteDescForm(request.POST)
        if(form.is_valid()):
            notes = Notes(
                        title = request.POST['title'],
                        user = request.user,
                        desc = request.POST['desc'],
                        )
            notes.save()
            messages.success(request, f"Saved the notes from {request.user.username} successfully")
    else:
        form = NoteDescForm()
    notes = Notes.objects.filter(user = request.user)
    all_users = User.objects.all()
    context = {
                'notes': notes,
                'form': form,
                'all_users' : all_users,
                }
    return render(request, 'dashboard/notes.html', context)

@login_required
def delete_note(request, primaryKey=None):
    # The note associated with this specific primary key (PK) will be delete
    Notes.objects.get(id = primaryKey).delete()
    return redirect("notes")

def shareNote(request, primaryKey=None):
    # HOW to share note to another user's session?
    obj = request.POST.copy()
    shared_user = User.objects.get(pk = obj['shared_user'])
    note = Notes.objects.get(id = primaryKey)
    obj['title'] = note.title
    obj['desc'] = note.desc

    form = NoteDescForm(obj)
    if(form.is_valid()):
        print(" Sending to user: ", shared_user)
        notes = Notes(
                    title = obj['title'],
                    user = shared_user,
                    desc = obj['desc'],
                    )
        notes.save()
        messages.success(request, f"Saved the notes to {shared_user} successfully")
    else:
        messages.success(request, f"Could not save the notes to {shared_user}")
        print("FAILED SHARING")
    return redirect("notes")

@login_required
def homework(request):
    # this function is used to keep track of HW while studying - update, delete, mark as done are it's functionalities
    if(request.method == "POST"):
        hwForm = HwForm(request.POST)
        if(hwForm.is_valid()):
            try:
                done = request.POST['is_finished']
                if(done == 'on'):
                    done = True
                else:
                    done = False
            except:
                done = False
            homeworks = Homework(
                user = request.user,
                title = request.POST['title'],
                subject = request.POST['subject'],
                due = request.POST['due'],
                desc = request.POST['desc'],
                is_finished = done,
            )
            homeworks.save()
            messages.success(request, f"Saved homework from {request.user.username}!!")
    else:
        hwForm = HwForm()

    homework = Homework.objects.filter(user = request.user)
    hw_done = True
    if(len(homework) != 0):
        hw_done = False
    context = {
                'homeworks' : homework,
                'hw_done': hw_done,
                'form': hwForm,
                }
    return render(request, 'dashboard/homework.html', context)


@login_required
def update_homework(request, primaryKey = None):
    print("\n\nI AM here \n\n")
    hw = Homework.objects.get(id = primaryKey)    # updating in DB
    if(hw.is_finished == True):
        hw.is_finished = False
    else:
        hw.is_finished = True
    hw.save()
    return redirect('homework')


@login_required
def delete_homework(request, primaryKey = None):
    Homework.objects.get(id = primaryKey).delete()  # deleting from Database
    return redirect('homework')

def youtube(request):
    if(request.method == "POST"):
        YoutubeForm = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text, limit = 300)  # serch built-in function!
        res = []
        for i in video.result()['result']:
            res_dict = {
            'input': text,
            'title' : i['title'],
            'duration' : i['duration'],
            'thumbnail' : i['thumbnails'][0]['url'],
            'link' : i['link'],
            'views' : i['viewCount']['short'],
            'published' : i['publishedTime'],
            'channel' : i['channel']['name'],
            }
            # some vids don't have description
            description = ''
            if( i['descriptionSnippet']):
                for j in i['descriptionSnippet']:
                    description += j['text']
            res_dict['description'] = description
            res.append(res_dict)
            context = {
                'form': YoutubeForm,
                'results': res,
            }
        return render(request, 'dashboard/youtube.html', context)
    else:
        YoutubeForm = DashboardForm()

    context = {'form': YoutubeForm}
    return render(request, "dashboard/youtube.html", context)

@login_required
def todo(request):
    if(request.method == "POST"):
        form = TodoForm(request.POST)
        if(form.is_valid()):
            try:
                done = request.POST['is_finished']
                if(done == 'on'):
                    done = True
                else:
                    done = False
            except:
                done = False
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                desc = request.POST['desc'],
                is_finished = done
            )
            todos.save()
            messages.success(request, f"Saved todo from {request.user.username}!!")
    else:
        form = TodoForm()

    todo = Todo.objects.filter(user = request.user)
    todos_done = True
    if(len(todo) != 0):
        todos_done = False
    context = {
        'todos': todo,
        'form': form,
        'todos_done': todos_done,
    }
    return render(request, "dashboard/todo.html", context)

@login_required
def update_todo(request, primaryKey = None):
    task = Todo.objects.get(id = primaryKey)    # updating in DB
    if(task.is_finished == True):
        task.is_finished = False
    else:
        task.is_finished = True
    task.save()
    return redirect('todo')


@login_required
def delete_todo(request, primaryKey = None):
    Todo.objects.get(id = primaryKey).delete()  # deleting from DB
    return redirect('todo')


def books(request):
    if(request.method == "POST"):
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)
        ans = r.json()
        res = []
        for i in range(10):
            # res_dict = {}
            res_dict = {
            'title' : ans['items'][i]['volumeInfo']['title'],
            'subtitle' : ans['items'][i]['volumeInfo'].get('subtitle'),
            'desc' : ans['items'][i]['volumeInfo'].get('description'),
            'count' : ans['items'][i]['volumeInfo'].get('pageCount'),
            'categories' : ans['items'][i]['volumeInfo'].get('categories'),
            'rating' : ans['items'][i]['volumeInfo'].get('pageRating'),
            'thumbnail' : ans['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
            'preview' : ans['items'][i]['volumeInfo'].get('previewLink'),
            }
            res.append(res_dict)
            context = {
                'form': form,
                'results': res,
            }
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()

    context = {'form': form}
    return render(request, "dashboard/books.html", context)

def dictionary(request):
    if(request.method == "POST"):
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/" + text
        print("\n\n\nURL = ", url)
        r = requests.get(url)
        ans = r.json()
        res = []
        # print("\n\n\nANS = ")
        try:
            # print("\n\n\nHIIIII = ")
            phonetics = ans[0]['phonetics'][0]['text']
            audio = ans[0]['phonetics'][0]['audio']
            definition = ans[0]['meanings'][0]['definitions'][0]['definition']
            example = ans[0]['meanings'][0]['definitions'][0]['example']
            synonyms = ans[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
            print("CONTEXT inside TRY\n\n", context)
        except:
            context = {
                'form': form,
                'input': '',
            }
            messages.success(request, f"Word does not exist in dictionary! Try again.")
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardForm()
        context = {'form':form}
    print("\n\n\ncontext = ", context)

    return render(request, 'dashboard/dictionary.html', context)

def wiki(request):
    if(request.method == "POST"):
        text = request.POST['text']
        # print("1st -----------------------------------\n", text, " = text \n\n\n\n")
        form = DashboardForm(request.POST)
        try:
            p = wikipedia.page(text, auto_suggest = False)
        except wikipedia.DisambiguationError as e:
            s = random.choice(e.options)
            p = wikipedia.page(s, auto_suggest = False)
            # print(e, "\n\n\p=", p, "\n\n\n=---------=\n\n\n" ,s, "\\\\\\\\\n\n\n")
            # print(text, " = text \n\n\n\n")
        # p = wikipedia.page(text)
        context = {
            'form': form,
            'title': p.title,
            'details': p.summary,
            'link': p.url,
        }
        return render(request, 'dashboard/wiki.html', context)

    else:
        form = DashboardForm()
        context = {'form':form}
    return render(request, 'dashboard/wiki.html', context)

def conversion(request):
    if(request.method == "POST"):
        form = ConversationForm(request.POST)
        if request.POST['measurement'] == 'length':
            measureForm = LengthConversion()
            context = {
                'form': form,
                'measureForm': measureForm,
                'input': True,
            }
            if('input' in request.POST):
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                ans = ''
                if input and int(input) >= 0:
                    if(first == 'yard' and second == 'foot'):
                        ans = f'{input} yard = {int(input)*3} foot'
                    elif(first == 'foot' and second == 'yard'):
                        ans = f'{input} foot = {int(input)/3} yard'
                    else:
                        print("\n\n Invalid input \n\n")
                context = {
                    'form': form,
                    'measureForm': measureForm,
                    'input': True,
                    'ans': ans,
                }
                print("ANS: ", ans, "\n----------\n\n")
        if request.POST['measurement'] == 'mass':
            measureForm = MassConversion()
            context = {
                'form': form,
                'measureForm': measureForm,
                'input': True,
            }
            if('input' in request.POST):
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                ans = ''
                if input and int(input) >= 0:
                    if(first == 'pound' and second == 'kg'):
                        ans = f'{input} pound = {int(input)*0.453592} kg'
                    elif(first == 'kg' and second == 'pound'):
                        ans = f'{input} kg = {int(input)*2.20462} pound'
                    else:
                        print("\n\n Invalid input \n\n")
                context = {
                    'form': form,
                    'measureForm': measureForm,
                    'input': True,
                    'ans': ans,
                }
                print("ANS: ", ans, "\n----------\n\n")
    else:
        form = ConversationForm()
        context = {
            'form': form,
            'input': False
        }
    print(" \ncontext: ", context, "\n\n")
    return render(request, 'dashboard/conversion.html', context)

def register(request):
    if(request.method == "POST"):
        form = UserRegForm(request.POST)
        if(form.is_valid()):
            user_ = form.cleaned_data.get('username')
            messages.success(request, f"Account Created for {user_}!")
            form.save()
            return redirect("signin")
    else:
        form = UserRegForm()
    context ={
        'form': form
    }
    return render(request, "dashboard/register.html", context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished = False, user = request.user)
    todos = Todo.objects.filter(is_finished = False, user = request.user)
    if(len(homeworks)==0):
        hw_done = True
    else:
        hw_done = False
    if(len(todos)==0):
        todos_done = True
    else:
        todos_done = False
    context = {
        'hw_done' : hw_done,
        'todos_done' : todos_done,
        'homeworks' : homeworks,
        'todos' : todos,
    }
    return render(request, "dashboard/profile.html", context)

from django.shortcuts import render, redirect
from .models import Note
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import logout
import sqlite3
 
 
# create editor page
@csrf_exempt
#To fix flaw 2, delete line above
@login_required(login_url='/login/')
def editor(request):
    docid = int(request.GET.get('docid', 0))
    #notes = Note.objects.all()
    notes = Note.objects.filter(owner=request.user) | Note.objects.filter(public=True)

    if 'search' in request.session:
        search = request.session['search']
        if search != None:
            notes = notes.filter(id__in=search)
            #pass

 
    if request.method == 'POST':
        docid = int(request.POST.get('docid', 0))
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        if request.POST.get('public') == "1":
            public = True
        else:
            public = False
 
        if docid > 0:
            note = Note.objects.get(pk=docid)
            note.title = title
            note.content = content
            note.public = public
            note.save()
 
            return redirect('/?docid=%i' % docid)
        else:
            note = Note.objects.create(title=title, content=content, owner=request.user, public=public)
 
            return redirect('/?docid=%i' % note.id)
 
    if docid > 0:
        note = Note.objects.get(pk=docid)
        '''
        #Fix for flaw 1
        if not note in notes:
            context = {
                'docid': docid,
                'notes': notes,
            }
            return render(request, 'cantView.html', context)
        '''
    else:
        note = ''

    request.session['search'] = None
 
    context = {
        'docid': docid,
        'notes': notes,
        'note': note,
    }

    if docid > 0 and note.owner != request.user:
        return render(request, 'viewNote.html', context)
 
    return render(request, 'editor.html', context)
 

@login_required(login_url='/login/')
def search(request):
    request.session['search'] = None
    if request.method == 'POST':
        searchword = request.POST.get('search')
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        response = cursor.execute("SELECT id FROM document_note WHERE UPPER(title) LIKE UPPER('%" + searchword + "%')").fetchall()
        #Flaw 4 is fixed by changing the above line to 
        #response = cursor.execute("SELECT id FROM document_note WHERE UPPER(title) LIKE UPPER(?)", ["'%" + searchword + "%'"]).fetchall()

        #You can try searching for these to see the effect
        #aaa%') UNION SELECT password FROM auth_user WHERE username='admin' or email LIKE UPPER('%aaa
        #aaa%') UNION SELECT username FROM auth_user WHERE id = (SELECT owner_id FROM document_note WHERE title='Hello to you too!') or email LIKE UPPER('%aaa

        aslist = list(response)
        searched_notes = [id[0] for id in aslist]
   

    request.session['search'] = searched_notes

    return redirect('/?docid=0')
    #return render(request, 'editor.html', context)



# create delete notes page
@login_required(login_url='/login/')
def delete_note(request, docid):
    note = Note.objects.get(pk=docid)
    note.delete()
 
    return redirect('/?docid=0')
 
 
# login page for user
def login_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_obj = User.objects.filter(username=username)
            if not user_obj.exists():
                messages.error(request, "Username not found")
                return redirect('/login/')
            user_obj = authenticate(username=username, password=password)
            if user_obj:
                login(request, user_obj)
                return redirect('editor')
            messages.error(request, "Wrong Password")
            return redirect('/login/')
        except Exception as e:
            messages.error(request, "Something went wrong")
            return redirect('/register/')
    return render(request, "login.html")
 
 
# register page for user
def register_page(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_obj = User.objects.filter(username=username)
            if user_obj.exists():
                messages.error(request, "Username is taken")
                return redirect('/register/')
            user_obj = User.objects.create(username=username)
            user_obj.set_password(password)
            user_obj.save()
            messages.success(request, "Account created")
            return redirect('/login')
        except Exception as e:
            messages.error(request, "Something went wrong")
            return redirect('/register')
    return render(request, "register.html")
 
 
# logout function
def custom_logout(request):
    logout(request)
    return redirect('login')
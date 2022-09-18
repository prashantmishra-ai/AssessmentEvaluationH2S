from curses.ascii import HT
from django.http import HttpResponse
from django.shortcuts import render,redirect
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['report']
question = 'NA'
answer = 'NA'
def teacherLogin(request):
    if request.POST:
        teacherId = request.POST.get('regno')
        password = request.POST.get('password')
        if(teacherId == 'admin' and password == 'teacher_admin'):
            return render(request, 'postquestion.html')
        return HttpResponse("<script>alert('Unauthorized User');</script>")
    else:
        return render(request, 'teacherlogin.html')
def postquestion(request):
    if request.POST:
        global question
        global answer
        received_data = request.POST
        print(received_data)
        question = request.POST.getlist('question')
        answer = request.POST.getlist('answer')
        print(len(question))
        collection = db['qans']
        for i in range(len(question)):
            res={}
            res[question[i]] = answer[i]
            collection.insert_one(res)
        print(res)
        qnas = {
            'question' : question,
            'answer' : answer
        }
        # collection.insert_one(qnas)
        return HttpResponse("Question Posted Successfully")
    else :
        return redirect('/teacherlogin')
def index(request):
    if request.POST:
        regno = request.POST.get('regno')
        password = request.POST.get('password')
        collection = db['studentinfo']
        usercheck = collection.find_one({'regno':regno})
        if usercheck:
            if (usercheck['password']== password):
                global question
                context = {
                    'newquestion' : question,
                    'regno' : regno,
                    'username' : usercheck['name']
                }
                return render(request, 'index2.html', context)
            else:
                context = {
                    'message' : 'Password Incorrect'
                }
                return render(request, 'index.html', context )
        else:
            return HttpResponse("User Doesn't Exist")
    return render(request, 'index.html')
def showresponses(request):
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    collection = db['score']
    collection2 = db['qans']
    student_details = []
    qnas_details = []
    student_data = collection.find({})
    qnas_data = collection2.find({})
    for i in student_data:
        student_details.append(i)
    for j in qnas_data:
        qnas_details.append(j)
    context = {
        'data' : student_details,
        'qdata' : qnas_details
    }
    print(student_details)
    print(context)
    return render(request,'studentrespon.html',context)
def register(request):
    if request.POST:
        regno = request.POST.get('regno')
        password = request.POST.get('password')
        name = request.POST.get('name')
        collection = db['studentinfo']
        usercheck = collection.find_one({'regno':regno})
        if(usercheck):
            context = {'message' : 'User All ready Present'}
            return render(request, 'register.html', context)
        studentdetails = {
            'regno' : regno,
            'password' : password,
            'name' : name
        }
        collection.insert_one(studentdetails)
        context = {'message' : 'User Registered Successfully'}
        return render(request, 'register.html', context)
    return render(request, 'register.html')
def submit(request):
    if request.POST:
        regno = request.POST.get('student')
        student_answer = request.POST.get('answer')
        # print('Importing Spacy')
        import spacy
        db = client['report']
        collection = db['score']
        # print('loading en_core_web_lg')
        nlp = spacy.load('en_core_web_lg')
        answer1 = nlp(answer)
        # print('Printing and Comparing')
        answer2=nlp(student_answer)
        def text_processing(text):
            doc = nlp(text)
            result = []
            for token in doc:
                if token.text in nlp.Defaults.stop_words:
                    continue
                if token.is_punct:
                    continue
                if token.lemma_ == '-PRON-':
                    continue
                result.append(token.lemma_)
            return " ".join(result)
        def check_Score(text1, text2):
            teacher_answer = nlp(text_processing(text1))
            student_answer = nlp(text_processing(text2))
            return teacher_answer.similarity(student_answer)
        # print(check_Score(answer1,answer2))
        global question
        print(answer)
        score_details = {
            "student" : regno,
            "marks" : check_Score(answer1,answer2)*10,
            "question" : question,
            "answer" : student_answer
        }
        collection.insert_one(score_details)
        return render(request, 'submit.html', score_details)
    else:
        return HttpResponse("Access Denied")

def edit_delete(request):
    return render('edit_delete.html')
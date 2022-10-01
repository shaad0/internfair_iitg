from django.contrib.auth import login, logout,authenticate
from django.shortcuts import redirect, render
from django.views import View
from .forms  import *
from django.http import HttpResponse
from django.views.generic import CreateView
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from recruiter.models import *
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    return render(request, "home.html")

def team(request):
    return render(request, "team.html")


def student(request):
    if request.user.is_authenticated:
        if request.user.is_student:
            return HttpResponseRedirect(reverse('StudentProfile',kwargs={'pk': request.user.id}))
        else:
            return render(request, "StudentLanding.html")
    else:
        return render(request, "StudentLanding.html")

def contact(request):
    return render(request, "contact.html")

class StudentRegistration(CreateView):
    model = User
    form_class = StudentsForm
    template_name = './StudentRegistration.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)



    def form_valid(self, form):
        givenemail = str(form.cleaned_data.get('IITG_webmail'))
        givenid = str(form.cleaned_data.get('Udgam_transaction_id'))
        roll_number = str(form.cleaned_data.get('roll_number'))
        # print(givenemail)
        iitgmail = "iitg.ac.in"
        trxn = "MOJO"
        if iitgmail.upper() in givenemail.upper() :
            if trxn.upper() in givenid.upper() and len(givenid)==20:
                if roll_number[:2]=='19' or roll_number[:2]=='20':
                    user = form.save()
                    login(self.request, user)
                    return HttpResponseRedirect(reverse('StudentProfile',kwargs={'pk': user.id}))
                else:
                    messages.info(self.request, 'Sorry, you are not eligible for Intern Fair')
                    return redirect('StudentRegistration')
            else:
                messages.info(self.request, 'Invalid Payment Id')
                return redirect('StudentRegistration')

        else:
            messages.info(self.request, 'Please Enter IITG webmail only.')
            return redirect('StudentRegistration')



class StartUpsRegistration(CreateView):
    model = User
    form_class = StartUpsForm
    template_name = 'recruiter/RecruiterRegistration.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'startup'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect(reverse('recruiter:Profile',kwargs={'pk': user.id}))

@login_required
def StudentProfile(request,**kwargs):

    user = Students.objects.get(user=request.user)
    registered_internships = InternApplication.objects.filter(Intern__id = user.pk)
    # print(registered_internships)
    return render(request, "StudentProfile1.html",{'student':user,'interns':registered_internships})


def studentLogin(request):

    if request.method == 'POST':
        username = request.POST.get('Username')
        password = request.POST.get('Password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_student:
                if user.is_active:
                    login(request,user)
                    return HttpResponseRedirect(reverse('StudentProfile',kwargs={'pk': user.id}))
                else:
                    return render(request, "StudentLanding.html",{'error':'User is flagged Inactive. Drop mail to internfair@udgam-iitg.in to reactivate your account'})
                # return redirect('/student/profile',kwargs={'pk': user.id})
            else:
                return render(request, "StudentLanding.html",{'error':'Invalid login details entered. If you are a recruiter, login at recruiter page.'})
        else:
            return render(request, "StudentLanding.html",{'error':'Invalid login details entered.'})
            # return redirect('/', {'error':'Invalid login details given, If you are a recruiter, login at recruiter page.'})
    else:
        return redirect('/student')

def startupLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_startup:
                if user.is_active:
                    login(request,user)
                    return HttpResponseRedirect(reverse('recruiter:Profile',kwargs={'pk': user.id}))
                    return redirect('../recruiter/profile')
                else:
                    return render(request, "recruiter/RecruiterLanding.html",{'error':'User is flagged Inactive. Drop mail to internfair@udgam-iitg.in to reactivate your account'})
            else:
                return render(request, "recruiter/RecruiterLanding.html",{'error':'Invalid login details entered. If you are a student, login at student page.'})

                # return redirect('../recruiter',{'error':'User is flagged Inactive. Drop mail to internfair@udgam.in to reactivate your account'})
        else:
            return render(request, "recruiter/RecruiterLanding.html",{'error':'Invalid login details entered.'})

            # return redirect('../recruiter',{'error':'Invalid login details given. If you are a student, loginin at student page.'})
    else:
        return redirect('../recruiter')



@login_required
def AvailableInternships(request):
    if request.method == "POST":
        # print(request.POST)
        student = Students.objects.get(user=request.user)
        startup = request.POST["startup"]
        profile = request.POST["profile"]
        id = request.POST['id']
        internship = Intern_form.objects.get(pk=id)
        answers  = request.POST.getlist("answers")
        CV  = request.POST["CV"]
        app_count = student.intern_count
        if app_count < 5  :
            student.intern_count = app_count + 1
            student.save()
            app = InternApplication.objects.create(Intern=student,Internship = internship, Intern_name= student.name,
            Intern_email= student.email, Intern_contact= student.contact, Startup_name = internship.startup.companyName,
            Startup_profile= internship.profile, Answers=answers,CV = CV)
            # app = [student.name,startup,profile,internship,answers]
            messages.success(request, f'You have successfully applied for internship in {internship.startup.companyName} for  {profile} profile  ', '')
        else:
            messages.error(request, 'You have already applied for 5 Internships. You cannot apply for more. ','')

        return redirect('StudentProfile')



    else:
        available_internships = Intern_form.objects.filter(FormStatus="ACTIVE").order_by('profile')
        startupName = []

        for x in available_internships:
            y= x.startup.companyName
            if y not in startupName:
                startupName.append(y)

        template = "AvailableInternships.html"
        context = {'interns': available_internships, 'startupName': startupName}
        return render(request, template, context)


@login_required
def EditStudProfile(request, **kwargs):
    current_user = request.user
    student = Students.objects.get(user=current_user)
    if request.method=='POST':
        if request.POST['roll_number']:
            student.roll_number = request.POST['roll_number']
        if request.POST['department']:
            student.department = request.POST['department']
        if request.POST['bio']:
            student.bio = request.POST['bio']
        student.save()
    return HttpResponseRedirect(reverse('StudentProfile',kwargs={'pk': current_user.id}))







@login_required
def logout_view(request):
    logout(request)
    return redirect( 'student')

@login_required
def delete_app(request,**kwargs):
    # print(kwargs)
    id = kwargs['pk']
    student = Students.objects.get(user = request.user)
    # print(student)
    intern_app = InternApplication.objects.get(pk = id)
    intern_app.delete()
    student.intern_count=student.intern_count-1
    student.save()

    # print(intern_app)


    return HttpResponseRedirect(reverse('StudentProfile',kwargs={'pk': student.id}))



def intern_app_count(student):
    count = InternApplication.objects.filter(Intern__id= student.id).count()
    # print(count)
    return count


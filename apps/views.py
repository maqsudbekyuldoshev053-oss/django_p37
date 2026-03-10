from django.shortcuts import  get_object_or_404
from django.shortcuts import render, redirect
from .models import Student, University


def student_list_page(request):
    query = request.GET.get('q', '')  # qidiruv so‘rovi
    if query:
        students = Student.objects.filter(
            first_name__icontains=query
        ) | Student.objects.filter(
            last_name__icontains=query
        ) | Student.objects.filter(
            university__name__icontains=query
        )
    else:
        students = Student.objects.all()
    return render(request, 'project_apps/student_list_page.html', {'students': students, 'query': query})



def student_detail_page(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        student.first_name = request.POST.get('first_name')
        student.last_name = request.POST.get('last_name')
        student.phone = request.POST.get('phone')
        student.birth_date = request.POST.get('birth_date')
        student.save()
        return redirect('student_list_page')


    context = {
        'student': student,
    }
    return render(request, 'project_apps/student_detail_page.html', context)


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        return redirect('student_list_page')  # student list page nomi bilan mos
    return render(request, 'project_apps/student_confirm_delete.html', {'student': student})



def student_add_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        birth_date = request.POST.get('birth_date')
        university_id = request.POST.get('university')

        Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date,
            university_id=university_id
        )
        return redirect('student_list_page')

    context = {
        'universities': University.objects.all()
    }
    return render(request, 'project_apps/student_add_page.html', context)
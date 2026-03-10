from django.urls import path
from apps.views import student_list_page, student_detail_page, student_delete, student_add_page

urlpatterns = [
    path('', student_list_page, name='student_list_page'),
    path('student-detail/<int:pk>/', student_detail_page, name='student_detail_page'),
    path('student/<int:pk>/delete/', student_delete, name='student_delete'),
    path('student/add', student_add_page, name='student_add'),
]

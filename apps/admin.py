import csv

from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path
from django import forms

from apps.models import University, Student


# -------yangi admin yaratish
# class EventAdminSite(AdminSite):
# site_header = "UMSRA Events Admin"
# site_title = "UMSRA Events Admin Portal"
# index_title = "Welcome to UMSRA Researcher Events Portal"


# event_admin_site = EventAdminSite(name='event_admin')


# -------Modellarni yangi admin panelga register qilish
# event_admin_site.register(Epic)
# event_admin_site.register(Event)
# event_admin_site.register(EventHero)
# event_admin_site.register(EventVillain)
# -------------------------------------


# -------- Agar siz faqat admin sahifasidagi yozuvlarni o‘zgartirmoqchi bo‘lsangiz:
# admin.site.site_header = "UMSRA Admin"
# admin.site.site_title = "UMSRA Admin Portal"
# admin.site.index_title = "Welcome to UMSRA Researcher Portal"

# -------- Keraksiz modellani admin paneldan olib tashlash
# admin.site.unregister(User)
# admin.site.unregister(Group)


# ---------------- CSV Import Form ----------------
class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


# ---------------- Custom Filter ----------------
class BigUniversityFilter(admin.SimpleListFilter):
    title = "Big university"
    parameter_name = "big_university"

    def lookups(self, request, model_admin):
        return (
            ("Yes", "Yes"),
            ("No", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "Yes":
            return queryset.annotate(
                student_count=Count("student", distinct=True)
            ).filter(student_count__gt=1000)
        if self.value() == "No":
            return queryset.annotate(
                student_count=Count("student", distinct=True)
            ).filter(student_count__lte=1000)
        return queryset


# ---------------- CSV Export Mixin ----------------
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'

        writer = csv.writer(response)
        writer.writerow(field_names)

        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


# ---------------- University Admin ----------------
@admin.register(University)
class UniversityModelAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = [
        'id', 'name', 'is_active', 'established_year', 'address', 'student_count', 'big_university']
    list_filter = (BigUniversityFilter,)
    actions = ["mark_immortal", "export_as_csv"]
    change_list_template = "apps/universities_changelist.html"

    # ----- Custom URLs -----
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('immortal/', self.set_immortal),
            path('mortal/', self.set_mortal),
        ]
        return my_urls + urls

    def set_immortal(self, request):
        self.model.objects.all().update(is_active=True)
        self.message_user(request, "All heroes are now immortal")
        return HttpResponseRedirect("../")

    def set_mortal(self, request):
        self.model.objects.all().update(is_active=False)
        self.message_user(request, "All heroes are now mortal")
        return HttpResponseRedirect("../")

    # ----- Custom Actions -----
    def mark_immortal(self, request, queryset):
        queryset.update(is_immortal=True)
        self.message_user(request, f"{queryset.count()} hero marked as immortal.")

    # ----- Remove delete action -----
    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    # ----- Annotate queryset with student count -----
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_student_count=Count("student", distinct=True))

    # ----- Display student count -----
    def student_count(self, obj):
        return obj._student_count

    student_count.admin_order_field = "_student_count"
    student_count.short_description = "Students"

    # ----- Display big university boolean -----
    def big_university(self, obj):
        return obj._student_count > 1000

    big_university.boolean = True
    big_university.short_description = "Big university"


# ---------------- Student Admin ----------------
@admin.register(Student)
class StudentModelAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'phone', 'birth_date']
    actions = ["export_as_csv"]
    change_list_template = "apps/students_changelist.html"

    # ----- Custom URLs -----
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    # ----- CSV Import -----
    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            reader = csv.reader(csv_file)
            # TODO: Create Student objects from CSV
            self.message_user(request, "Your CSV file has been imported")
            return redirect("..")

        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)

    # ----- Remove delete action -----
    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
import csv
from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.models import University, Student, Course, File, Image
from datetime import datetime

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
    def export_as_csv(self, queryset):
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
    list_display = ['id', 'name', 'is_active', 'established_year', 'address', 'student_count', 'big_university']
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


    # ----- Display student count -----

    @admin.display(description="Students")
    def student_count(self, obj):
        return obj.student_set.count


    # ----- Display big university boolean -----
    @admin.display()
    def big_university(self, obj):
        return obj.studebt_set.count > 1

    big_university.boolean = True
    big_university.short_description = "Big university"



class FileStackedInline(admin.StackedInline):
    model = File
    min_num = 1
    extra = 2
    max_num = 3
    can_delete = False

# ---------------- Student Admin ----------------
@admin.register(Student)
class StudentModelAdmin(ExportCsvMixin, admin.ModelAdmin):
    list_display = ['phone', 'birth_date_with_days', 'passport', 'get_courses', 'img_preview']
    # date_hierarchy = 'added_on'
    list_per_page = 50
    search_fields = ('first_name', 'phone')
    inlines = [FileStackedInline]
    readonly_fields = ('img_preview',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "courses":  # Student modelidagi M2M field nomi
            kwargs["queryset"] = Course.objects.filter(name__in=['IT', 'English'])
        return super().formfield_for_manytomany(db_field, request, **kwargs)


    @admin.display(description="Birth Date")
    def birth_date_with_days(self, obj):
        today = datetime.now().date()
        birth = obj.birth_date

        next_birthday = birth.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        days_left = (next_birthday - today).days
        birth_str = birth.strftime("%Y:%m:%d")
        return f"{birth_str} ({days_left} kun qoldi)"


    @admin.display(description= "Passport")
    def passport(self, obj):
        return f"{obj.passport_series}{obj.passport_number}"


    @admin.display(description="Courses")
    def get_courses(self, obj):
        return ", ".join(obj.courses.values_list("name", flat=True))

    @admin.display(description="Photo")
    def img_preview(self, obj):
        if obj.image and obj.image.headshot:
            return format_html('<img src="{}" width="60" style="border-radius:4px;" />', obj.image.headshot.url)
        return "No Image"



    # actions = ["export_as_csv"]
    # change_list_template = "apps/students_changelist.html"

    # ----- Custom URLs -----
    # def get_urls(self):
    #     urls = super().get_urls()
    #     my_urls = [
    #         path('import-csv/', self.import_csv),
    #     ]
    #     return my_urls + urls
    #
    # # ----- CSV Import -----
    # def import_csv(self, request):
    #     if request.method == "POST":
    #         csv_file = request.FILES["csv_file"]
    #         reader = csv.reader(csv_file)
    #         # TODO: Create Student objects from CSV
    #         self.message_user(request, "Your CSV file has been imported")
    #         return redirect("..")
    #
    #     form = CsvImportForm()
    #     payload = {"form": form}
    #     return render(request, "admin/csv_form.html", payload)
    #
    # # ----- Remove delete action -----
    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if "delete_selected" in actions:
    #         del actions["delete_selected"]
    #     return actions


@admin.register(Course)
class CourseModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'student_count']

    @admin.display(description='Number of Students')
    def student_count(self, obj):
        return obj.student_set.count()



@admin.register(Image)
class ImageModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'img']

    readonly_fields = ('img',)

    @admin.display(description="Image")
    def img(self, obj):
        if obj.headshot:
            return mark_safe(f'<img src="{obj.headshot.url}" width="120"/>')
        return "No Image"

from django.db.models import Model, ForeignKey, CASCADE, ManyToManyField, FileField, ImageField
from django.db.models.fields import CharField, IntegerField, DateField, BooleanField


class University(Model):
    name = CharField(max_length=255)
    established_year = IntegerField(default=0)
    address = CharField(max_length=255)
    is_active = BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Universities"

    def __str__(self):
        return self.name


class Student(Model):
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    phone = CharField(max_length=255)
    birth_date = DateField(default=0)
    passport_number = CharField(max_length=7)
    passport_series = CharField(max_length=2)
    university = ForeignKey("apps.University", CASCADE)
    courses = ManyToManyField("apps.Course", blank=True)
    image = ForeignKey('apps.Image', on_delete=CASCADE, null=True, blank=True)

    def __str__(self):
        return self.first_name

    class Meta:
        unique_together = (
            ("passport_number", "passport_series"),
        )


class Course(Model):
    name = CharField(max_length=255)
    price = IntegerField(default=0)

    def __str__(self):
        return self.name


class File(Model):
    image = FileField(upload_to='news/%Y/%m/d')
    news = ForeignKey('apps.Student', CASCADE, related_name='files')


class Image(Model):
    name = CharField(max_length=100)
    headshot = ImageField(null=True, blank=True, upload_to="hero_headshots/")

    def __str__(self):
        return self.name



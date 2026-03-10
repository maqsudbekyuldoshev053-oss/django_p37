from django.db.models import Model, ForeignKey, CASCADE
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
    university = ForeignKey("apps.University", CASCADE)

    def __str__(self):
        return self.first_name

# django jinjada kod yozyapman student list html kodini yozib ber hamma narsa listni urtasida chiqsin

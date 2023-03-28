from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length=30)
    students = models.ManyToManyField(User, blank=True)
    gives_atar_bonus = models.BooleanField(null=True)

    def __str__(self):
        return self.name

class Class(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    students = models.ManyToManyField(User, blank=True)
    code = models.CharField(max_length=30)
    teacher = models.CharField(max_length=30)
    people = models.IntegerField(null=True)
    description = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = "classes"

class Test(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200, null=True)
    marks_out_of = models.IntegerField()
    weighting = models.DecimalField(decimal_places=2, max_digits=5)
    order = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    has_happened = models.BooleanField(null=True)
    is_exam = models.BooleanField(null=True)

    def __str__(self):
        return self.name

class Mark(models.Model):
    value = models.IntegerField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.student.username) + ", " + str(self.test) + " : " + str(self.value)

class Average(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    value = models.DecimalField(decimal_places=10,max_digits=13)

    def __str__(self):
        return str(self.subject) + " " + str(self.student) + " " + str(self.value)

class Rank(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    value = models.IntegerField()

    def __str__(self):
        return str(self.subject) + " " + str(self.student) + " " + str(self.value)







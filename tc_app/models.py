from django.db import models


from django.contrib.auth.models import AbstractUser

from django.conf import settings
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)


class Student(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True,blank=True)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    serial_no = models.CharField(max_length=20)
    admission_no = models.CharField(max_length=20)

    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=50)
    religion_caste = models.CharField(max_length=100)
    community = models.CharField(max_length=20)
    sex = models.CharField(max_length=10)

    dob = models.CharField(max_length=50)
    admission_date = models.CharField(max_length=50)

    identification_mark1 = models.CharField(max_length=100)
    identification_mark2 = models.CharField(max_length=100)

    branch_sem = models.CharField(max_length=100)
    promotion = models.CharField(max_length=50)
    fees_paid = models.CharField(max_length=50)
    scholarship = models.CharField(max_length=50)
    medium = models.CharField(max_length=50)
    conduct = models.CharField(max_length=50)

    tc_issue_date = models.CharField(max_length=50)
    leaving_date = models.CharField(max_length=50)
    declaration_date = models.CharField(max_length=50)
    def __str__(self):
        return self.name
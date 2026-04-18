import pandas as pd
from django.shortcuts import render,get_object_or_404
from .models import Student
from django.contrib.auth.decorators import login_required


from django.template.loader import get_template

from django.http import HttpResponse
from .models import Student

from django.contrib.auth import authenticate, login,logout
from django.shortcuts import redirect

from django.contrib.auth.models import User


from django.conf import settings
import os


from django.db.models import Q

from django.contrib import messages

@login_required
def upload_excel(request):
    
    if request.user.role == 'user':
        return HttpResponse("Unauthorized", status=403)
    if request.method == "POST":
        file = request.FILES['file']
        df = pd.read_excel(file)

        for _, row in df.iterrows():
            Student.objects.create(
                serial_no=row['serial_no'],
                admission_no=row['admission_no'],
                name=row['name'],
                father_name=row['father_name'],
                nationality=row['nationality'],
                religion_caste=row['religion_caste'],
                community=row['community'],
                sex=row['sex'],
                dob=row['dob'],
                admission_date=row['admission_date'],
                identification_mark1=row['mark1'],
                identification_mark2=row['mark2'],
                branch_sem=row['branch'],
                promotion=row['promotion'],
                fees_paid=row['fees'],
                scholarship=row['scholarship'],
                medium=row['medium'],
                conduct=row['conduct'],
                tc_issue_date=row['tc_issue'],
                leaving_date=row['leaving'],
                declaration_date=row['declaration_date']
            )

        return render(request, "upload.html")

    return render(request, "upload.html")


@login_required
def student_list(request):
    if request.user.role not in ['admin', 'staff']:
        return HttpResponse("Unauthorized", status=403)
    query = request.GET.get('q')

    if query:
        students = Student.objects.filter(
            Q(name__icontains=query) |
            Q(admission_no__icontains=query) |
            Q(branch_sem__icontains=query)
        )
    else:
        students = Student.objects.all()

    return render(request, "student_list.html", {"students": students})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST.get('role')

        # ✅ Check existing user
        if User.objects.filter(username=username).exists():
            messages.error(request, f"{username} already exists. Try another username.")
            return redirect('register')

        # ✅ Create user
        User.objects.create_user(
            username=username,
            password=password,
            role=role
        )

        messages.success(request, "Account created successfully!")
        return redirect('/')

    return render(request, 'register.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        print(username, password)

        user = authenticate(request, username=username, password=password)

        if user is None:
            return HttpResponse("<h1>Username or Password is incorrect</h1>")

        login(request, user)

        # ✅ Correct role + staff check
        if user.role == 'admin':
            return redirect('admin_dashboard')
        elif user.role == 'staff':
            return redirect('staff_dashboard')
        else:
            return redirect('user_dashboard')

    return render(request, 'login.html')





from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.conf import settings
import os

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from django.http import HttpResponse
from django.conf import settings
import os

@login_required
def generate_tc(request, id):

        student = Student.objects.get(id=id)

        if student.status != 'approved':
            return HttpResponse("TC not approved yet!", status=403)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="tc.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4


        # 🔹 LOGO (increased size)
        logo_path = os.path.join(settings.BASE_DIR, 'tc_app/static/images/logo.png')
        p.drawImage(logo_path, 60, height - 120, width=90, height=90)

        # 🔹 HEADER
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width/2, height - 40,
            "ST. JOSEPH’S COLLEGE (ARTS & SCIENCE)")

        p.setFont("Times-Roman", 10)
        p.drawCentredString(width/2, height - 55, "MANAGED BY SISTERS OF DMI")
        
        p.drawCentredString(width/2, height - 68,
            "Affiliated to University of Madras, Accredited by NAAC with “A” Grade")
        p.drawCentredString(width/2, height - 81,
            "2(f) Status of UGC Act, 1956  ISO 21001 : 2018 Certified Institution")
        p.drawCentredString(width/2, height - 94,
            "Kundrathur Main Road, Kovur, Chennai – 600 128")

        # 🔹 TITLE
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width / 2, height - 130, "TRANSFER CERTIFICATE")
        p.line(width/2 - 100, height - 135, width/2 + 100, height - 135)
    
        # 🔹 SERIAL + ADMISSION
        p.setFont("Helvetica", 10)
        p.drawString(40, height - 130, "SERIAL No :")
        p.setFont("Times-Italic", 10)
        p.drawString(120, height - 130, str(student.serial_no))

        y_pos = height - 110

        # 🔹 VALUE (right aligned, italic)
        p.setFont("Times-Italic", 10)
        value_text = str(student.admission_no)
        value_width = p.stringWidth(value_text, "Times-Italic", 10)

        p.drawRightString(width - 90, y_pos, value_text)

        # 🔹 LABEL (normal, placed before value)
        p.setFont("Helvetica", 10)
        label_text = "ADMISSION No : "
        label_width = p.stringWidth(label_text, "Helvetica", 10)

        p.drawString(width - 100 - value_width - label_width, y_pos, label_text)

        # 🔹 START Y
        y = height - 150

        # 🔹 STYLES
        label_style = ParagraphStyle(
            'label',
            fontName='Helvetica',
            fontSize=10,
            leading=12
        )

        value_style = ParagraphStyle(
            'value',
            fontName='Times-Italic',
            fontSize=10,
            leading=12
        )

        def draw_line(label, value, is_name=False, is_bold=False):
            nonlocal y

            label_x = 40
            colon_x = 300
            value_x = 315
            max_width = width - 360

            # Label
            label_para = Paragraph(label, label_style)
            lw, lh = label_para.wrap(colon_x - label_x - 30, 100)
            label_para.drawOn(p, label_x, y - lh + 5)

            # Colon
            p.setFont("Helvetica", 10)
            p.drawString(colon_x, y, ":")

            # 🔹 VALUE STYLE CONTROL
            if is_name:
                v_style = ParagraphStyle(
                    'name_style',
                    fontName='Times-Bold',
                    value=value.upper(),    
                    fontSize=11,
                    leading=12
                )
                value = value.upper() 

            elif is_bold:
                v_style = ParagraphStyle(
                    'bold_style',
                    fontName='Times-Bold',
                    fontSize=10,
                    leading=12
                )

            else:
                v_style = ParagraphStyle(
                    'normal_style',
                    fontName='Times-Italic',
                    fontSize=10,
                    leading=12
                )

            # Value
            value_para = Paragraph(str(value), v_style)
            vw, vh = value_para.wrap(max_width, 100)
            value_para.drawOn(p, value_x, y - vh + 5)

            # Underline
            p.line(value_x, y - vh, width - 40, y - vh)

            y -= max(lh, vh) + 12
                
        y -= 15
        # 🔹 FIELDS
        draw_line("1. Name of the student (in BLOCK LETTERS)", student.name, is_name=True)

        draw_line("2. Name of the Father / Guardian", student.father_name)
        draw_line("3. Nationality, Religion and Caste", student.religion_caste)
        draw_line("4. Community : OC / BC / MBC / SC / ST", student.community)
        draw_line("5. Sex", student.sex)

        draw_line(
            "6. Date of Birth as entered in the admission<br/>Register in figures & words",
            student.dob
        )

        draw_line("7. Date of Admission & Class in which admitted", student.admission_date)

        # Identification continues...

        draw_line(
            "9. Branch / Semester in which the Students was<br/>Studying at the time of leaving",
            student.branch_sem,
            is_bold=True   # ✅ bold
        )

        draw_line("10. Whether qualified for promotion to higher studies", student.promotion)
        draw_line("11. Whether the student has paid all the fees", student.fees_paid)
        draw_line("12. Whether the student was in receipt of any Scholarship", student.scholarship)
        draw_line("13. Medium of instruction", student.medium)

        draw_line(
            "14. Conduct and Character",
            student.conduct,
            is_bold=True   # ✅ bold
        )

        draw_line("15. Date of the Transfer Certificate issued", student.tc_issue_date)
        draw_line("16. Date on which the student left", student.leaving_date)
                # 🔹 1 INCH SPACE BEFORE SIGNATURE
        y -= 15

        # 🔹 SEAL + PRINCIPAL
        p.setFont("Helvetica-Bold",10)
        p.drawString(50, y, "Seal")
    
        p.setFont("Helvetica-Bold", 10)
        p.drawRightString(width - 60, y, "PRINCIPAL")
        y -= 25
        # 🔹 NOTES TITLE WITH UNDERLINE
        note_y = 140
        decl_y = 90
        date_y = 50
        p.setFont("Helvetica", 10)

        p.drawString(40, y, "Note:")

        # underline
        p.line(40, y - 2, 72, y - 2)   # adjust end (75) if needed

        y -= 22
        p.drawString(40, y,
            "a. Erasures and unauthenticated or fraudulent alterations in the certificate will lead to it's cancellation.")
        y -= 14
        p.drawString(40, y,
            "b. Should be signed in ink by the principal who will be held responsible for the correctness entries.")

        # 🔹 DECLARATION (EXACT CONTENT)
        y -= 25
        p.setFont("Helvetica-Bold", 10)

        text = "Declaration by the student:"
        
        p.drawString(40, y, text)
        p.setFont("Helvetica", 10)
        text_width = p.stringWidth(text, "Helvetica", 10)

        p.line(40, y - 2, 40 + text_width, y - 2)
        y -= 22
        p.drawString(40, y,
            "I hereby declare that the particulars recorded against items 1 to 8 are correct and that no change will be demanded by me in")
        y -= 12
        p.drawString(40, y, 
            "future.")

        y -= 23
        y_pos = y

        # 🔹 VALUE (italic)
        p.setFont("Times-Italic", 10)
        value_text = str(student.declaration_date)
        value_width = p.stringWidth(value_text, "Times-Italic", 10)

        p.drawString(80, y_pos, value_text)

        # 🔹 LABEL (bold)
        p.setFont("Helvetica-Bold", 10)
        label_text = "Date :"
        p.drawString(40, y_pos, label_text)

        # 🔹 SIGNATURE (right side)
        p.setFont("Helvetica-Bold", 10)
        p.drawRightString(width - 40, y_pos, "Signature of the Student")

        p.showPage()
        p.save()

        return response

    
import zipfile
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

@login_required
def bulk_tc(request):

    ids = request.POST.getlist('student_ids')

    if request.user.role == 'user':
        return HttpResponse("Unauthorized", status=403)

    students = Student.objects.filter(id__in=ids, status='approved')

    if not students:
        return HttpResponse("No approved records selected!")

    zip_buffer = BytesIO()
    zip_file = zipfile.ZipFile(zip_buffer, 'w')

    for student in students:

        pdf_buffer = BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4



        # 🔹 LOGO (increased size)
        logo_path = os.path.join(settings.BASE_DIR, 'tc_app/static/images/logo.png')
        p.drawImage(logo_path, 60, height - 120, width=90, height=90)

        # 🔹 HEADER
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width/2, height - 40,
            "ST. JOSEPH’S COLLEGE (ARTS & SCIENCE)")

        p.setFont("Times-Roman", 10)
        p.drawCentredString(width/2, height - 55, "MANAGED BY SISTERS OF DMI")
        
        p.drawCentredString(width/2, height - 68,
            "Affiliated to University of Madras, Accredited by NAAC with “A” Grade")
        p.drawCentredString(width/2, height - 81,
            "2(f) Status of UGC Act, 1956  ISO 21001 : 2018 Certified Institution")
        p.drawCentredString(width/2, height - 94,
            "Kundrathur Main Road, Kovur, Chennai – 600 128")

        # 🔹 TITLE
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width / 2, height - 130, "TRANSFER CERTIFICATE")
        p.line(width/2 - 100, height - 135, width/2 + 100, height - 135)
    
        # 🔹 SERIAL + ADMISSION
        p.setFont("Helvetica", 10)
        p.drawString(40, height - 130, "SERIAL No :")
        p.setFont("Times-Italic", 10)
        p.drawString(120, height - 130, str(student.serial_no))

        y_pos = height - 110

        # 🔹 VALUE (right aligned, italic)
        p.setFont("Times-Italic", 10)
        value_text = str(student.admission_no)
        value_width = p.stringWidth(value_text, "Times-Italic", 10)

        p.drawRightString(width - 90, y_pos, value_text)

        # 🔹 LABEL (normal, placed before value)
        p.setFont("Helvetica", 10)
        label_text = "ADMISSION No : "
        label_width = p.stringWidth(label_text, "Helvetica", 10)

        p.drawString(width - 100 - value_width - label_width, y_pos, label_text)

        # 🔹 START Y
        y = height - 150

        # 🔹 STYLES
        label_style = ParagraphStyle(
            'label',
            fontName='Helvetica',
            fontSize=10,
            leading=12
        )

        value_style = ParagraphStyle(
            'value',
            fontName='Times-Italic',
            fontSize=10,
            leading=12
        )

        def draw_line(label, value, is_name=False, is_bold=False):
            nonlocal y

            label_x = 40
            colon_x = 300
            value_x = 315
            max_width = width - 360

            # Label
            label_para = Paragraph(label, label_style)
            lw, lh = label_para.wrap(colon_x - label_x - 30, 100)
            label_para.drawOn(p, label_x, y - lh + 5)

            # Colon
            p.setFont("Helvetica", 10)
            p.drawString(colon_x, y, ":")

            # 🔹 VALUE STYLE CONTROL
            if is_name:
                v_style = ParagraphStyle(
                    'name_style',
                    fontName='Times-Bold',
                    value=value.upper(),    
                    fontSize=11,
                    leading=12
                )
                value = value.upper() 

            elif is_bold:
                v_style = ParagraphStyle(
                    'bold_style',
                    fontName='Times-Bold',
                    fontSize=10,
                    leading=12
                )

            else:
                v_style = ParagraphStyle(
                    'normal_style',
                    fontName='Times-Italic',
                    fontSize=10,
                    leading=12
                )
            # Value
            value_para = Paragraph(str(value), v_style)
            vw, vh = value_para.wrap(max_width, 100)
            value_para.drawOn(p, value_x, y - vh + 5)

            # Underline
            p.line(value_x, y - vh, width - 40, y - vh)

            y -= max(lh, vh) + 12
                
        y -= 15
        # 🔹 FIELDS
        draw_line("1. Name of the student (in BLOCK LETTERS)", student.name, is_name=True)

        draw_line("2. Name of the Father / Guardian", student.father_name)
        draw_line("3. Nationality, Religion and Caste", student.religion_caste)
        draw_line("4. Community : OC / BC / MBC / SC / ST", student.community)
        draw_line("5. Sex", student.sex)

        draw_line(
            "6. Date of Birth as entered in the admission<br/>Register in figures & words",
            student.dob
        )

        draw_line("7. Date of Admission & Class in which admitted", student.admission_date)

        # Identification continues...

        draw_line(
            "9. Branch / Semester in which the Students was<br/>Studying at the time of leaving",
            student.branch_sem,
            is_bold=True   # ✅ bold
        )

        draw_line("10. Whether qualified for promotion to higher studies", student.promotion)
        draw_line("11. Whether the student has paid all the fees", student.fees_paid)
        draw_line("12. Whether the student was in receipt of any Scholarship", student.scholarship)
        draw_line("13. Medium of instruction", student.medium)

        draw_line(
            "14. Conduct and Character",
            student.conduct,
            is_bold=True   # ✅ bold
        )

        draw_line("15. Date of the Transfer Certificate issued", student.tc_issue_date)
        draw_line("16. Date on which the student left", student.leaving_date)
                # 🔹 1 INCH SPACE BEFORE SIGNATURE
        y -= 15

        # 🔹 SEAL + PRINCIPAL
        p.setFont("Helvetica-Bold",10)
        p.drawString(50, y, "Seal")
    
        p.setFont("Helvetica-Bold", 10)
        p.drawRightString(width - 60, y, "PRINCIPAL")
        y -= 25
        # 🔹 NOTES TITLE WITH UNDERLINE
        note_y = 140
        decl_y = 90
        date_y = 50
        p.setFont("Helvetica", 10)

        p.drawString(40, y, "Note:")

        # underline
        p.line(40, y - 2, 72, y - 2)   # adjust end (75) if needed

        y -= 22
        p.drawString(40, y,
            "a. Erasures and unauthenticated or fraudulent alterations in the certificate will lead to it's cancellation.")
        y -= 14
        p.drawString(40, y,
            "b. Should be signed in ink by the principal who will be held responsible for the correctness entries.")

        # 🔹 DECLARATION (EXACT CONTENT)
        y -= 25
        p.setFont("Helvetica-Bold", 10)

        text = "Declaration by the student:"
        
        p.drawString(40, y, text)
        p.setFont("Helvetica", 10)
        text_width = p.stringWidth(text, "Helvetica", 10)

        p.line(40, y - 2, 40 + text_width, y - 2)
        y -= 22
        p.drawString(40, y,
            "I hereby declare that the particulars recorded against items 1 to 8 are correct and that no change will be demanded by me in")
        y -= 12
        p.drawString(40, y, 
            "future.")

        y -= 23
        y_pos = y

        # 🔹 VALUE (italic)
        p.setFont("Times-Italic", 10)
        value_text = str(student.declaration_date)
        value_width = p.stringWidth(value_text, "Times-Italic", 10)

        p.drawString(80, y_pos, value_text)

        # 🔹 LABEL (bold)
        p.setFont("Helvetica-Bold", 10)
        label_text = "Date :"
        p.drawString(40, y_pos, label_text)

        # 🔹 SIGNATURE (right side)
        p.setFont("Helvetica-Bold", 10)
        p.drawRightString(width - 40, y_pos, "Signature of the Student")

        p.showPage()
        p.save()

    

        # 🔹 ADD TO ZIP (IMPORTANT - INSIDE LOOP)
        pdf_buffer.seek(0)
        zip_file.writestr(f"{student.admission_no}.pdf", pdf_buffer.read())

    zip_file.close()

    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="TCs.zip"'

    return response

def tc_template(request):

    return render(request,'tc_template.html')



@login_required
def admin_dashboard(request):
    if request.user.role != 'admin' or not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)

    query = request.GET.get('q')
    branch = request.GET.get('branch')

    students = Student.objects.all()

    #  Search
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(admission_no__icontains=query)
        )

    # Group / Filter (Branch)
    if branch:
        students = students.filter(branch_sem=branch)

    # Counts
    total = students.count()
    pending = students.filter(status='pending').count()
    approved = students.filter(status='approved').count()
    rejected = students.filter(status='rejected').count()

    # Get unique branches for dropdown
    branches = Student.objects.values_list('branch_sem', flat=True).distinct()

    return render(request, "admin_dashboard.html", {
        "students": students,
        "branches": branches,
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
    })


def total_students(request):

    total_users=User.objects.filter(role="user")  
    total_teachers=User.objects.filter(role="staff")
    
    return render(request,'student_list.html',{'total_users':total_users,'total_teachers':total_teachers})

from django.shortcuts import redirect

@login_required
def approve_tc(request, id):
    
    if request.user.role != 'admin' or not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)

    student = Student.objects.get(id=id)
    student.status = 'approved'
    student.save()
    return redirect('/admin-dashboard/')


@login_required
def reject_tc(request, id):
    
    if request.user.role != 'admin':
        return HttpResponse("Unauthorized", status=403)

    student = Student.objects.get(id=id)
    student.status = 'rejected'
    student.save()
    return redirect('/admin-dashboard/')


@login_required
def pending_requests(request):
    
    if request.user.role != 'admin' or not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)

    students = Student.objects.filter(status='pending')

    return render(request, "pending_requests.html", {"students": students})




from django.db.models import Q

@login_required

def staff_dashboard(request):
    
    if request.user.role == 'user':
        return HttpResponse("Unauthorized", status=403)

    query = request.GET.get('q')
    branch = request.GET.get('branch')

    students = Student.objects.all()

    #  Search
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(admission_no__icontains=query)
        )

    # Group / Filter (Branch)
    if branch:
        students = students.filter(branch_sem=branch)

    # Counts
    total = students.count()
    pending = students.filter(status='pending').count()
    approved = students.filter(status='approved').count()
    rejected = students.filter(status='rejected').count()

    # Get unique branches for dropdown
    branches = Student.objects.values_list('branch_sem', flat=True).distinct()

    return render(request, "staff_dashboard.html", {
        "students": students,
        "branches": branches,
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
    })



@login_required
def user_dashboard(request):


    students = Student.objects.filter(user=request.user)
    approved = Student.objects.filter(status='approved').count()
    pending= Student.objects.filter(status='pending').count()
    rejected = Student.objects.filter(status='rejected').count()


    return render(request, "user_dashboard.html", {"students": students,"approved":approved,'pending':pending,'rejected':rejected})

from .forms import SrequestForm

@login_required
def request_tc(request):



    if request.method == "POST":
        request_form = SrequestForm(request.POST)
        if request_form.is_valid():
            obj = request_form.save(commit=False)
            obj.user=request.user
            obj.status = "pending"   #  ensure default
            obj.save()
            messages.success(request,'enter data saved')
        else:
            print(request_form.errors)
            messages.error(request,'enter data didnt save')   #  DEBUG          return redirect('/user-dashboard/')
    else:
        request_form = SrequestForm()   #  important

    return render(request, "request_tc.html", {'request_form': request_form})


def pending(request):
    students = Student.objects.all()
    pending_count = students.filter(status='pending').count()
   
   
    pending=Student.objects.filter(status='pending')

   
    return render(request,'pending.html',{'pending':pending,'pending_count':pending_count})
    

def approved(request):
    students = Student.objects.all()
    approved_count = students.filter(status='approved').count()
    approved=Student.objects.filter(status='approved')

   
    return render(request,'approved.html',{'approved':approved,approved_count:approved_count})


def rejected(request):
    students = Student.objects.all()
    rejected_count = students.filter(status='rejected').count()
    rejected=Student.objects.filter(status='rejected')

   
    return render(request,'rejected.html',{'rejected':rejected,'rejected_count':rejected_count})





def student_delete(request, id):
    get_del = get_object_or_404(Student, id=id)
    get_del.delete()
    return redirect('admin_dashboard')


from django.db.models import Count
def Reports(request):


    data = Student.objects.values('status').annotate(total=Count('id'))

    labels = []
    values = []

    for item in data:
        labels.append(item['status'])
        values.append(item['total'])

    context = {
        'labels': labels,
        'values': values,
    }
    return render(request, 'report.html', context)



def user_logout(request):
    logout(request)
    return redirect('login')
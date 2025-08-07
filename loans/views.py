from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa
from io import BytesIO
from .forms import LoanInquiryForm, HistoryForm, PropertySearchForm, PropertyForm, PropertyInquiryForm, AdsForm, KPRCalculatorForm, ModalKerjaCalculatorForm, MultigunaCalculatorForm
from .models import Property, LoanInquiry, PropertyInquiry, AdsInquiry, PropertyImage
import random


def home(request):
    return render(request, 'home.html')

def loan_inquiry(request, loan_type):
    loan_type_map = {
        'kpr_primary': 'KPR Primary',
        'kpr_secondary': 'KPR Secondary',
        'kredit_investasi': 'Kredit Investasi',
        'multiguna': 'Multiguna',
        'refinancing': 'Refinancing',
        'modal_kerja': 'Modal Kerja',
        'take_over_kpr': 'Take Over KPR',
        'take_over_modal_kerja': 'Take Over Modal Kerja',
        'take_over_multiguna': 'Take Over Multiguna',
        'take_over_jual_beli': 'Take Over Jual Beli',
        'jaminan_bpkb': 'Jaminan BPKB',
        'jaminan_alat_berat': 'Jaminan Alat Berat',
        'invoice_financing': 'Invoice Financing',
        'po_financing': 'PO Financing',
        'spk_financing': 'SPK Financing',
        'bridging_offering_letter': 'Bridging Offering Letter',
    }

    formatted_loan_type = loan_type_map.get(loan_type, loan_type.replace('_', ' ').title())

    if request.method == 'POST':
        form = LoanInquiryForm(request.POST)
        form.instance.loan_type = loan_type
        if form.is_valid():
            # Convert loan amount to a plain integer
            raw_loan_amount = request.POST.get('loan_amount').replace('.', '')  # Remove periods
            form.instance.loan_amount = raw_loan_amount  # Save the unformatted amount
            
            inquiry = form.save()

            # Generate OTP
            otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
            request.session['otp'] = otp
            request.session['inquiry_id'] = inquiry.id

            # Prepare the OTP email content
            email_subject = 'Verifikasi OTP untuk Permohonan Pinjaman'
            email_body = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            padding: 20px;
                            color: #333;
                        }}
                        .email-container {{
                            background-color: #ffffff;
                            padding: 20px;
                            border-radius: 5px;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        }}
                        .email-title {{
                            color: #008374;
                            font-size: 28px;
                            margin-bottom: 10px;
                        }}
                        .email-greeting {{
                            font-size: 18px;
                        }}
                        .email-message {{
                            font-size: 16px;
                            line-height: 1.5;
                        }}
                        .otp-code {{
                            font-weight: bold;
                            font-size: 24px;
                            color: #008374;
                            margin: 10px 0;
                        }}
                        .email-signoff {{
                            margin-top: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="email-title">Verifikasi Kode OTP</div>
                        <div class="email-greeting">Halo,</div>
                        <div class="email-message">
                            Terima kasih telah mengajukan permohonan. Kode OTP Anda untuk verifikasi adalah:
                        </div>
                        <div class="otp-code">{otp}</div>
                        <div class="email-message">
                            Harap masukkan kode ini untuk melanjutkan proses. Jika Anda tidak merasa melakukan permohonan ini, silakan abaikan email ini.
                        </div>
                        <div class="email-signoff">Salam,<br>Tim FINANCIAL BROKER</div>
                    </div>
                </body>
                </html>
                """

            send_mail(
                email_subject,
                '',
                'Financial Broker <financialbrokerid@gmail.com>',
                [inquiry.email],  # Send to the user's email
                fail_silently=False,
                html_message=email_body  # Use this for HTML content
            )

            # Redirect to the OTP verification page
            return redirect('verify_otp_loan')

    else:
        form = LoanInquiryForm(initial={'loan_type': loan_type})

    return render(request, 'loan_inquiry.html', {'form': form, 'loan_type': formatted_loan_type})

def verify_otp_loan(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        generated_otp = request.session.get('otp')
        inquiry_id = request.session.get('inquiry_id')

        if entered_otp == generated_otp:
            # OTP is correct, mark the inquiry as verified
            inquiry = LoanInquiry.objects.get(id=inquiry_id)
            inquiry.is_verified = True  # Assuming you have this field in your model
            inquiry.save()

            gender_map = {
                'male': 'Laki-laki',
                'female': 'Perempuan',
            }

            # Prepare the email content for confirmation
            email_subject = 'Permohonan Pinjaman Baru'
            email_body = f"""
            <html>
            <head>
                <style>
                    .email-body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                    }}
                    .email-container {{
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }}
                    .email-title {{
                        color: #008374;
                    }}
                </style>
            </head>
            <body class="email-body">
                <div class="email-container">
                    <h2 class="email-title">Permohonan Pinjaman Baru</h2>
                    <p style="color: #000000;"><strong>Nama:</strong> {inquiry.name}</p>
                    <p style="color: #000000;"><strong>Email:</strong> {inquiry.email}</p>
                    <p style="color: #000000;"><strong>Domisili:</strong> {inquiry.domicile}</p>
                    <p style="color: #000000;"><strong>Nomor Telepon:</strong> {inquiry.phone_number}</p>
                    <p style="color: #000000;"><strong>Jenis Kelamin:</strong> {gender_map.get(inquiry.gender, inquiry.gender)}</p>
                    <p style="color: #000000;"><strong>Plafon Pinjaman:</strong> {format(int(inquiry.loan_amount), ',').replace(',', '.')}</p>
                    <p style="color: #000000;"><strong>Tipe Pinjaman:</strong> {inquiry.loan_type}</p>
                </div>
            </body>
            </html>
            """

            send_mail(
                email_subject,
                '',
                'Financial Broker <financialbrokerid@gmail.com>',
                ['billyjonathanjahja@gmail.com', 'danielfelixjahja@gmail.com', 'marketing@financialbroker.id'],  # Send to the user's email
                fail_silently=False,
                html_message=email_body  # Use this for HTML content
            )

            return redirect('thank_you')  # Redirect to thank you page
        else:
            # Handle invalid OTP
            error_message = "OTP yang Anda masukkan tidak valid."
            return render(request, 'verify_otp_loan.html', {'error_message': error_message})

    return render(request, 'verify_otp_loan.html')

def thank_you(request):
    return render(request, 'thank_you.html')  
def thank_you_property(request):
    return render(request, 'thank_you_property.html')  

def history(request):
    if request.method == 'POST':
        form = HistoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']

            # Check for existing inquiries
            inquiries = LoanInquiry.objects.filter(name=name, email=email, phone_number=phone_number)

            if inquiries.exists():
                otp = random.randint(100000, 999999)
                request.session['otp'] = otp
                request.session['user_inquiries'] = [
                    {
                        'name': inquiry['name'],
                        'email': inquiry['email'],
                        'phone_number': inquiry['phone_number'],
                        'loan_amount': int(inquiry['loan_amount']),  # Convert to int to remove .0
                        'loan_type': inquiry['loan_type'],  # Include loan type
                        'submitted_at': inquiry['submitted_at'].strftime('%d %B %Y') if inquiry['submitted_at'] else None,  # Format datetime
                        'gender': 'Laki-laki' if inquiry['gender'] == 'male' else 'Perempuan',  # Change gender display
                    }
                    for inquiry in inquiries.values()
                ]

                otp_email_body = f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            padding: 20px;
                            color: #333;
                        }}
                        .email-container {{
                            background-color: #ffffff;
                            padding: 20px;
                            border-radius: 5px;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        }}
                        .email-title {{
                            color: #008374;
                            font-size: 28px;
                            margin-bottom: 10px;
                        }}
                        .email-greeting {{
                            font-size: 18px;
                        }}
                        .email-message {{
                            font-size: 16px;
                            line-height: 1.5;
                        }}
                        .otp-code {{
                            font-weight: bold;
                            font-size: 24px;
                            color: #008374;
                            margin: 10px 0;
                        }}
                        .email-signoff {{
                            margin-top: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="email-title">Verifikasi Kode OTP</div>
                        <div class="email-greeting">Halo,</div>
                        <div class="email-message">
                            Terima kasih telah mengajukan permohonan. Kode OTP Anda untuk verifikasi adalah:
                        </div>
                        <div class="otp-code">{otp}</div>
                        <div class="email-message">
                            Harap masukkan kode ini untuk melanjutkan proses. Jika Anda tidak merasa melakukan permohonan ini, silakan abaikan email ini.
                        </div>
                        <div class="email-signoff">Salam,<br>Tim FINANCIAL BROKER</div>
                    </div>
                </body>
                </html>
                """

                # Then use this in your send_mail function
                send_mail(
                    'Kode OTP Anda',
                    '',  # Leave this empty because we're sending HTML
                    [email],
                    fail_silently=False,
                    html_message=otp_email_body  # Use this for HTML content
                )
                return redirect('verify_otp')  # Redirect to OTP verification page
            else:
                # Handle case where no inquiries are found
                error_message = "Tidak ada riwayat pengajuan yang tercatat"
                return render(request, 'history.html', {'form': form, 'error_message': error_message})
    else:
        form = HistoryForm()
    
    return render(request, 'history.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == str(request.session.get('otp')):
            return redirect('inquiry_list')
        else:
            error_message = "OTP tidak valid. Silakan coba lagi."
            return render(request, 'verify_otp.html', {'error_message': error_message})

    return render(request, 'verify_otp.html')

def terms_condition(request):
    return render(request, 'terms_condition.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def perjanjian(request):
    return render(request, 'perjanjian.html')


def inquiry_list(request):
    inquiries = request.session.get('user_inquiries', [])
    for inquiry in inquiries:
        loan_amount = inquiry.get('loan_amount', '0')
        # Format loan amount with periods as thousand separators
        try:
            inquiry['formatted_loan_amount'] = format(int(loan_amount), ',').replace(',', '.')
        except ValueError:
            inquiry['formatted_loan_amount'] = loan_amount
    return render(request, 'inquiry_list.html', {'inquiries': inquiries})

def delete_inquiry(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        submitted_at = request.POST.get('submitted_at')
        
        inquiries = request.session.get('user_inquiries', [])
        inquiries = [
            inquiry for inquiry in inquiries 
            if not (inquiry['email'] == email and inquiry['submitted_at'] == submitted_at)
        ]
        request.session['user_inquiries'] = inquiries

        return redirect('inquiry_list')  # Adjust this URL name as needed

    return redirect('inquiry_list')

def property_list(request):
    # Initialize the search form with GET data
    form = PropertySearchForm(request.GET)

    # Start with all properties
    properties = Property.objects.all()

    # Apply filters if the form is valid
    if form.is_valid():
        # Filter by location
        location = form.cleaned_data.get('location')
        if location:
            properties = properties.filter(location__icontains=location)

        # Filter by area
        min_area = form.cleaned_data.get('min_area')
        max_area = form.cleaned_data.get('max_area')
        if min_area:
            properties = properties.filter(area__gte=min_area)
        if max_area:
            properties = properties.filter(area__lte=max_area)

        # Filter by price range
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        if min_price:
            properties = properties.filter(price__gte=min_price)
        if max_price:
            properties = properties.filter(price__lte=max_price)

    # Pass the filtered properties and form to the template
    return render(request, 'property_list.html', {'properties': properties, 'form': form})

def property_inquiry(request, property_id):
    # Get the property object
    property = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        form = PropertyInquiryForm(request.POST)
        form.instance.property = property  # Link the inquiry to the property
        if form.is_valid():
            # Save the inquiry
            inquiry = form.save()

            # Generate OTP
            otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
            request.session['otp'] = otp
            request.session['inquiry_id'] = inquiry.id

            # Prepare the OTP email content
            email_subject = 'Verifikasi OTP untuk Permintaan Informasi Properti'
            email_body = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            padding: 20px;
                            color: #333;
                        }}
                        .email-container {{
                            background-color: #ffffff;
                            padding: 20px;
                            border-radius: 5px;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        }}
                        .email-title {{
                            color: #008374;
                            font-size: 28px;
                            margin-bottom: 10px;
                        }}
                        .email-greeting {{
                            font-size: 18px;
                        }}
                        .email-message {{
                            font-size: 16px;
                            line-height: 1.5;
                        }}
                        .otp-code {{
                            font-weight: bold;
                            font-size: 24px;
                            color: #008374;
                            margin: 10px 0;
                        }}
                        .email-signoff {{
                            margin-top: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="email-title">Verifikasi Kode OTP</div>
                        <div class="email-greeting">Halo,</div>
                        <div class="email-message">
                            Terima kasih telah mengajukan permintaan informasi untuk properti <strong>{property.title}</strong>.
                            Kode OTP Anda untuk verifikasi adalah:
                        </div>
                        <div class="otp-code">{otp}</div>
                        <div class="email-message">
                            Harap masukkan kode ini untuk melanjutkan proses. Jika Anda tidak merasa melakukan permintaan ini, silakan abaikan email ini.
                        </div>
                        <div class="email-signoff">Salam,<br>Tim Properti Kami</div>
                    </div>
                </body>
            </html>
            """

            send_mail(
                email_subject,
                '',
                'Financial Broker <financialbrokerid@gmail.com>',
                [inquiry.email],  # Send to the user's email
                fail_silently=False,
                html_message=email_body  # Use this for HTML content
            )

            # Redirect to the OTP verification page
            return redirect('verify_otp_property')

    else:
        form = PropertyInquiryForm()

    return render(request, 'property_inquiry.html', {'form': form, 'property': property})

def verify_otp_property(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        generated_otp = request.session.get('otp')
        inquiry_id = request.session.get('inquiry_id')

        if entered_otp == generated_otp:
            # OTP is correct, mark the inquiry as verified
            inquiry = PropertyInquiry.objects.get(id=inquiry_id)
            inquiry.is_verified = True  # Assuming you have this field in your model
            inquiry.save()

            # Prepare the email content for confirmation
            email_subject = 'Permintaan Informasi Properti Baru'
            email_body = f"""
            <html>
            <head>
                <style>
                    .email-body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                    }}
                    .email-container {{
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }}
                    .email-title {{
                        color: #008374;
                    }}
                </style>
            </head>
            <body class="email-body">
                <div class="email-container">
                    <h2 class="email-title">Permintaan Informasi Properti Baru</h2>
                    <p style="color: #000000;"><strong>Nama:</strong> {inquiry.name}</p>
                    <p style="color: #000000;"><strong>Email:</strong> {inquiry.email}</p>
                    <p style="color: #000000;"><strong>Nomor Telepon:</strong> {inquiry.phone_number}</p>
                </div>
            </body>
            </html>
            """

            send_mail(
                email_subject,
                '',
                'Financial Broker <financialbrokerid@gmail.com>',
                # ['emailcumanbuatgame@gmail.com'],
                ['billyjonathanjahja@gmail.com', 'danielfelixjahja@gmail.com', 'marketing@financialbroker.id'],  # Send to the appropriate email addresses
                fail_silently=False,
                html_message=email_body  # Use this for HTML content
            )

            return redirect('thank_you_property')  # Redirect to a property-specific thank you page
        else:
            # Handle invalid OTP
            error_message = "OTP yang Anda masukkan tidak valid."
            return render(request, 'verify_otp_property.html', {'error_message': error_message})

    return render(request, 'verify_otp_property.html')

def property_detail(request, slug):
    property = get_object_or_404(Property, slug=slug)
    return render(request, 'property_detail.html', {'property': property})

def custom_admin(request):
    properties = Property.objects.all()
    return render(request, 'admins/custom_admin.html', {'properties': properties})

ADMIN_USERNAME = "fbadmin"
ADMIN_PASSWORD = "11223344"

def admin_verification(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the entered username and password match the stored credentials
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect('custom_admin')  # Redirect to the custom admin page
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('admin_verification')  # Stay on the verification page if credentials are wrong

    return render(request, 'admin_verification.html')

def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)

    if request.method == 'POST':
        property.delete()
        return redirect('custom_admin')  # Redirect back to the admin page

def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)  # Don't pass request.FILES here
        if form.is_valid():
            property_instance = form.save()  # Save property first

            # Process multiple images
            images = request.FILES.getlist('images')  # Get list of uploaded images
            for image in images:
                PropertyImage.objects.create(property=property_instance, image=image)  # Save each image

            return redirect('property_list')  # Redirect after successful upload
    else:
        form = PropertyForm()

    return render(request, 'add_property.html', {'form': form})

def ads_inquiry(request):
    # Get the property object
    # property = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        form = AdsForm(request.POST)
        if form.is_valid():
            # Save the inquiry
            inquiry = form.save()

            # Generate OTP
            otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
            request.session['otp'] = otp
            request.session['inquiry_id'] = inquiry.id

            # Prepare the OTP email content
            email_subject = 'Verifikasi OTP untuk Permintaan Pengiklanan Properti'
            email_body = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            padding: 20px;
                            color: #333;
                        }}
                        .email-container {{
                            background-color: #ffffff;
                            padding: 20px;
                            border-radius: 5px;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        }}
                        .email-title {{
                            color: #008374;
                            font-size: 28px;
                            margin-bottom: 10px;
                        }}
                        .email-greeting {{
                            font-size: 18px;
                        }}
                        .email-message {{
                            font-size: 16px;
                            line-height: 1.5;
                        }}
                        .otp-code {{
                            font-weight: bold;
                            font-size: 24px;
                            color: #008374;
                            margin: 10px 0;
                        }}
                        .email-signoff {{
                            margin-top: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="email-title">Verifikasi Kode OTP</div>
                        <div class="email-greeting">Halo,</div>
                        <div class="email-message">
                            Terima kasih telah mengajukan permohonan.
                            Kode OTP Anda untuk verifikasi adalah:
                        </div>
                        <div class="otp-code">{otp}</div>
                        <div class="email-message">
                            Harap masukkan kode ini untuk melanjutkan proses. Jika Anda tidak merasa melakukan permintaan ini, silakan abaikan email ini.
                        </div>
                        <div class="email-signoff">Salam,<br>Tim Financial Broker</div>
                    </div>
                </body>
            </html>
            """

            send_mail(
                email_subject,
                '',
                'Financial Broker <financialbrokerid@gmail.com>',
                [inquiry.email],  # Send to the user's email
                fail_silently=False,
                html_message=email_body  # Use this for HTML content
            )

            # Redirect to the OTP verification page
            return redirect('verify_otp_ads')

    else:
        form = AdsForm()

    return render(request, 'ads_inquiry.html', {'form': form})

def verify_otp_ads(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        generated_otp = request.session.get('otp')
        inquiry_id = request.session.get('inquiry_id')

        if entered_otp == generated_otp:
            # OTP is correct, mark the inquiry as verified
            inquiry = AdsInquiry.objects.get(id=inquiry_id)
            inquiry.is_verified = True  # Assuming you have this field in your model
            inquiry.save()

            # Prepare the email content for confirmation
            email_subject = 'Permintaan Pengiklanan Properti Baru'
            email_body = f"""
            <html>
            <head>
                <style>
                    .email-body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        padding: 20px;
                    }}
                    .email-container {{
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }}
                    .email-title {{
                        color: #008374;
                    }}
                </style>
            </head>
            <body class="email-body">
                <div class="email-container">
                    <h2 class="email-title">Permohonan Iklan</h2>
                    <p style="color: #000000;"><strong>Nama:</strong> {inquiry.name}</p>
                    <p style="color: #000000;"><strong>Email:</strong> {inquiry.email}</p>
                    <p style="color: #000000;"><strong>Nomor Telepon:</strong> {inquiry.phone_number}</p>
                </div>
            </body>
            </html>
            """

            send_mail(
                email_subject,
                '',
                'Financial Broker <financialbrokerid@gmail.com>',
                # ['emailcumanbuatgame@gmail.com'],
                ['billyjonathanjahja@gmail.com', 'danielfelixjahja@gmail.com', 'marketing@financialbroker.id'],  # Send to the appropriate email addresses
                fail_silently=False,
                html_message=email_body  # Use this for HTML content
            )

            return redirect('thank_you_property')  # Redirect to a property-specific thank you page
        else:
            # Handle invalid OTP
            error_message = "OTP yang Anda masukkan tidak valid."
            return render(request, 'verify_otp_ads.html', {'error_message': error_message})

    return render(request, 'verify_otp_ads.html')

def kpr_calculator(request):
    monthly_payment = None

    if request.method == 'POST':
        form = KPRCalculatorForm(request.POST)
        if form.is_valid():
            # Remove thousand separators and convert to int
            harga_properti = int(form.cleaned_data['harga_properti'].replace('.', ''))
            uang_muka = int(form.cleaned_data['uang_muka'].replace('.', ''))
            bunga = form.cleaned_data['bunga']
            tenor = form.cleaned_data['tenor']

            pinjaman = harga_properti - uang_muka
            bunga_bulanan = bunga / 12 / 100
            jumlah_angsuran = tenor * 12

            if bunga_bulanan > 0:
                monthly_payment = round(
                    pinjaman * bunga_bulanan / (1 - (1 + bunga_bulanan) ** -jumlah_angsuran)
                )
            else:
                monthly_payment = round(pinjaman / jumlah_angsuran)

    else:
        form = KPRCalculatorForm()

    return render(request, 'kpr_calculator.html', {
        'form': form,
        'monthly_payment': monthly_payment
    })

def modal_kerja_calculator(request):
    anuitas_schedule = []
    efektif_schedule = []
    total_anuitas = total_efektif = 0
    plafon_pinjaman = bunga = tenor = 0

    if request.method == 'POST':
        form = ModalKerjaCalculatorForm(request.POST)
        if form.is_valid():
            plafon_pinjaman = int(str(form.cleaned_data['plafon_pinjaman']).replace('.', '').replace(',', '').strip())
            bunga = form.cleaned_data['bunga']
            tenor = form.cleaned_data['tenor']

            tenor_bulan = tenor * 12
            bunga_bulanan = bunga / 100 / 12

            # Metode Anuitas
            if bunga_bulanan > 0:
                cicilan = round(plafon_pinjaman * bunga_bulanan / (1 - (1 + bunga_bulanan) ** -tenor_bulan))
            else:
                cicilan = round(plafon_pinjaman / tenor_bulan)

            for i in range(tenor_bulan):
                anuitas_schedule.append({
                    'bulan': i + 1,
                    'total': cicilan
                })
                total_anuitas += cicilan

            # Metode Efektif
            sisa_pinjaman = plafon_pinjaman
            pokok_per_bulan = round(plafon_pinjaman / tenor_bulan, -3)
            for i in range(tenor_bulan):
                bunga_bulan_ini = round(sisa_pinjaman * bunga_bulanan, -3)
                total_cicilan = bunga_bulan_ini + pokok_per_bulan
                efektif_schedule.append({
                    'bulan': i + 1,
                    'total': round(total_cicilan, -3)
                })
                total_efektif += total_cicilan
                sisa_pinjaman -= pokok_per_bulan
    else:
        form = ModalKerjaCalculatorForm()

    return render(request, 'modal_kerja_calculator.html', {
        'form': form,
        'anuitas_schedule': anuitas_schedule,
        'efektif_schedule': efektif_schedule,
        'total_anuitas': total_anuitas,
        'total_efektif': round(total_efektif),
        'plafon_pinjaman': plafon_pinjaman,
        'bunga': bunga,
        'tenor': tenor
    })

def modal_kerja_pdf(request):
    if request.method == 'POST':
        form = ModalKerjaCalculatorForm(request.POST)
        if form.is_valid():
            plafon_pinjaman = int(str(form.cleaned_data['plafon_pinjaman']).replace('.', '').replace(',', '').strip())
            bunga = form.cleaned_data['bunga']
            tenor = form.cleaned_data['tenor']

            tenor_bulan = tenor * 12
            bunga_bulanan = bunga / 100 / 12

            # Metode Anuitas
            if bunga_bulanan > 0:
                cicilan = round(plafon_pinjaman * bunga_bulanan / (1 - (1 + bunga_bulanan) ** -tenor_bulan))
            else:
                cicilan = round(plafon_pinjaman / tenor_bulan)

            anuitas_schedule = []
            total_anuitas = 0
            for i in range(tenor_bulan):
                anuitas_schedule.append({
                    'bulan': i + 1,
                    'total': cicilan
                })
                total_anuitas += cicilan

            # === PERHITUNGAN EFEKTIF ===
            efektif_schedule = []
            total_efektif = 0
            pokok_per_bulan = round(plafon_pinjaman / tenor_bulan, -3)

            for i in range(tenor_bulan + 1):
                if i == 0:
                    continue

                if i == tenor_bulan + 1:
                    efektif_schedule.append({
                        'bulan': i,
                        'pokok': 0,
                        'bunga': 0,
                        'total': 0
                    })
                    break

                sisa_pokok = plafon_pinjaman - (pokok_per_bulan * i)
                bunga_bulan_ini = round(sisa_pokok * bunga_bulanan, -3)
                cicilan_bulan_ini = pokok_per_bulan + bunga_bulan_ini
                efektif_schedule.append({
                    'bulan': i,
                    'pokok': pokok_per_bulan,
                    'bunga': bunga_bulan_ini,
                    'total': round(cicilan_bulan_ini, -3)
                })
                total_efektif += cicilan_bulan_ini

            template = get_template('modal_kerja_pdf.html')
            html = template.render({
                'anuitas_schedule': anuitas_schedule,
                'efektif_schedule': efektif_schedule,
                'total_anuitas': total_anuitas,
                'total_efektif': round(total_efektif),
                'plafon_pinjaman': plafon_pinjaman,
                'bunga': bunga,
                'tenor': tenor
            })

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="modal_kerja_kalkulasi.pdf"'
            pisa_status = pisa.CreatePDF(html, dest=response)

            if pisa_status.err:
                return HttpResponse('Terjadi kesalahan saat membuat PDF.')
            return response

    return redirect('modal_kerja_calculator')

def multiguna_calculator(request):
    efektif_schedule = []
    anuitas_schedule = []
    total_efektif = 0
    total_anuitas = 0

    if request.method == 'POST':
        form = MultigunaCalculatorForm(request.POST)
        if form.is_valid():
            # Clean currency
            plafon_pinjaman = int(str(form.cleaned_data['plafon_pinjaman']).replace('.', '').replace(',', '').strip())
            bunga_tahunan = form.cleaned_data['bunga']
            tenor_tahun = form.cleaned_data['tenor']

            tenor_bulan = tenor_tahun * 12
            bunga_bulanan = bunga_tahunan / 100 / 12

            ### === PERHITUNGAN EFEKTIF ===
            pokok_per_bulan = round(plafon_pinjaman / tenor_bulan, -3)
            for i in range(tenor_bulan):
                sisa_pokok = plafon_pinjaman - (pokok_per_bulan * i)
                bunga_bulan_ini = round(sisa_pokok * bunga_bulanan, -3)
                cicilan_bulan_ini = pokok_per_bulan + bunga_bulan_ini
                efektif_schedule.append({
                    'bulan': i + 1,
                    'pokok': pokok_per_bulan,
                    'bunga': bunga_bulan_ini,
                    'total': round(cicilan_bulan_ini, -3)
                })
                total_efektif += cicilan_bulan_ini

            ### === PERHITUNGAN ANUITAS ===
            if bunga_bulanan > 0:
                cicilan_anuitas = round(plafon_pinjaman * bunga_bulanan / (1 - (1 + bunga_bulanan) ** -tenor_bulan))
            else:
                cicilan_anuitas = round(plafon_pinjaman / tenor_bulan)

            for i in range(tenor_bulan):
                anuitas_schedule.append({
                    'bulan': i + 1,
                    'total': cicilan_anuitas
                })
                total_anuitas += cicilan_anuitas
    else:
        form = MultigunaCalculatorForm()

    return render(request, 'multiguna_calculator.html', {
        'form': form,
        'efektif_schedule': efektif_schedule,
        'anuitas_schedule': anuitas_schedule,
        'total_efektif': total_efektif,
        'total_anuitas': total_anuitas
    })

@csrf_exempt
def multiguna_calculator_pdf(request):
    if request.method == 'POST':
        form = MultigunaCalculatorForm(request.POST)
        if form.is_valid():
            plafon_pinjaman = int(str(form.cleaned_data['plafon_pinjaman']).replace('.', '').replace(',', '').strip())
            bunga_tahunan = form.cleaned_data['bunga']
            tenor_tahun = form.cleaned_data['tenor']

            tenor_bulan = tenor_tahun * 12
            bunga_bulanan = bunga_tahunan / 100 / 12

            # === PERHITUNGAN EFEKTIF ===
            efektif_schedule = []
            total_efektif = 0
            pokok_per_bulan = round(plafon_pinjaman / tenor_bulan, -3)

            for i in range(tenor_bulan + 1):
                if i == 0:
                    continue

                if i == tenor_bulan + 1:
                    efektif_schedule.append({
                        'bulan': i,
                        'pokok': 0,
                        'bunga': 0,
                        'total': 0
                    })
                    break

                sisa_pokok = plafon_pinjaman - (pokok_per_bulan * i)
                bunga_bulan_ini = round(sisa_pokok * bunga_bulanan, -3)
                cicilan_bulan_ini = pokok_per_bulan + bunga_bulan_ini
                efektif_schedule.append({
                    'bulan': i,
                    'pokok': pokok_per_bulan,
                    'bunga': bunga_bulan_ini,
                    'total': round(cicilan_bulan_ini, -3)
                })
                total_efektif += cicilan_bulan_ini

            # === PERHITUNGAN ANUITAS ===
            if bunga_bulanan > 0:
                cicilan_anuitas = round(plafon_pinjaman * bunga_bulanan / (1 - (1 + bunga_bulanan) ** -tenor_bulan))
            else:
                cicilan_anuitas = round(plafon_pinjaman / tenor_bulan)

            anuitas_schedule = []
            total_anuitas = 0
            for i in range(tenor_bulan):
                anuitas_schedule.append({
                    'bulan': i + 1,
                    'total': cicilan_anuitas
                })
                total_anuitas += cicilan_anuitas

            context = {
                'plafon_pinjaman': plafon_pinjaman,
                'bunga': bunga_tahunan,
                'tenor': tenor_tahun,
                'total_efektif': total_efektif,
                'total_anuitas': total_anuitas,
                'efektif_schedule': efektif_schedule,
                'anuitas_schedule': anuitas_schedule,
            }

            template_path = 'multiguna_pdf.html'
            template = get_template(template_path)
            html = template.render(context)

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="multiguna_kalkulasi.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response

    return HttpResponse("Invalid data", status=400)

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def why_us(request):
    return render(request, 'why_us.html')

def kpr(request):
    return render(request, 'kpr.html')

def kpr_primary(request):
    return render(request, 'kpr_primary.html')

def kpr_secondary(request):
    return render(request, 'kpr_secondary.html')

def kredit_investasi(request):
    return render(request, 'kredit_investasi.html')

def multiguna_refinancing(request):
    return render(request, 'multiguna_refinancing.html')

def multiguna(request):
    return render(request, 'multiguna.html')

def refinancing(request):
    return render(request, 'refinancing.html')

def modal_kerja(request):
    return render(request, 'modal_kerja.html')

def take_over(request):
    return render(request, 'take_over.html')

def take_over_modal_kerja(request):
    return render(request, 'take_over_modal_kerja.html')

def take_over_multiguna(request):
    return render(request, 'take_over_multiguna.html')

def take_over_jual_beli(request):
    return render(request, 'take_over_jual_beli.html')

def take_over_kpr(request):
    return render(request, 'take_over_kpr.html')

def jaminan_bpkb_alat_berat(request):
    return render(request, 'jaminan_bpkb_alat_berat.html')

def jaminan_bpkb(request):
    return render(request, 'jaminan_bpkb.html')

def jaminan_alat_berat(request):
    return render(request, 'jaminan_alat_berat.html')

def invoice_po_spk_financing(request):
    return render(request, 'invoice_po_spk_financing.html')

def po_financing(request):
    return render(request, 'po_financing.html')

def spk_financing(request):
    return render(request, 'spk_financing.html')

def invoice_financing(request):
    return render(request, 'invoice_financing.html')

def bridging_offering_letter(request):
    return render(request, 'bridging_offering_letter.html')

def take_over_top_up(request):
    return render(request, 'take_over_top_up.html')

def take_over_refinancing(request):
    return render(request, 'take_over_refinancing.html')

def sitemap(request):
    return render(request, 'sitemap.xml')

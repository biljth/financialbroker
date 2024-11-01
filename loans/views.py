from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import LoanInquiryForm, HistoryForm
from .models import LoanInquiry
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
                ['emailcumanbuatgame@gmail.com', 'hutauruk.lamhot@gmail.com','wisdom334@yahoo.co.id', 'danielfelixjahja@gmail.com'],  # Send to the user's email
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
                    'billyjonathanjahja@gmail.com',
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

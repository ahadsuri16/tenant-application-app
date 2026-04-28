import re

file_path = r"c:\Users\ahads\OneDrive\Desktop\New folder\index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

replacements = [
    # Header
    (r"<h1>Tenant Application Form</h1>", r'<h1>Tenant Application Form <span dir="rtl" class="urdu-text">(کرایہ دار کی درخواست کا فارم)</span></h1>'),
    (r"<p>Please fill out the details below to complete your application.</p>", r'<p>Please fill out the details below to complete your application. <span dir="rtl" class="urdu-text">(براہ کرم اپنی درخواست مکمل کرنے کے لیے نیچے دی گئی تفصیلات پُر کریں۔)</span></p>'),
    
    # Section 1
    (r"<h2><span class=\"icon\">👤</span> Personal Information of Family Head</h2>", r'<h2><span class="icon">👤</span> Personal Information of Family Head <span dir="rtl" class="urdu-text">(خاندان کے سربراہ کی ذاتی معلومات)</span></h2>'),
    (r"<label for=\"fullName\">Full Name</label>", r'<label for="fullName">Full Name <span dir="rtl" class="urdu-text">(مکمل نام)</span></label>'),
    (r"placeholder=\"Ali\"", r'placeholder="Ali (علی)"'),
    (r"<label for=\"phone\">Phone Number</label>", r'<label for="phone">Phone Number <span dir="rtl" class="urdu-text">(فون نمبر)</span></label>'),
    (r"<label for=\"cnic\">Upload CNIC Picture</label>", r'<label for="cnic">Upload CNIC Picture <span dir="rtl" class="urdu-text">(شناختی کارڈ کی تصویر اپ لوڈ کریں)</span></label>'),
    (r"<span class=\"upload-text\">Choose a file or drag it here</span>", r'<span class="upload-text">Choose a file or drag it here <span dir="rtl" class="urdu-text">(کوئی فائل منتخب کریں یا یہاں کھینچ لائیں)</span></span>'),
    (r"<label for=\"address\">Permanent Address</label>", r'<label for="address">Permanent Address <span dir="rtl" class="urdu-text">(مستقل پتہ)</span></label>'),
    
    # Section 2
    (r"<h2><span class=\"icon\">👨‍👩‍👧</span> Tenant Details</h2>", r'<h2><span class="icon">👨‍👩‍👧</span> Tenant Details <span dir="rtl" class="urdu-text">(کرایہ دار کی تفصیلات)</span></h2>'),
    (r"<label for=\"peopleDetails\">How many people will live in the house & Your relation with\s*them\?</label>", r'<label for="peopleDetails">How many people will live in the house & Your relation with them? <span dir="rtl" class="urdu-text">(گھر میں کتنے افراد رہیں گے اور ان سے آپ کا کیا رشتہ ہے؟)</span></label>'),
    (r"<label>Any pets\?</label>", r'<label>Any pets? <span dir="rtl" class="urdu-text">(کیا آپ کے پاس کوئی پالتو جانور ہے؟)</span></label>'),
    (r"<span class=\"radio-custom\"></span> Yes\s*</label>", r'<span class="radio-custom"></span> Yes (ہاں)</label>'),
    (r"<span class=\"radio-custom\"></span> No\s*</label>", r'<span class="radio-custom"></span> No (نہیں)</label>'),
    (r"<label for=\"petDetails\">Pet Details</label>", r'<label for="petDetails">Pet Details <span dir="rtl" class="urdu-text">(پالتو جانور کی تفصیلات)</span></label>'),
    
    # Section 3
    (r"<h2><span class=\"icon\">💼</span> Employment / Source of Income</h2>", r'<h2><span class="icon">💼</span> Employment / Source of Income <span dir="rtl" class="urdu-text">(روزگار / آمدنی کا ذریعہ)</span></h2>'),
    (r"<label for=\"occupation\">Occupation</label>", r'<label for="occupation">Occupation <span dir="rtl" class="urdu-text">(پیشہ)</span></label>'),
    (r"<option value=\"job\">Job / Salaried</option>", r'<option value="job">Job / Salaried (نوکری / تنخواہ دار)</option>'),
    (r"<option value=\"business\">Business / Self-Employed</option>", r'<option value="business">Business / Self-Employed (کاروبار / ذاتی روزگار)</option>'),
    (r"<option value=\"student\">Student</option>", r'<option value="student">Student (طالب علم)</option>'),
    (r"<option value=\"other\">Other</option>", r'<option value="other">Other (دیگر)</option>'),
    
    (r"<label for=\"company\">Company / Organization Name</label>", r'<label for="company">Company / Organization Name <span dir="rtl" class="urdu-text">(کمپنی / ادارے کا نام)</span></label>'),
    (r"<label for=\"jobType\">Job Type</label>", r'<label for="jobType">Job Type <span dir="rtl" class="urdu-text">(نوکری کی قسم)</span></label>'),
    (r"<option value=\"private\">Private Sector</option>", r'<option value="private">Private Sector (نجی شعبہ)</option>'),
    (r"<option value=\"public\">Public / Government</option>", r'<option value="public">Public / Government (سرکاری / گورنمنٹ)</option>'),
    
    (r"<label for=\"businessInfo\">Business / Self-Employed Details</label>", r'<label for="businessInfo">Business / Self-Employed Details <span dir="rtl" class="urdu-text">(کاروبار کی تفصیلات)</span></label>'),
    
    (r"<label for=\"institute\">Institute Details</label>", r'<label for="institute">Institute Details <span dir="rtl" class="urdu-text">(تعلیمی ادارے کی تفصیلات)</span></label>'),
    (r"<label>Any source of income\?</label>", r'<label>Any source of income? <span dir="rtl" class="urdu-text">(کیا آمدنی کا کوئی ذریعہ ہے؟)</span></label>'),
    (r"<label for=\"incomeSourceDetails\">Source of Income Details</label>", r'<label for="incomeSourceDetails">Source of Income Details <span dir="rtl" class="urdu-text">(آمدنی کے ذریعہ کی تفصیلات)</span></label>'),
    
    (r"<label for=\"income\">Monthly Income \(Range\)</label>", r'<label for="income">Monthly Income (Range) <span dir="rtl" class="urdu-text">(ماہانہ آمدنی کی حد)</span></label>'),
    (r"<label for=\"employmentDuration\">How long working there\?</label>", r'<label for="employmentDuration">How long working there? <span dir="rtl" class="urdu-text">(آپ کو وہاں کام کرتے ہوئے کتنا عرصہ ہو گیا ہے؟)</span></label>'),

    # Section 4
    (r"<h2><span class=\"icon\">📅</span> Rental Preferences</h2>", r'<h2><span class="icon">📅</span> Rental Preferences <span dir="rtl" class="urdu-text">(کرائے کی ترجیحات)</span></h2>'),
    (r"<label for=\"moveInDate\">When do you want to move in\?</label>", r'<label for="moveInDate">When do you want to move in? <span dir="rtl" class="urdu-text">(آپ کب منتقل ہونا چاہتے ہیں؟)</span></label>'),
    (r"<label for=\"stayDuration\">How long do you plan to stay\?</label>", r'<label for="stayDuration">How long do you plan to stay? <span dir="rtl" class="urdu-text">(آپ کا کتنا عرصہ قیام کا ارادہ ہے؟)</span></label>'),
    (r"<label for=\"rentRange\">Preferred Rent Range \(Optional\)</label>", r'<label for="rentRange">Preferred Rent Range (Optional) <span dir="rtl" class="urdu-text">(کرائے کی ترجیحی حد (اختیاری))</span></label>'),
    (r"<label>Can you pay security deposit\?</label>", r'<label>Can you pay security deposit? <span dir="rtl" class="urdu-text">(کیا آپ سیکیورٹی ڈپازٹ ادا کر سکتے ہیں؟)</span></label>'),
    
    # Section 5
    (r"<h2><span class=\"icon\">🏡</span> Rental History</h2>", r'<h2><span class="icon">🏡</span> Rental History <span dir="rtl" class="urdu-text">(کرائے کی تاریخ / سابقہ ریکارڈ)</span></h2>'),
    (r"<label>Have you rented before\?</label>", r'<label>Have you rented before? <span dir="rtl" class="urdu-text">(کیا آپ نے پہلے کبھی کرائے پر گھر لیا ہے؟)</span></label>'),
    (r"<label for=\"previousLandlord\">Previous Landlord Contact \(Optional if you have\)</label>", r'<label for="previousLandlord">Previous Landlord Contact (Optional if you have) <span dir="rtl" class="urdu-text">(پچھلے مالک مکان کا رابطہ)</span></label>'),
    (r"<label for=\"reasonForLeaving\">Reason for leaving previous place</label>", r'<label for="reasonForLeaving">Reason for leaving previous place <span dir="rtl" class="urdu-text">(پچھلی جگہ چھوڑنے کی وجہ)</span></label>'),

    # Section 6
    (r"<h2><span class=\"icon\">📜</span> Rules, Regulations & Eligibility</h2>", r'<h2><span class="icon">📜</span> Rules, Regulations & Eligibility <span dir="rtl" class="urdu-text">(قواعد، ضوابط اور اہلیت)</span></h2>'),
    (r"Please read and confirm\s*all the following conditions:</p>", r'Please read and confirm all the following conditions: <span dir="rtl" class="urdu-text">(براہ کرم درج ذیل تمام شرائط پڑھیں اور تصدیق کریں:)</span></p>'),
    
    (r"I confirm that I will pay the monthly rent on or before the 10th of\s*each month. In case of delay, a late fee of PKR 50 per day will be applicable.</span>", r'I confirm that I will pay the monthly rent on or before the 10th of each month. In case of delay, a late fee of PKR 50 per day will be applicable. <span dir="rtl" class="urdu-text">(میں تصدیق کرتا ہوں کہ میں ہر ماہ کی 10 تاریخ تک کرایہ ادا کروں گا۔ تاخیر کی صورت میں روزانہ 50 روپے جرمانہ عائد ہوگا۔)</span></span>'),
    (r"I confirm that I have not been involved in any illegal or criminal\s*activity and have no history of unlawful conduct.</span>", r'I confirm that I have not been involved in any illegal or criminal activity and have no history of unlawful conduct. <span dir="rtl" class="urdu-text">(میں تصدیق کرتا ہوں کہ میں کسی غیر قانونی یا مجرمانہ سرگرمی میں ملوث نہیں رہا اور میرا کوئی غیر قانونی ریکارڈ نہیں ہے۔)</span></span>'),
    (r"I agree to use the property only for residential purposes and will\s*not engage in any illegal activities on the premises.</span>", r'I agree to use the property only for residential purposes and will not engage in any illegal activities on the premises. <span dir="rtl" class="urdu-text">(میں اتفاق کرتا ہوں کہ میں پراپرٹی صرف رہائشی مقاصد کے لیے استعمال کروں گا اور احاطے میں کسی غیر قانونی سرگرمی میں ملوث نہیں ہوں گا۔)</span></span>'),
    (r"I agree to respect neighbors and maintain a peaceful\s*environment.</span>", r'I agree to respect neighbors and maintain a peaceful environment. <span dir="rtl" class="urdu-text">(میں پڑوسیوں کا احترام کرنے اور پرامن ماحول برقرار رکھنے سے اتفاق کرتا ہوں۔)</span></span>'),
    (r"I agree to follow all house rules and terms set by the\s*landlord.</span>", r'I agree to follow all house rules and terms set by the landlord. <span dir="rtl" class="urdu-text">(میں مالک مکان کی مقرر کردہ تمام شرائط اور قواعد پر عمل کرنے سے اتفاق کرتا ہوں۔)</span></span>'),
    (r"I confirm that all the information provided in this application is\s*accurate and can be verified if required.</span>", r'I confirm that all the information provided in this application is accurate and can be verified if required. <span dir="rtl" class="urdu-text">(میں تصدیق کرتا ہوں کہ اس درخواست میں فراہم کردہ تمام معلومات درست ہیں اور ضرورت پڑنے پر ان کی تصدیق کی جا سکتی ہے۔)</span></span>'),
    
    (r"Sorry, you are not eligible to apply for this property.", r'Sorry, you are not eligible to apply for this property. <span dir="rtl" class="urdu-text">(معذرت، آپ اس پراپرٹی کے لیے درخواست دینے کے اہل نہیں ہیں۔)</span>'),
    
    # Button
    (r"<span>Submit Application</span>", r'<span>Submit Application <span dir="rtl" class="urdu-text" style="display:inline; color: white;">(جمع کروائیں)</span></span>'),
    (r"btn.innerHTML = '<span>Submitting...</span>';", r"btn.innerHTML = '<span>Submitting... <span dir=\"rtl\" class=\"urdu-text\" style=\"display:inline; color: white;\">(جمع ہو رہا ہے...)</span></span>';"),
    (r"btn.innerHTML = '<span>Application Sent! ✓</span>';", r"btn.innerHTML = '<span>Application Sent! ✓ <span dir=\"rtl\" class=\"urdu-text\" style=\"display:inline; color: white;\">(درخواست موصول ہو گئی! ✓)</span></span>';"),
    
    # Success Message
    (r"Thank you for submitting your application.</h2>", r'Thank you for submitting your application. <div dir="rtl" class="urdu-text" style="font-size: 0.7em; margin-top: 5px;">(آپ کی درخواست کا شکریہ)</div></h2>'),
    (r"We have successfully received your information. We will review your details and contact you shortly after verification.\s*<br><br>\s*We appreciate your interest.", r'We have successfully received your information. We will review your details and contact you shortly after verification.<br><br>We appreciate your interest.<br><br><span dir="rtl" class="urdu-text" style="font-size: 1.1rem; line-height: 1.8; color: var(--text-muted);">(آپ کی درخواست کامیابی سے موصول ہو گئی ہے۔ ہم آپ کی معلومات کی تصدیق کے بعد جلد ہی آپ سے رابطہ کریں گے۔)</span>')
]

for old, new in replacements:
    html = re.sub(old, new, html)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Done")

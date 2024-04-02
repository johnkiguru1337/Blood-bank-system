# Replace 'yourproject' with your project name
settings_path = 'Blood_Bank_System.settings'

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_path)

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Donor, BloodRequest, Profile, BloodDonation, DonationCount
from django.contrib import messages
from multiprocessing import context
from django.db.models import Q 
import csv
from . import predict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create your views here.

def signup(request):
    donor_group, _ = Group.objects.get_or_create(name='DonorGroup')
    patient_group, _ = Group.objects.get_or_create(name='PatientGroup')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        role = request.POST['role']
        try:
            user = User.objects.create_user(username, email, password )
            user.save()
             # Add user to specific group based on role
            if role == 'donor':
                donor_group.user_set.add(user)  
                pass
            elif role == 'patient':
                patient_group.user_set.add(user)
                pass
            # Login the user after signup
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Successfully logged in')
            return redirect('/')
        except:
            messages.error(request, f' Account name already exists !')
    return render(request, 'signup.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Successfully logged in")
                return redirect('/')
            else:
                messages.error(request, "Incorrect Username or Password")
                return redirect('login')
        except:
            messages.error(request, "Incorrect Username or Password")
    return render(request, 'login.html')

@login_required
def profile(request):
    try:
        if request.method == 'GET':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        else: 
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile) 
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)

        context = {
            'u_form': u_form,
            'p_form': p_form
        }

        return render(request, 'profile.html', context)
    except:
        messages.success(request, "Redirecting you to profile creation")
        return redirect("profile_form")

@login_required
def profile_form(request):
    u_form = UserUpdateForm(instance=request.user)
    context = {
        'u_form' : u_form
    }

    if request.method == 'POST':
        profile = Profile.objects.create(user=request.user)

        # Update profile using dedicated UserUpdateForm
        profile_form = UserUpdateForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('profile')  # Redirect to profile page after update

    return render(request, "create_profile.html", context)  # Handle invalid POST or other errors

@login_required
def logout_user(request):
    logout(request)
    return redirect('/login')

@login_required
def dashboard(request):
    # Get all user groups
    all_groups = Group.objects.all()
    # Get all donors
    donors = Donor.objects.all()
    # Get all blood Requests
    blood_request = BloodRequest.objects.all()
    available_blood = BloodDonation.objects.all()
    # Create empty dictionaries to store users by group
    group_users = {}
    for group in all_groups:
        group_users[group.name] = group.user_set.all().order_by('username')
    context = {'group_users': group_users , 'donors' : donors , 'blood_request': blood_request ,'available_blood': available_blood}
    return render(request, 'dashboard.html', context)

def home(request):
    return render(request, 'home.html')

@login_required
def request_blood(request):
    if request.method == 'POST':
        blood_type = request.POST['blood_type']
        # Create a BloodRequest object for the patient
        request_obj = BloodRequest.objects.create(patient=request.user, blood_type=blood_type)
        request_obj.save()
        # Show success message or redirect to appropriate page
        messages.success(request, "Successfully requested for blood")
        pass
    return render(request, 'request_blood.html')

@login_required
def donate(request):
    donors = Donor.objects.all()
    if request.method == 'POST':
        name = request.user.username
        for i in donors:
            if i.name == name:
                messages.error(request, "Thank you for your willingness to donate blood, Although you have already placed a another request. Sit tight you will be notified of approval shortly.")
                return redirect("donate")
        blood_type = request.POST['blood_type']
        # Create a Donor object
        donor_obj = Donor.objects.create(name=name, blood_type=blood_type, approved=False)
        donor_obj.save()
        messages.success(request, "Thank you for your willingness to donate blood! Your request is being reviewed and you will be notified of approval shortly.")
        return redirect('/')
        pass
    return render(request, 'donate.html')

@login_required
def view_donor_requests(request):
    group_name = 'StaffGroup'
    if request.user.is_superuser or request.user.groups.filter(name=group_name).exists():  # Check if admin
        donors = Donor.objects.filter(approved=False)
        potential_donors = Donor.objects.filter(approved=True)
        return render(request, 'view_donor_requests.html', {'donors': donors , 'potential_donors': potential_donors})  
    else:
        return redirect('/')  # Redirect non-admins

@login_required
def approve_donor(request, donor_id):
    group_name = 'StaffGroup'
    if request.user.is_superuser or request.user.groups.filter(name=group_name).exists():  # Check if admin or exists in StaffGroup group
        donor = Donor.objects.get(pk=donor_id)
        donor.approved = True
        donor.save()
        messages.success(request, "Successfully approved!")
        return redirect('/dashboard')
    else:
        return redirect('/')  # Redirect non-admins

@login_required
def view_patient_requests(request):
    group_name = 'StaffGroup'
    if request.user.is_superuser or request.user.groups.filter(name=group_name).exists():  # Check if admin
        patients = BloodRequest.objects.filter(status="pending")
        return render(request, 'view_patient_requests.html', {'patients': patients})  
    else:
        return redirect('/') 

@login_required
def approve_patient(request, patient_id):
    group_name = 'StaffGroup'
    if request.user.is_superuser or request.user.groups.filter(name=group_name).exists():  # Check if admin or exists in StaffGroup group
        patient = BloodRequest.objects.get(id=patient_id)
        patient.status = "approved"
        patient.save()
        messages.success(request, "Successfully approved!")
        return redirect('/dashboard')
    else:
        return redirect('/')  # Redirect non-admins

@login_required
def available_donors(request):
    # Assuming patient is logged in (check request.user)
    blood_type = request.user.blood_type  # Replace with how you store patient blood type
    donors = Donor.objects.filter(approved=True, blood_type=blood_type)
    return render(request, 'available_donors.html', {'donors': donors})

# Function to display existing blood donations
@login_required
def blood_stock(request):
    blood_donations = BloodDonation.objects.all().order_by('-donation_date')  # Order by recent donations
    context = {'blood_donations': blood_donations}
    return render(request, 'blood_stock.html', context)

# Function to handle blood donation approval
@login_required
def approve_donation(request, donation_id):
    try:
        # donation = BloodDonation.objects.get(pk=donation_id)
        quantity = 1
        donation = Donor.objects.get(pk=donation_id)
        donated, created = BloodDonation.objects.get_or_create(donor=donation.name,blood_type=donation.blood_type, quantity=quantity)
        donated.save()
        # Check if donation is not already approved
        if True:
            # Create new DonationCount record or update existing one
            donor, created = DonationCount.objects.get_or_create(id_donor=donation.id,donor=donation.name)
            donor.donation_count += 1
            donor.save()

            remove_from_requests(request, donation_id)
            
            messages.success(request, f'Blood donation from {donation.name} has been approved!')
            return redirect('view_donor_requests')  # Redirect to pending requests page (modify as needed)
        else:
            messages.warning(request, 'This donation has already been approved.')
            return redirect('view_donor_requests')  # Redirect to pending requests page (modify as needed)
    except BloodDonation.DoesNotExist:
        messages.error(request, 'Invalid donation ID.')
        return redirect('view_donor_requests')  # Redirect to pending requests page (modify as needed)

# Function for demonstration purposes (modify as needed)
@login_required
def remove_from_requests(request, donation_id):  # Placeholder, replace with appropriate logic
    try:
        donation = BloodDonation.objects.get(pk=donation_id)
        # Handle removal logic from blood request table (modify as needed)
        blood_request = Donor.objects.filter(name=donation.donor)
        blood_request.delete()
        messages.success(request, f'Blood donation request from {donation.donor} has been removed.')
        return redirect('view_donor_requests')  # Redirect to pending requests page (modify as needed)
    except BloodDonation.DoesNotExist:
        messages.error(request, 'Invalid donation ID.')
        return redirect('view_donor_requests')  # Redirect to pending requests page (modify as needed)

@login_required
def predict_donor_behavior(request):
    """
    Reads blood transfusion data from a CSV file, performs basic processing (replace with your prediction logic),
    and renders the output to the 'predict.html' template.
    """

    data_path = 'static/blood-transfusion-dataset/transfusion.csv'  # Replace with your actual CSV path
    try:
        # Use openpyxl or csv for data processing (modify as needed)
        with open(data_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)  # Assuming header row is not needed for your processing

         # Rename target column (assuming header row is present)
        data[0][data[0].index('whether he/she donated blood in March 2007')] = 'target'  # Modify indices if needed
        data = data[1:]  # Remove header row after renaming

        # Calculate target value counts with normalization and rounding
        target_counts = [i for i in data]  # Assuming target is in the first column after header removal
        # target_value_counts = [i for i in target_counts]  # Normalize and round
        data = []
        j = 1
        for i in target_counts:
            if j < 10:
                data.append(i)
            else:
                break
            j += 1
        target_value_counts = data  # Normalize and round

        counts = 1
        donors = BloodDonation.objects.all().order_by('-donation_date')
        count = DonationCount.objects.all()

        context = {'target_value_counts': target_value_counts , 'donors': donors , 'count' : count , 'counts':counts}
        return render(request, 'predict.html', context)

    except FileNotFoundError:
        context = {'error': 'Data file not found.'}
        return render(request, 'predict.html', context)

@login_required
def predict_donor(request, donor_id):
    count = DonationCount.objects.get(id_donor=donor_id)
    counts = DonationCount.objects.all()
    name_donor = count.donor
    donors = BloodDonation.objects.filter(donor=name_donor)
    frequency = 0
    money = 12500
    recency = 0

    for donor in donors:
        for i in counts:
            if i.donor == donor.donor:
                frequency += 1
    
    time_months = 6 * frequency
    donor_data = {
        'Recency (months)': recency,
        'Frequency (times)': frequency,
        'Time (months)': time_months,
        'money': money,
    }

    output = predict.predict_donation(donor_data)
    if output == 1.0:
        output = "Donor will donate blood when called upon"
        messages.success(request, output)
    else:
        output = "Donor will not donate blood when called upon"
        messages.error(request,output)
    return redirect('predict_donor_behavior')

@login_required
def send_email(request, donor_id):
    count = DonationCount.objects.get(id_donor=donor_id)
    name_donor = count.donor
    user = User.objects.get(username=name_donor)
    email = user.email    

    def send_email(sender_email, sender_password, receiver_email, subject, message):
        # Set up the SMTP server
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587  # For Gmail

        # Create a secure SSL context
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Login to the email server
        server.login(sender_email, sender_password)

        # Create a message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach the message to the email
        msg.attach(MIMEText(message, 'plain'))

        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())

        # Close the connection to the server
        server.quit()

    # Example usage
    sender_email = 'kiguru.joan1@students.jkuat.ac.ke'
    sender_password = 'iamJOHNKIGURU123#'
    receiver_email = email
    subject = 'Calling for donation'
    message = 'Kindly come and donate blood!'

    try:
        send_email(sender_email, sender_password, receiver_email, subject, message)
        output = "Successfully sent an email!"
        messages.success(request,output)
        return redirect('predict_donor_behavior')
    except:
        messages.error(request,"Bad credentials")
        return redirect('predict_donor_behavior')

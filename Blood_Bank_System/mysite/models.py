from django.contrib.auth.models import User, Group
from django.db import models
from PIL import Image
from distutils.command.upload import upload
from django.contrib.auth.models import User
from datetime import date, timedelta  # For calculating expiry date



class Donor(models.Model):
  name = models.CharField(max_length=255)
  blood_type = models.CharField(max_length=3)
  approved = models.BooleanField(default=False)

  def __str__(self):
    return f"{self.name} ({self.blood_type}) - {'Approved' if self.approved else 'Pending Approval'}"

class BloodDonation(models.Model):
    donor = models.CharField(max_length=255)
    blood_type = models.CharField(max_length=3)
    quantity = models.PositiveIntegerField()  # Store quantity in milliliters (ml)
    donation_date = models.DateField(default=date.today)  # Set default to today's date
    expiry_date = models.DateField(blank=True, null=True)  # Calculated upon saving

    def save(self, *args, **kwargs):
        # Calculate expiry date (adjust based on blood type shelf life)
        self.expiry_date = self.donation_date + timedelta(days=42)  # Adjust for actual shelf life
        super().save(*args, **kwargs)  # Call the parent class save method

    def __str__(self):
        return f"{self.donor} - {self.blood_type} ({self.quantity} ml)"

class DonationCount(models.Model):
    id_donor = models.PositiveIntegerField()
    donor = models.CharField(max_length=255)
    donation_count = models.PositiveIntegerField(default=0)  # Track total number of donations

    def __str__(self):
        return f"{self.donor.first_name} {self.donor.last_name} - Donations: {self.donation_count}"

class BloodRequest(models.Model):
  patient = models.ForeignKey(User, on_delete=models.CASCADE)
  blood_type = models.CharField(max_length=3)
  role = models.CharField(max_length=20, choices=(('donor', 'Donor'), ('patient', 'Patient'), ('staff','Staff' )), default='patient')
  request_date = models.DateTimeField(auto_now_add=True)  
  status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('approved', 'Approved'), ('fulfilled', 'Fulfilled')), default='pending')

  def __str__(self):
    return f"Blood request by {self.patient.username} for {self.blood_type} blood (Role: {self.role}, Status: {self.status})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/profile_pics', default='static/profile_pics/default.jpg')

    def __str__(self):
        return f'{self.user.username} Profile'

# The method is used to resive the profile photos uploaded by users
# It uses the save() method from parent class and reuses the method to save image once it has been resized
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        try:
          img = Image.open(self.image.path)
        except:
          img = Image.open("static/profile_pics/default.jpg")
        if img.height > 350 or img.width > 350:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
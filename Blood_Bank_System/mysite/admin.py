from django.contrib import admin
from . models import (BloodRequest, Donor, Profile, BloodDonation, DonationCount)
# Register your models here.
# create a request for functionality :)
admin.site.register(BloodRequest)
admin.site.register(Donor)
admin.site.register(Profile)
admin.site.register(BloodDonation)
admin.site.register(DonationCount)
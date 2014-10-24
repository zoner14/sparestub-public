# Standard Python modules

#Django
from utils.models import TimeStampedModel
from django.db import models

#SparStub imports
from registration.models import User
from .settings import ticket_model_settings
from locations.models import Location

class Ticket(TimeStampedModel):
    poster = models.ForeignKey(User,
                               blank=False,
                               null=False,
                               db_index=True,
                               related_name='poster',
                               )

    bidders = models.ForeignKey(User,
                                blank=True,
                                null=True,
                                db_index=True,
                                related_name='bidders',
                                )

    price = models.IntegerField(blank=False)

    title = models.CharField(blank=False,
                             max_length=ticket_model_settings.get('TITLE_MAX_LENGTH'),
                             )

    contents = models.TextField(blank=True,
                                default='',
                                max_length=ticket_model_settings.get('CONTENT_MAX_LENGTH'))

    # When does the event start?
    start_datetime = models.DateTimeField(blank=False)

    # The city and state that the user originally entered in the form.
    location_raw = models.CharField(max_length=254)  # Keep the city, state combo around just in case we are
                                                     # we need to debug

    # The system tries to map the raw input form the user to a location record. That's what this is.
    location = models.IntegerField(Location)  # We are going to map the inputted city, state to a zipcode

    type = models.CharField(max_length=1,
                            choices=ticket_model_settings.get('TICKET_TYPES'))

    payment_method = models.CharField(max_length=1,
                                      choices=ticket_model_settings.get('PAYMENT_METHODS'))

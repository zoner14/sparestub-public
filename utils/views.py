# Django Imports
from django.forms import ValidationError

# SpareStub Imports
from .networking import ajax_http
from locations.models import Location
from registration.models import User


def valid_username(request):
    """
    Return true if a username is valid and false if it is not. Used exclusively for form validation.
    """
    username = request.GET.get('username')
    user = request.user
    try:
        user.user_profile.valid_username(username)
        valid = True
    except ValidationError:
        valid = False

    return ajax_http(True,
                     extra_json={'valid': valid})


def valid_zip_code(request):
    """
    There are a number of 5 digit strings that do not map to a real zip_code.
    Return true for 5 digit strings that do map to zip_codes and false otherwise.
    Used exclusively for form validation.
    """
    zip_code = request.GET.get('zip_code')
    try:
        Location.valid_zipcode(zip_code)
        valid = True
    except ValidationError:
        valid = False

    return ajax_http(True,
                     extra_json={'valid': valid})


def valid_email(request):
    """
    Return true if the email is valid and false otherwise. Used exclusively for form validation.
    """

    email = request.GET.get('email')
    user = request.user
    try:
        user.valid_email(email)
        valid = True
    except ValidationError:
        valid = False

    return ajax_http(True,
                     extra_json={'valid': valid})

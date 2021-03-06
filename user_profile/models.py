# Python core modules
import logging
import re

# Django core modules
from django.db import models
from django.forms import ValidationError
from django.core.urlresolvers import reverse

# SpareStub imports
from utils.models import TimeStampedModel
from .settings import profile_question_model_settings, profile_answer_model_settings, user_profile_model_settings


class UserProfilerManager(models.Manager):

    def create_user_profile(self, first_name=None, last_name=None, profile_views=0):
        """
        Creates a user profile given a particular first and last name.
        The way the system exists now, profile_views will never have a value when the profile is created.
        """

        username = self.make_username(first_name, last_name)

        user_profile = self.model(username=username,
                                  profile_views=profile_views,
                                  )

        user_profile.save()

        # Make sure a blank profile answer object exists for every question
        for profile_question in ProfileQuestion.objects.all():
            ProfileAnswer.objects.create_profile_answer(user_profile, profile_question, '')

        return user_profile


    @staticmethod
    def make_username(first_name, last_name):
        # Make the usernames title case and remove any spaces.
        # This avoids having spaces that need escaping in the user profile url.
        first_name, last_name = first_name.title().replace(' ', ''), last_name.title().replace(' ', '')

        # Try to make the url equal to the users first and last names concatenated together
        potential_username = first_name + last_name
        if not UserProfile.user_profile_exists(potential_username):
            return potential_username

        # Make the user's url equal to his email with an appended number
        #TODO we really need to make sure this returns something
        number_to_append = 100
        while number_to_append < 100000:  # Let's make this finite just for safety
            potential_username = potential_username + str(number_to_append)
            if not UserProfile.user_profile_exists(potential_username):
                return potential_username
            number_to_append += 1

        logging.error("profile.html url did not generate properly for input user profile {} {}".
                      format(first_name, last_name))
        return None


class UserProfile(TimeStampedModel):
    #The username must be composed of numbers and upper and lower case letters
    username_regex = re.compile(r'^[a-zA-Z0-9]+$')


    # This is set in the User manager as opposed to here. This is because we need user email/name info. to create the username,
    # but the UserProfile needs to be created before the User because the User.user_profile cannot be null.
    username = models.CharField(max_length=user_profile_model_settings.get('USERNAME_MAX_LENGTH'),
                                # and last name
                                db_index=True,
                                unique=True,
                                )

    # The number of times that this person's profile.html has been viewed by others.
    profile_views = models.IntegerField(default=0)

    objects = UserProfilerManager()

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('view_profile', kwargs={'username': self.username})

    def valid_username(self, username):
        # Make sure that the inputted username is in the correct format
        if not re.match(UserProfile.username_regex, username):
            raise ValidationError("Your username can only contain letters and numbers.", code="bad username format")

        # If the submitted username is the same as the current one, then validation is complete since the current
        # username has been validated before. But do the regex check first anyway to save DB hits on username changes.
        if self.username == username:
            return username

        # Make sure that another user does not already have this username
        if UserProfile.user_profile_exists(username):
            raise ValidationError('Username already exists. Please choose another')

        return username

    @staticmethod
    def user_profile_exists(username):
        if UserProfile.objects.filter(username=username):
            return True
        return False

    @staticmethod
    def get_user_profile_from_username(username):
        profile = UserProfile.objects.filter(username=username)
        if profile:
            return profile[0]
        return None


class ProfileQuestionManager(models.Manager):

    def create_profile_question(self, question):
        """
        Creates a profile question record using the given input
        """

        profile_question = self.model(question=question)
        profile_question.save()
        return profile_question


class ProfileQuestion(models.Model):
    question = models.CharField(blank=False,
                                max_length=profile_question_model_settings.get('QUESTION_MAX_LENGTH'),
                                )

    objects = ProfileQuestionManager()

    def __str__(self):
        return self.question


class ProfileAnswerManager(models.Manager):

    def create_profile_answer(self, user, question, answer):
        """
        Creates a profile answer record using the given input
        """

        # If a User model was passed in instead of a UserProfile model, do the conversion
        try:
            user = user.user_profile
        except AttributeError:
            pass

        profile_answer = self.model(user_profile=user,
                                    question=question,
                                    answer=answer)

        profile_answer.save()
        return profile_answer


class ProfileAnswer(models.Model):
    user_profile = models.ForeignKey(UserProfile,
                                     blank=False,
                                     null=False,
                                     )

    question = models.ForeignKey(ProfileQuestion,
                                 blank=False,
                                 null=False
                                 )

    answer = models.TextField(blank=False,
                              null=False,
                              default='',
                              max_length=profile_answer_model_settings.get('ANSWER_MAX_LENGTH'),
                              )

    objects = ProfileAnswerManager()

    @staticmethod
    def get_answer(user, question):
        """
        Gets a particular user's answer to a specific question.
        """

        answer = ProfileAnswer.objects.filter(user_profile=user.user_profile, question=question)
        # This should always be true since the create_user_profile function creates answers for every question for
        # every user_profile created.
        if answer:
            return answer[0]
        return None

    def __str__(self):
        return "Question: {} | Answer: {}".format(self.question.id, self.answer)
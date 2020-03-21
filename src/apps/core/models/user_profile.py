from django.db import models
from logging import getLogger
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from djchoices import DjangoChoices, ChoiceItem

logger = getLogger(__name__)


class UserTypes(DjangoChoices):
    """
    Allowed user types for users in the platform
    """
    admin = ChoiceItem(0)
    customer = ChoiceItem(1)
    commerce = ChoiceItem(2)


class UserProfile(models.Model):
    """
    Model for add extra parameters to the users in the platform
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.IntegerField(
        choices=UserTypes.choices, default=UserTypes.customer, null=True, blank=True,
        help_text="Select one of the user types for the platform.", verbose_name="User type"
    )

    def __str__(self):
        return f'{self.user} - {UserTypes.attributes[self.user_type]}'

    def change_user_type(self, new_user_type: int = 0):
        """
        Function to update the user type
        :param new_user_type:
        :return:
        """
        logger.info(
            f"The user {self}, will change the user type from '{UserTypes.attributes[self.user_type]}' to '{UserTypes.attributes[new_user_type]}'."
        )
        self.user_type = new_user_type
        self.save()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Function used to create the user profile when create the user
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()

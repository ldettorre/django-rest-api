from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin

# AbstractBaseUser provides the core implementation of a user model,
# including hashed passwords and tokenized password resets.
# PermissionsMixin is an abstract model that will give us all the methods
# and db fields to support Djangos permission model.


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        '''This creates and saves a new user.'''
        '''**extra_fields allows us to include additional fields later on'''
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        '''Creates and saves a new superuser'''
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    ''' This is a Custom User Model that supports email instead of username.'''
    email = models.EmailField(max_length=250, unique=True)
    name = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

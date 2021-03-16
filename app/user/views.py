# from django.shortcuts import render
from user.serializers import UserSerializer
from rest_framework import generics


class CreateUserView(generics.CreateAPIView):
    '''creates a new user in the system'''
    serializer_class = UserSerializer

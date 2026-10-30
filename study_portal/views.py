from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import AllowAny

from serilizers import RegisterSerializer
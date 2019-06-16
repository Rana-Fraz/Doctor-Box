from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
# from rest_framework import request


@api_view(['POST'])
def emailVer(request,):
    if User.objects.filter(email=request.data['email']).exists():
        return Response({'status': False, 'Message': 'Email Already Exist'}, status=status.HTTP_200_OK)
    else:
        return Response({'status': True, 'Message': 'No email exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def usernameVer(request,):
    if User.objects.filter(username=request.data['username']).exists():
        return Response({'status': False, 'Message': 'Username Already Exist'}, status=status.HTTP_200_OK)
    else:
        return Response({'status': True, 'Message': 'No username exist'}, status=status.HTTP_404_NOT_FOUND)
@csrf_exempt
@api_view(['POST'])
def user_register(request,):
    if request.method=='POST':
        dic=request.data
        email = request.data['email']
        username = request.data['username']
        password = request.data['password']
        firstname = request.data['firstname']
        lastname = request.data['lastname']
        un = User.objects.filter(username=username).exists()
        em = User.objects.filter(email=email).exists()
        if em and un:
            return Response({'Message': 'Username and Email already Exist'}, status=status.HTTP_404_NOT_FOUND)
        elif un:
            return Response({'Message': 'Username already Exist'}, status=status.HTTP_404_NOT_FOUND)
        elif em:
            return Response({'Message': 'Email already Exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            min_length = 8
            if len(password) < min_length:
                msg = 'Password must be at least %s characters long.' % (str(min_length))
                return Response({"Message": msg}, status=status.HTTP_400_BAD_REQUEST)

            # check for digit
            if sum(c.isdigit() for c in password) < 1:
                msg = 'Password must contain at least 1 number.'
                return Response({"Message": msg}, status=status.HTTP_400_BAD_REQUEST)

            # check for uppercase letter
            if not any(c.isupper() for c in password):
                msg = 'Password must contain at least 1 uppercase letter.'
                return Response({"Message": msg}, status=status.HTTP_400_BAD_REQUEST)

            # check for lowercase letter
            if not any(c.islower() for c in password):
                msg = 'Password must contain at least 1 lowercase letter.'
                return Response({"Message": msg}, status=status.HTTP_400_BAD_REQUEST)
        try:
            User.objects.create_user(username=dic['username'],password=dic['password'],email=dic['email'],first_name=dic['firstname'],
                                      last_name=dic['lastname'],is_staff=dic['doctor'])
            return Response({'Message':'Registered Successfully'},status=status.HTTP_200_OK)
        except:
            return Response({'Message':'Something went wrong'},status=status.HTTP_400_BAD_REQUEST)

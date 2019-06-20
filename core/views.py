from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
import random
import string
from django.core.mail import EmailMessage

from core.models import profile
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

def send_activation_code_function(register_obj):
    print ('activation')

    # register_obj = Contractor.objects.get(user=user)
    secret_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(200))
    key = {
        'name':register_obj.user.first_name,'code':secret_id
    }

    message = get_template('Email Activation.html').render(key)
    email = EmailMessage('Email Confirmation', message, to=[register_obj.user.email])
    email.content_subtype = 'html'
    email.send()
    register_obj.authentication_code = secret_id
    register_obj.save()
    return Response({'Message': 'Email Send'}, status=status.HTTP_200_OK)

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
        # date_of_birth=request.data['date_of_birth']
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
        # try:
        user=User.objects.create_user(username=dic['username'],password=dic['password'],email=dic['email'],first_name=dic['firstname'],
                                  last_name=dic['lastname'],is_staff=dic['doctor'])
        register_obj = profile()
        register_obj.user_id = user.id
        # register_obj.date_on_birth = date_of_birth
        register_obj.save()
        send_activation_code_function(register_obj)

        return Response({'Message':'Registered Successfully'},status=status.HTTP_200_OK)
        # except:
            # return Response({'Message':'Something went wrong'},status=status.HTTP_403_FORBIDDEN)
@csrf_exempt
@api_view(['POST'])
def forget_password(request):
    if request.method == 'POST':

        email = request.data['email']
        # email=request.data.get('username', False)
        # obj=User.objects.get(email=email)
        # # email=obj.email
        # print(email)
        if not User.objects.filter(email=email).exists():
            return Response({'Message': 'User Does not exist', 'status': False}, status.HTTP_404_NOT_FOUND)
            # return Response('Email Does not Exist! Please SignUp/Register First', status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(email=email)
            profile2 = profile.objects.get(user=user)
        except profile.DoesNotExist:
            return Response({'Message': 'Profile does not exist', 'status': False}, status.HTTP_404_NOT_FOUND)

        print (profile2.is_active)
        if profile2.is_active:
            reset_email = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in
                range(200))
            while profile.objects.filter(authentication_code=reset_email).exists():
                reset_email = ''.join(
                    random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _
                    in
                    range(100))
            key = {
                'name': user.first_name, 'code': reset_email
            }
            message = get_template('Reset Password.html').render(key)
            email = EmailMessage('Email Confirmation', message, to=[email])
            email.content_subtype = 'html'
            email.send()
            profile2.authentication_code = reset_email
            profile2.save()
            return Response({'Message': 'Password reset link has been sent to your email'}, status=status.HTTP_200_OK)
        else:
            return Response({'Message': 'Unauthenticated User.', 'status': False},
                            status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def activate_account(request, code):
    if request.method == 'POST':
        try:
            if (profile.objects.filter(authentication_code=code).exists()):

                reg = profile.objects.get(authentication_code=code)
                if (reg.isActivat==True):
                    return Response({'Message': 'Account Already Activated'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    reg.isActivat = True
                    reg.save()
                    return Response({'Message': 'Account Activated'}, status=status.HTTP_200_OK)
            else:
                return Response({'Message': 'Error '}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'Message': 'Error '}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_authentication(request):
    if request.method == 'POST':
        username=request.data['username']
        password=request.data['password']
        try:
            user = User.objects.get(username=username)
        except:
            return Response({'Message': 'Invalid username'}, status=status.HTTP_401_UNAUTHORIZED)
        # print("Success", user.username)
        success = user.check_password(password)

        if success is not False:
            user = User.objects.get(username=username)
            profile2 = profile.objects.get(user=user.id)
            if profile.is_active == True:
                return Response({'Message': 'Account is Active','doctor':user.is_staff },status=status.HTTP_200_OK)

            else:
                return Response({'Message': 'Account is Inactive'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Message': 'Username or Password are wrong'}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.conf import settings
from twilio.rest import Client

class SendOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone')

        # Send OTP using Twilio Verify
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        verification = client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
            to=phone_number,
            channel='sms'
        )

        if verification.status == 'pending':
            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to send OTP'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOtpView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone_number = request.data.get('phone')
        entered_otp = request.data.get('otp')

        # Verify OTP with Twilio Verify
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        verification_check = client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID).verification_checks.create(
            to=phone_number,
            code=entered_otp
        )

        if verification_check.status == 'approved':
            # OTP is correct, get or create user
            user, created = User.objects.get_or_create(username=phone_number)

            # Create or get token for the user
            token, created = Token.objects.get_or_create(user=user)

            # Return relevant user data and the token
            user_data = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }

            return Response({'user': user_data, 'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
class UserViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def update_profile(self, request):
        user = request.user

        first_name = request.data.get('first_name', user.first_name)
        last_name = request.data.get('last_name', user.last_name)
        email = request.data.get('email', user.email)

        # Update the user's information
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Return the updated user data and the token
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        token, created = Token.objects.get_or_create(user=user)

        return Response({'user': user_data, 'token': token.key}, status=status.HTTP_200_OK)

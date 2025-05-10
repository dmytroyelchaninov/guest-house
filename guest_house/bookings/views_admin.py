from django.conf import settings
from django.core import signing
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

TOKEN_SALT = settings.TOKEN_SALT
COOKIE_NAME = settings.COOKIE_NAME
MAX_AGE     = settings.MAX_AGE

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    if request.data.get('key') != settings.HOTEL_ADMIN_KEY:
        return Response({'detail': 'Forbidden'}, status=403)
    token = signing.dumps({'admin': True}, salt=TOKEN_SALT)
    resp = Response({'detail': 'Logged in'})
    resp.set_cookie(
        COOKIE_NAME, token, httponly=True, max_age=MAX_AGE,
        secure=not settings.DEBUG, samesite='Lax')
    return resp

@csrf_exempt
@api_view(['POST'])
def admin_logout(request):
    resp = Response({'detail': 'Logged out'})
    resp.delete_cookie(COOKIE_NAME)
    return resp

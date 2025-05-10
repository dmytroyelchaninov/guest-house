import logging
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

logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    logger.debug('admin_login attempt with body %s', request.data)
    if request.data.get('key') != settings.HOTEL_ADMIN_KEY:
        logger.warning('Invalid admin key: %s', request.data.get('key'))
        return Response({'detail': 'Forbidden'}, status=403)
    token = signing.dumps({'admin': True}, salt=TOKEN_SALT)
    resp = Response({'detail': 'Logged in'})
    resp.set_cookie(
        COOKIE_NAME, token,
        httponly=True, max_age=MAX_AGE,
        secure=not settings.DEBUG,
        samesite='Lax'
    )
    logger.info('Admin logged in, cookie set')
    return resp

@csrf_exempt
@api_view(['POST'])
def admin_logout(request):
    logger.debug('admin_logout called')
    resp = Response({'detail': 'Logged out'})
    resp.delete_cookie(COOKIE_NAME)
    logger.info('Admin logged out, cookie deleted')
    return resp


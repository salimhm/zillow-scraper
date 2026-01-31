"""
Custom exception handling for the API.
"""

import logging
import traceback
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from scrapers.base import NotFoundException, BlockedException, ScraperException

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that converts scraper exceptions to API responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        return response
    
    # Handle scraper-specific exceptions (expected errors - minimal logging)
    if isinstance(exc, NotFoundException):
        # Expected error - just log a simple warning, no stack trace
        logger.info(f"404: {exc}")
        return Response(
            {
                'error': 'Not Found',
                'message': str(exc),
                'status_code': 404,
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if isinstance(exc, BlockedException):
        logger.warning(f"503: {exc}")
        return Response(
            {
                'error': 'Service Unavailable',
                'message': str(exc) if settings.DEBUG else 'The request was blocked. Please try again later.',
                'status_code': 503,
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    if isinstance(exc, ScraperException):
        error_msg = str(exc).lower()
        
        # Check if this is a wrapped BlockedException (403 Forbidden)
        if 'blocked' in error_msg or '403' in error_msg or 'forbidden' in error_msg:
            logger.warning(f"503: {exc}")
            return Response(
                {
                    'error': 'Service Unavailable',
                    'message': 'The request was blocked by the target site. Please try again later or use a different proxy.',
                    'status_code': 503,
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        logger.warning(f"500: {exc}")
        return Response(
            {
                'error': 'Internal Server Error',
                'message': str(exc) if settings.DEBUG else 'An error occurred while processing your request.',
                'status_code': 500,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # For any other unhandled exceptions
    logger.exception(f"Unhandled exception: {exc}")
    return Response(
        {
            'error': 'Internal Server Error',
            'message': str(exc) if settings.DEBUG else 'An unexpected error occurred.',
            'status_code': 500,
            'exception_type': type(exc).__name__ if settings.DEBUG else None,
            'details': traceback.format_exc() if settings.DEBUG else None,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

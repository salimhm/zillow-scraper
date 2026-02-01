"""
Serializers for the Zillow scraper API.
"""

from rest_framework import serializers


class AgentSerializer(serializers.Serializer):
    """Serializer for agent data."""
    
    name = serializers.CharField()
    url = serializers.CharField()
    photo_url = serializers.CharField(required=False, allow_blank=True)
    brokerage = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    rating = serializers.FloatField(required=False, allow_null=True)
    reviews_count = serializers.IntegerField(required=False, allow_null=True)
    sales_count = serializers.IntegerField(required=False, allow_null=True)
    price_range = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_team = serializers.BooleanField(required=False, default=False)
    bio = serializers.CharField(required=False, allow_blank=True)


class PropertySerializer(serializers.Serializer):
    """Serializer for property data."""
    
    zpid = serializers.IntegerField(required=False, allow_null=True)
    address = serializers.CharField()
    url = serializers.CharField(required=False, allow_blank=True)
    photo_url = serializers.CharField(required=False, allow_blank=True)
    price = serializers.FloatField(required=False, allow_null=True)
    beds = serializers.IntegerField(required=False, allow_null=True)
    baths = serializers.IntegerField(required=False, allow_null=True)
    sqft = serializers.IntegerField(required=False, allow_null=True)
    property_type = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    brokerage = serializers.CharField(required=False, allow_blank=True)


class ReviewSerializer(serializers.Serializer):
    """Serializer for review data."""
    
    zuid = serializers.CharField()
    rating = serializers.IntegerField()
    review = serializers.CharField()
    reviewer_name = serializers.CharField(required=False, allow_blank=True)
    date = serializers.CharField(required=False, allow_blank=True)
    transaction_type = serializers.CharField(required=False, allow_blank=True)


class PaginationMetadataSerializer(serializers.Serializer):
    """Serializer for pagination metadata."""
    
    total_results = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    current_page = serializers.IntegerField()
    per_page = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()



class AutocompleteSuggestionSerializer(serializers.Serializer):
    """Serializer for autocomplete suggestions."""
    
    display = serializers.CharField()
    type = serializers.CharField()
    id = serializers.CharField(required=False, allow_blank=True)


class ApartmentDetailsSerializer(serializers.Serializer):
    """Serializer for apartment details."""
    
    url = serializers.CharField()
    name = serializers.CharField()
    address = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    units = serializers.ListField(required=False, default=list)
    amenities = serializers.ListField(required=False, default=list)
    photos = serializers.ListField(required=False, default=list)


class ErrorSerializer(serializers.Serializer):
    """Serializer for error responses."""
    
    error = serializers.CharField()
    message = serializers.CharField()
    status_code = serializers.IntegerField()

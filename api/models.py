"""
Data models for the Zillow scraper API.

Note: These models are primarily used for data validation and serialization.
Since this is a real-time scraper, data is not stored in the database.
"""

from django.db import models


class Agent(models.Model):
    """Model representing a Zillow real estate agent."""
    
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    location = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    reviews_count = models.IntegerField(null=True, blank=True)
    sales_count = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)
    photo_url = models.URLField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'
    
    def __str__(self):
        return self.name


class Property(models.Model):
    """Model representing a Zillow property listing."""
    
    zpid = models.BigIntegerField(unique=True, null=True, blank=True)
    address = models.CharField(max_length=500)
    url = models.URLField(max_length=500)
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    beds = models.IntegerField(null=True, blank=True)
    baths = models.IntegerField(null=True, blank=True)
    sqft = models.IntegerField(null=True, blank=True)
    property_type = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
    
    def __str__(self):
        return f"{self.address} - ${self.price}"


class Review(models.Model):
    """Model representing a Zillow agent review."""
    
    zuid = models.CharField(max_length=100)
    rating = models.IntegerField()
    review = models.TextField()
    reviewer_name = models.CharField(max_length=255, blank=True)
    date = models.CharField(max_length=50, blank=True)
    transaction_type = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
    
    def __str__(self):
        return f"Review by {self.reviewer_name or self.zuid} - {self.rating}/5"

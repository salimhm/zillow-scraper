from django.contrib import admin
from .models import Agent, Property, Review


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'rating', 'reviews_count', 'created_at']
    search_fields = ['name', 'location']
    list_filter = ['location', 'created_at']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['address', 'price', 'beds', 'baths', 'sqft', 'status', 'created_at']
    search_fields = ['address', 'zpid']
    list_filter = ['status', 'property_type', 'created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer_name', 'rating', 'date', 'created_at']
    search_fields = ['reviewer_name', 'review']
    list_filter = ['rating', 'created_at']

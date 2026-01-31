"""
URL configuration for the API app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Agent endpoints
    path('agentBylocation', views.agent_by_location, name='agent-by-location'),
    path('agentInfo', views.agent_info, name='agent-info'),
    path('agentReviews', views.agent_reviews, name='agent-reviews'),
    path('agentForSaleProperties', views.agent_for_sale_properties, name='agent-for-sale'),
    path('agentForRentProperties', views.agent_for_rent_properties, name='agent-for-rent'),
    path('agentSoldProperties', views.agent_sold_properties, name='agent-sold'),
    
    # Property search endpoints
    path('bylocation', views.by_location, name='by-location'),
    path('bycoordinates', views.by_coordinates, name='by-coordinates'),
    path('bymapbounds', views.by_map_bounds, name='by-map-bounds'),
    path('bymlsid', views.by_mls_id, name='by-mls-id'),
    path('bypolygon', views.by_polygon, name='by-polygon'),
    path('byurl', views.by_url, name='by-url'),
    
    # Other endpoints
    path('apartmentDetails', views.apartment_details, name='apartment-details'),
    path('autocomplete', views.autocomplete, name='autocomplete'),
]


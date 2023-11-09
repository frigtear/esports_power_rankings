from django.urls import path
from rankings import views

urlpatterns = [path("",views.display_rankings,name="rankings"),
               path('teams/<int:team_id>/',views.display_team_information,name='team_info'),
               path('players/<int:player_id>/',views.display_player_information,name='player_info'),
               path('regions/<str:region_name>/',views.display_region_information,name='region_info')]


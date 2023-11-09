from django.http import Http404
from .models import Team,Player,Region
from django.shortcuts import render,get_object_or_404
from django.views.decorators.cache import cache_control


# Stop browser from caching static files for easy front end development
@cache_control(private=True, no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def display_rankings(request):
    context = {'teams':Team.objects.order_by("-skill"),'regions':Region.objects.order_by('-skill')}
    return render(request,'rankings/index.html',context)

@cache_control(private=True, no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def display_team_information(request,team_id):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        raise Http404("No team could be found")

    roster = Player.objects.filter(team=team_id).order_by('-games_played', '-skill')[:5]
    return render(request, 'rankings/team_info.html',{'team':team,'roster':roster})

@cache_control(private=True, no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def display_player_information(request,player_id):
    player = get_object_or_404(Player,pk=player_id)
    return render(request,"rankings/player_info.html",{'player':player})


def display_region_information(request,region_name):
    region = get_object_or_404(Region,pk=region_name)
    return render(request, "rankings/region_info.html",{'region':region})
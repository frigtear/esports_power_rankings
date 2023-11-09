from django.db import models

maxLength = 200


class Region(models.Model):
    name = models.CharField(primary_key=True,max_length=maxLength)
    skill = models.IntegerField(default=None)
    wins = models.IntegerField(default=None)
    losses = models.IntegerField(default=None)
    scaledWR = models.IntegerField(default=None)
    gamesPlayed = models.IntegerField(default=None)
    scaledGamesPlayed = models.IntegerField(default=None)

    def __str__(self):
        return self.name
# Create your models here.
class Team(models.Model):
    team_id = models.IntegerField(primary_key=True,default=None)
    name = models.CharField(max_length=maxLength,default=None)
    skill = models.FloatField(default=-1,null=True)
    rank = models.IntegerField(default=None)
    level = models.IntegerField(default=1)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)

    scaledLevel = models.IntegerField(default=-1)
    avgPlayerSkill = models.IntegerField(default=0)
    scaledPlayerSkill = models.IntegerField(default=-1)
    totalPlayerSkill = models.IntegerField(default=0)
    youngWins = models.IntegerField(default=0)
    youngLosses = models.IntegerField(default=0)
    scaledYoungWR = models.IntegerField(default=-1)
    agedWins = models.IntegerField(default=0)
    agedLosses = models.IntegerField(default=0)
    scaledAgedWR = models.IntegerField(default=-1)
    oldWins = models.IntegerField(default=0)
    oldLosses = models.IntegerField(default=0)
    scaledOldWR = models.IntegerField(default=-1)
    ancientWins = models.IntegerField(default=0)
    ancientLosses = models.IntegerField(default=0)
    scaledAncientWR = models.IntegerField(default=-1)


    def __str__(self):
        return self.name


class Player(models.Model):
    player_id = models.IntegerField(primary_key=True,default=None)
    first_name = models.CharField(max_length=maxLength,default=None,null=True)
    last_name = models.CharField(max_length=maxLength,default=None,null=True)
    handle = models.CharField(max_length=maxLength, default=None,null=True)
    skill = models.IntegerField(default=None,null=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    scaledWR = models.IntegerField(default=-1)
    kills = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    scaledKD = models.IntegerField(default=-1)
    avgTD= models.IntegerField(default=0)
    scaledTD = models.IntegerField(default=-1)
    avgFB = models.IntegerField(default=0)
    scaledFB = models.IntegerField(default=-1)
    games_played = models.IntegerField(default=0)
    scaledGP = models.IntegerField(default=-1)

    def __str__(self):
        return self.handle

from django.db import models

class FPLTeam(models.Model):
    team_id = models.IntegerField(unique=True)  # Corresponds to 'id' in standings
    manager_name = models.CharField(max_length=255)  # Manager's name
    team_name = models.CharField(max_length=255)  # Team name
    rank = models.IntegerField()  # Current rank in the league

    def __str__(self):
        return f"{self.team_name} - {self.manager_name}"


from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    signup_confirmation = models.BooleanField(default=False)


class Tournament(models.Model):
    name = models.CharField(max_length=64)
    discipline = models.CharField(max_length=64)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    limit = models.IntegerField()
    deadline = models.DateField()
    num_of_seeded = models.IntegerField(default=0)
    num_of_registered = models.IntegerField(default=0)
    localization = models.CharField(max_length=128, default='')
    draw_calculated = models.BooleanField(default=False)


class Sponsor(models.Model):
    name = models.CharField(max_length=64)
    logo = models.ImageField(upload_to='logos')


class Sponsoring(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("tournament", "sponsor"),)


class Participation(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    license = models.CharField(max_length=64)
    ranking = models.IntegerField()
    seed = models.IntegerField(default=-1)

    class Meta:
        unique_together = (("tournament", "user"),)

        constraints = [
            models.UniqueConstraint(fields=['tournament', 'license'], name='license unique'),
            models.UniqueConstraint(fields=['tournament', 'ranking'], name='ranking unique')
        ]


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user1 = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='user1')
    user2 = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='user2')
    user1_seed = models.IntegerField(default=-1)
    user2_seed = models.IntegerField(default=-1)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    stage = models.IntegerField(default=1)
    stage_name = models.CharField(max_length=64, default="1st round")
    number = models.IntegerField(default=1)
    finished = models.BooleanField(default=False)
    user1_decision = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='user1_decision')
    user2_decision = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='user2_decision')

    class Meta:
        unique_together = (("tournament", "number"),)
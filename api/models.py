from pyexpat import model
from helpers.models import TrackingModel
from authentication.models import User
from django.db import models

class Todo(TrackingModel):
    title = models.CharField(max_length=225)
    desc = models.TextField()
    is_complete = models.BooleanField(default=False)
    owner = models.ForeignKey(to=User,on_delete=models.CASCADE)

    def __str__(self):
        return self.title
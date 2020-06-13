from django.db import models

# Create your models here.

class Regestration(models.Model):
    name = models.CharField(max_length=100,default="")
    email = models.EmailField(max_length=254,default="")
    amount = models.PositiveIntegerField(default=0)
    m_no = models.PositiveIntegerField(default=0)
    password = models.CharField(max_length=100,default="")
    index = models.PositiveIntegerField(default=0)
    u_hash = models.CharField(max_length=200,default="")
    nonce = models.PositiveIntegerField(default=0)
    bitcoin = models.FloatField(default=0.0,max_length=10)
    u_prev_hash = models.CharField(max_length=200,default="")
    timestamp = models.CharField(max_length=100,default="")

    def __str__(self):
        return self.name

class feedback(models.Model):
    sender_name = models.CharField(max_length=100,default="")
    sender_email = models.CharField(max_length=100,default="")
    feedback_topic = models.CharField(max_length=100,default="")
    feedback = models.TextField()

    def __str__(self):
        return self.feedback_topic

class Transaction(models.Model):
    user = models.ForeignKey(Regestration,on_delete=models.CASCADE)
    sender = models.CharField(max_length=500,default="")
    receiver = models.CharField(max_length=500,default="") 
    amount = models.FloatField(default=0.0)
    bitcoin = models.FloatField(default=0.0,max_length=10)
    time = models.CharField(max_length=200,default="")
    cut_money = models.FloatField(default=0.0)
    send_notes = models.TextField(default="")
    receive_notes = models.TextField(default="")


    def __str__(self):
        return self.sender

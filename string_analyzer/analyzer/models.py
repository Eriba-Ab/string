from django.db import models


class StringEntry(models.Model):
	id = models.CharField(max_length=64, primary_key=True) # sha256 hash
	value = models.TextField(unique=True)
	properties = models.JSONField()
	created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
	return self.value
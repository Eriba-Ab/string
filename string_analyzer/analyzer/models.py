from django.db import models
import hashlib
from collections import Counter


class AnalyzedString(models.Model):
	id = models.CharField(max_length=64, primary_key=True)
	value = models.TextField(unique=True)
	length = models.IntegerField()
	is_palindrome = models.BooleanField()
	unique_characters = models.IntegerField()
	word_count = models.IntegerField()
	sha256_hash = models.CharField(max_length=64)
	character_frequency_map = models.JSONField()
	created_at = models.DateTimeField(auto_now_add=True)


	@staticmethod
	def analyze(value: str):
		lowered = value.lower()
		freq = dict(Counter(value))
		sha = hashlib.sha256(value.encode()).hexdigest()
		return dict(
			length=len(value),
			is_palindrome=(lowered == lowered[::-1]),
			unique_characters=len(set(value)),
			word_count=len(value.split()),
			sha256_hash=sha,
			character_frequency_map=freq,
		)


	@classmethod
	def create_or_raise(cls, value: str):
		props = cls.analyze(value)
		if cls.objects.filter(id=props['sha256_hash']).exists():
			raise ValueError('exists')
		obj = cls(
			id=props['sha256_hash'],
			value=value,
			**props,
		)
		obj.save()
		return obj
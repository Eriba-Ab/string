from django.contrib import admin
from django.utils.safestring import mark_safe
import json
from .models import StringEntry


# ---- Custom filters ----
class PalindromeFilter(admin.SimpleListFilter):
    title = 'Is Palindrome'
    parameter_name = 'is_palindrome'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Yes'),
            ('false', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return [obj for obj in queryset if obj.properties.get('is_palindrome')]
        if self.value() == 'false':
            return [obj for obj in queryset if not obj.properties.get('is_palindrome')]
        return queryset


class WordCountFilter(admin.SimpleListFilter):
    title = 'Word Count'
    parameter_name = 'word_count'

    def lookups(self, request, model_admin):
        # show basic options based on known data
        counts = set(obj.properties.get('word_count', 0) for obj in model_admin.model.objects.all())
        return [(str(c), f'{c} words') for c in sorted(counts)]

    def queryset(self, request, queryset):
        if self.value():
            return [obj for obj in queryset if str(obj.properties.get('word_count')) == self.value()]
        return queryset


# ---- Admin Registration ----
@admin.register(StringEntry)
class StringEntryAdmin(admin.ModelAdmin):
    list_display = ('short_value', 'is_palindrome', 'length', 'unique_characters', 'word_count', 'created_at')
    search_fields = ('value',)
    list_filter = (PalindromeFilter, WordCountFilter)
    readonly_fields = ('id', 'value', 'formatted_properties', 'created_at')

    def short_value(self, obj):
        return (obj.value[:50] + '...') if len(obj.value) > 50 else obj.value
    short_value.short_description = 'Value Preview'

    def formatted_properties(self, obj):
        formatted_json = json.dumps(obj.properties, indent=4)
        return mark_safe(f"<pre style='background:#f9f9f9; padding:10px; border-radius:8px;'>{formatted_json}</pre>")
    formatted_properties.short_description = 'Analyzed Properties'

    def is_palindrome(self, obj):
        return obj.properties.get('is_palindrome', False)
    is_palindrome.boolean = True

    def length(self, obj):
        return obj.properties.get('length')

    def unique_characters(self, obj):
        return obj.properties.get('unique_characters')

    def word_count(self, obj):
        return obj.properties.get('word_count')

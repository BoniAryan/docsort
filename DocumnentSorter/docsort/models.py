from django.db import models
from django.contrib.auth.models import User
import os
import uuid


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @property
    def name_trimmed(self):
        return self.name.replace(' ', '')


class Document(models.Model):
    """Single table document model with comma-separated keywords"""
    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # File Fields
    file1 = models.FileField(upload_to='files/', blank=True, null=True)
    file2 = models.FileField(upload_to='files/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

    # Document Type
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)

    # Version Info

    # Keywords (comma-separated)
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords for search")

    # Access Control
    accessible_by = models.ManyToManyField(
        User,
        related_name='accessible_documents',
        blank=True,
        help_text="Users who can access this document. If empty, only superusers can access."
    )

    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def get_keywords_list(self):
        """Return keywords as a list"""
        if not self.keywords:
            return []
        return [keyword.strip() for keyword in self.keywords.split(',')]

    @property
    def category_trimmed(self):
        cat_string = str(self.category)
        try:
            return cat_string.replace(' ', '')
        except:
            return cat_string

    def can_access(self, user):
        """Check if a user can access this document"""
        if user.is_superuser:
            return True
        return user in self.accessible_by.all()

    def __str__(self):
        return f"{self.title} "

    class Meta:
        ordering = ['-upload_date']
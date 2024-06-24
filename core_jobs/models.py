from django.db import models
from django.contrib.auth import get_user_model



User = get_user_model()

class Subject(models.Model):
    
    SUBJECTS= (
        ("math", "Mathematics"),
        ("science", "Science"),
        ("english", "English"),
        ("social_studies", "Social Studies"),
        ("hindi", "Hindi"),
        ("computer_science", "Computer Science"),
        ("physics", "Physics"),
        ("chemistry", "Chemistry"),
        ("biology", "Biology"),
        ("history", "History"),
        ("geography", "Geography"),
        ("economics", "Economics"),
        ("civics", "Civics"),
        ("physical_education", "Physical Education"),
        ("arts", "Arts"),
        ("music", "Music"),
        ("foreign_language", "Foreign Language"),
    )

    name = models.CharField(max_length=100, db_index=True, choices=SUBJECTS)

    def __str__(self):
        return self.get_name_display()

class Language(models.Model):
    LANGUAGES = (
        ("english", "English"),
        ("mandarin", "Mandarin"),
        ("spanish", "Spanish"),
        ("hindi", "Hindi"),
        ("french", "French"),
        ("arabic", "Arabic"),
        ("bengali", "Bengali"),
        ("russian", "Russian"),
        ("portuguese", "Portuguese"),
        ("urdu", "Urdu"),
    )

    name = models.CharField(max_length=100, db_index=True, choices=LANGUAGES)

    def __str__(self):
        return self.get_name_display()

class Job(models.Model):
    JOB_TYPE = (
        ("online", "Online"),
        ("Face-to-face", "Face-to-face"),
        ("Home", "Home")
    )

    tutor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    about_tutor = models.TextField()
    job_title = models.CharField(max_length=100, db_index=True)
    job_location = models.CharField(max_length=100, db_index=True, choices=JOB_TYPE, default='online')
    job_lang = models.ManyToManyField(Language, db_index=True, related_name="jobs")
    job_subjects = models.ManyToManyField(Subject, db_index=True, related_name="jobs")
    job_about = models.TextField()
    publish = models.BooleanField(default=True, db_index=True, null=True, blank=True)
    job_created = models.DateField(auto_now_add=True, db_index=True, null=True)

    def __str__(self):
        return self.job_title




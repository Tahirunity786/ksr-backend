from rest_framework import serializers
from django.contrib.auth import get_user_model

from core_reviews.serializers import ReviewsSerializer


from .models import Subject, Language, Job

User = get_user_model()

class TutorUserSerializer(serializers.ModelSerializer):
    reviews = ReviewsSerializer(many = True)
    class Meta:
        model = User
        fields = ['profile', 'first_name', 'last_name', 'email', 'hourly_rate', 'response_time', 't_to_number_of_students', 'reviews']


class SubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"

class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"

class JobSerializer(serializers.ModelSerializer):
    tutor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Job
        fields = ('id', 'tutor', 'job_title', 'about_tutor', 'job_about', 'job_location', 'job_lang', 'job_subjects', 'publish')

    def create(self, validated_data):
        job_subjects_data = validated_data.pop('job_subjects', [])
        job_lang_data = validated_data.pop('job_lang', [])
        tutor = validated_data.pop('tutor', None)

        job = Job.objects.create(tutor=tutor, **validated_data)

        for subject in job_subjects_data:
            job.job_subjects.add(subject)

        for lang in job_lang_data:
            job.job_lang.add(lang)

        return job



    def update(self, instance, validated_data):
        job_subjects_data = validated_data.pop('job_subjects', None)
        job_lang_data = validated_data.pop('job_lang', None)

        instance.job_title = validated_data.get('job_title', instance.job_title)
        instance.job_location = validated_data.get('job_location', instance.job_location)
        instance.job_about = validated_data.get('job_about', instance.job_about)
        instance.publish = validated_data.get('publish', instance.publish)
        instance.save()

        if job_subjects_data is not None:
            instance.job_subjects.set(job_subjects_data)

        if job_lang_data is not None:
            instance.job_lang.set(job_lang_data)

        return instance


class JoblistSerializer(serializers.ModelSerializer):
    tutor = TutorUserSerializer()

    class Meta:
        model = Job
        fields = ('id', 'tutor', 'job_title', 'about_tutor', 'job_about', 'job_location', 'job_lang', 'job_subjects', 'publish')


class JobDetailSerializer(serializers.ModelSerializer):
    job_lang = LanguagesSerializer(many=True)
    job_subjects = SubjectsSerializer(many=True)
    tutor = TutorUserSerializer()

 

    class Meta:
        model = Job
        fields = ['id', 'job_title', 'job_location', 'job_lang', 'job_subjects', 'job_about', 'job_created', 'tutor']



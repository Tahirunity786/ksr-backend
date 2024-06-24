from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Job, Language, Subject
from .serializers import JobDetailSerializer, JobSerializer, JoblistSerializer, SubjectsSerializer, LanguagesSerializer
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)

class JobCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the current user
        user = request.user

        # Copy request data to avoid modifying the original request data
        request_data = request.data.copy()

        # Add the current user as the tutor to the request data
        request_data['tutor'] = user.id

        # Initialize the serializer with the modified request data
        job_serializer = JobSerializer(data=request_data)

        if job_serializer.is_valid():
            job_serializer.save()
            return Response({"Success": True, "Info": "Job created successfully", "data": job_serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response({"Success": False, "Info": job_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        # Here you can set additional fields or perform additional actions before saving
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddSubjects(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_subject = SubjectsSerializer(data = request.data)
        if current_subject.is_valid():
            current_subject.save()
            return Response({"Success":True, "Info":"Subject saved successfully"}, status=status.HTTP_201_CREATED)
        
        return Response({"Success":False, "Info":current_subject.errors}, status=status.HTTP_400_BAD_REQUEST)

class AddLanguages(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_language = LanguagesSerializer(data = request.data)
        if current_language.is_valid():
            current_language.save()
            return Response({"Success":True, "Info":"Language saved successfully"}, status=status.HTTP_201_CREATED)
        
        return Response({"Success":False, "Info":current_language.errors}, status=status.HTTP_400_BAD_REQUEST)

class ListSubject(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectsSerializer
    


class ListLanguage(generics.ListAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguagesSerializer
    

class DeleteSubject(generics.DestroyAPIView):
    queryset = Subject.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class DeleteLanguage(generics.DestroyAPIView):
    queryset = Language.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class Listjobs(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JoblistSerializer
    

class SearchJobs(APIView):

    

    def get(self, request):
        try:
            data_a = request.query_params.get('subject', None)
            data_b = request.query_params.get('location', 'online')

            filters = Q()
            if data_a:
                filters &= (Q(job_title__icontains=data_a) | Q(job_subjects__name__icontains= data_a))
            if data_b:
                filters &= Q(job_location__icontains=data_b)

            if data_a or data_b:
                jobs = Job.objects.filter(filters).distinct()
            else:
                jobs = Job.objects.all()

            serializers = JoblistSerializer(instance=jobs, many=True)
            
            return Response(data=serializers.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"Success": False, "Info": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class GetJobDetail(APIView):
   

    def get(self, request, id):
        job = get_object_or_404(Job, id=id)
        
        job_data = JobDetailSerializer(job).data
        return Response({"Success": True, "JobDetail": job_data}, status=status.HTTP_200_OK)


from django.urls import path
from core_jobs.views import  DeleteLanguage, DeleteSubject, GetJobDetail, JobCreateView, JobDetailView, AddSubjects, AddLanguages,ListLanguage, ListSubject, Listjobs, SearchJobs

urlpatterns = [
    path('create/', JobCreateView.as_view(),),
    path('add/subject', AddSubjects.as_view()),
    path('delete/<int:id>/subject', DeleteSubject.as_view()),
    path('list/subject', ListSubject.as_view()),
    path('add/language', AddLanguages.as_view()),
    path('delete/<int:id>/language', DeleteLanguage.as_view()),
    path('list/', Listjobs.as_view()),
    path('search/', SearchJobs.as_view()),
    path('list/language', ListLanguage.as_view()),
    path('<int:pk>/update/', JobDetailView.as_view(),),
    path('<int:pk>/delete/', JobDetailView.as_view(),),
    path('<int:id>/details/', GetJobDetail.as_view()),
]

from rest_framework import viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Subject, Exam, Content, Comment
from .models import Post, Like, Share
from .models import Grade, Quarter
from .serializer import UserSerializer, SubjectSerializer, ExamSerializer
from .serializer import ContentSerializer, CommentSerializer
from .serializer import PostSerializer, LikeSerializer, ShareSerializer
from .serializer import GradeSerializer, QuarterSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from datetime import datetime
from django.db.models import Q
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['POST'], detail=True, url_path='login')
    def login(self, request, pk=None):
        # return request
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        success_login = False
        if user is not None and user.auth(request.POST['password']):
            success_login = True
        return Response({'success': success_login})


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend]

    @action(methods=['GET'], detail=False, url_path='user_related')
    def subject_list_user_related(self, request):
        subjects = get_subjects(user=request.user)

        subject = Q(id=subjects[0])
        for i in range(1, len(subjects)):
            subject = subject | Q(id=subjects[i])

        return Response(Subject.objects.filter(
            subject
        ).values())


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('subject', 'grade', )


class QuarterViewSet(viewsets.ModelViewSet):
    queryset = Quarter.objects.all()
    serializer_class = QuarterSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('subject', 'quarter', )


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('subject', )

    @action(methods=['GET'], detail=False, url_path='user_related')
    def subject_list_user_related(self, request):
        subjects = get_subjects(user=request.user)

        exam = Q(subject_id=subjects[0])
        for i in range(1, len(subjects)):
            exam = exam | Q(subject_id=subjects[i])

        return Response(Exam.objects.all().filter(exam).values())


class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('exam', 'poster', )

    @action(methods=['GET'], detail=False, url_path='user_related')
    def content_list_user_related(self, request):
        subjects = get_subjects(user=request.user)

        exam = Q(exam_id=subjects[0])
        for i in range(1, len(subjects)):
            exam = exam | Q(exam_id=subjects[i])

        return Response(Content.objects.all().filter(exam).values())


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('exam', 'sender', 'bef_comment')


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('user', 'bef_post')


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('post')


class ShareViewSet(viewsets.ModelViewSet):
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('post')


def get_subjects(user):
    period = get_period(user=user)
    quarter = Q(quarter=period["quarter"][0])
    for i in range(1, len(period["quarter"])):
        quarter = quarter | Q(quarter=period["quarter"][i])

    proper_quarter = set([_["subject_id"] for _ in Quarter.objects.filter(
        quarter
    ).values()])

    proper_grade = set([_["subject_id"] for _ in Grade.objects.filter(
        grade=period["grade"]
    ).values()])

    quarter = Q(quarter=period["quarter"][0])
    for i in range(1, len(period["quarter"])):
        quarter = quarter | Q(quarter=period["quarter"][i])

    return list(proper_grade & proper_quarter)


def get_period(user: User, now=datetime.now()):
    """
    user => grade
    time => quarter(4, 6, 10, 12)
    """
    return {
        'grade': get_grade(user, now),
        'quarter': get_quarters(now)
    }


def get_grade(user: User, now):
    grade = now.year - int(user.number[1:5]) - 766
    return grade - 1 if now.month in [1, 2, 3] else grade


def get_quarters(now):
    month = now.month
    quarters = []
    if month > 10:   # 4 Quarter
        quarters = ["前期", "第4学期"]
    elif month > 6:  # 3 Quarter
        quarters = ["前期", "第3学期"]
    elif month > 4:  # 2 Quarter
        quarters = ["後期", "第2学期"]
    else:            # 1 Quarter
        quarters = ["後期", "第1学期"]
    return quarters

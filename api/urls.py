from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.start, name='start'),
    path('browse/', views.browse, name='browse'),
    path('quiz/select/<int:quiz_id>/', views.quiz_select, name='quiz_select'),
    path('quiz/update/<int:quiz_id>/', views.quiz_update, name='quiz_update'),
    path('quiz/delete/<int:quiz_id>/', views.quiz_delete, name='quiz_delete'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    path('view_quiz/', views.view_quiz, name='view_quiz'),
    path('authenticate_user/', views.authenticate_user, name='authenticate_user'),
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='quiz_start'),
    path('quiz_qr/', views.quiz_qr, name='quiz_qr'),
    path('save_quiz/', views.save_quiz, name='save_quiz'),  # Remove api/ from path
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='quiz_start'),
    path('quiz/join/', views.enter_pin, name='enter_pin'),  # Default join path
    path('quiz/join/<str:quiz_code>/', views.join_quiz, name='join_quiz'),
    path('quiz/<int:quiz_id>/waiting/', views.waiting_room, name='waiting_room'),
    path('quiz/<int:quiz_id>/host/', views.host_quiz, name='host_quiz'), 
    path('quiz/<int:quiz_id>/play/', views.play_quiz, name='play_quiz'),
    #still no buttons on player side. also need result logic.

    # path('quiz/submit/', views.submit_quiz, name='submit_quiz'),
    # path('quiz/leaderboard/<int:quiz_id>/', views.leaderboard, name='leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/update/', views.update_leaderboard, name='update_leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/delete/', views.delete_leaderboard, name='delete_leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/create/', views.create_leaderboard, name='create_leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/view/', views.view_leaderboard, name='view_leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/authenticate_user/', views.authenticate_user, name='authenticate_user'),
    # path('quiz/leaderboard/<int:quiz_id>/start/', views.start_leaderboard, name='leaderboard_start'),
    # path('quiz/leaderboard/<int:quiz_id>/join/', views.join_leaderboard, name='join_leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/submit/', views.submit_leaderboard, name='submit_leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/leaderboard/', views.leaderboard, name='leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/leaderboard/update/', views.update_leaderboard, name='update_leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/leaderboard/delete/', views.delete_leaderboard, name='delete_leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/leaderboard/create/', views.create_leaderboard, name='create_leaderboard'),
    # path('quiz/leaderboard/<int:quiz_id>/leaderboard/view/', views.view_leaderboard, name='view_leaderboard'),
    
]
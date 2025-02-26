from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Profile, Quiz, Question
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Profile, Quiz, Question
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
import json, base64
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render
from .models import Quiz, User
from django.shortcuts import render, get_object_or_404
from .models import Quiz
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Quiz
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Quiz, Question, Answer, Profile, QuizUser
from django.contrib.auth.models import User
from django.urls import reverse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import qrcode
from io import BytesIO
import base64
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def browse(request):
    if request.method == 'GET':
        # Get all quizzes (we'll filter by user later if needed)
        quizzes = Quiz.objects.all().order_by('-date_created')
        
        return render(request, 'api/browse.html', {
            'quizzes': quizzes,
            'quiz_count': quizzes.count()
        })
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            fingerprint_hash = data.get('fingerprint_hash')
            
            if not fingerprint_hash:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Fingerprint hash is required'
                }, status=400)
            
            # Get or create user based on fingerprint
            user, created = User.objects.get_or_create(username=fingerprint_hash)
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Get quizzes for this user
            quizzes = Quiz.objects.filter(profile=profile).order_by('-date_created')
            
            return JsonResponse({
                'status': 'success',
                'quizzes': list(quizzes.values('id', 'quiz_name', 'date_created'))
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


def save_quiz(request):
    if request.method == 'POST':
        quiz = Quiz.objects.create(
            quiz_name=request.POST['quiz_name'],
            visitor_id=request.POST['visitor_id']
        )
        
        # Get all question data from the form
        questions = []
        i = 1
        while f'question{i}' in request.POST:
            question = Question.objects.create(
                quiz=quiz,
                text=request.POST[f'question{i}'],  # Changed from question_text to text
                question_type=request.POST.get(f'question_type{i}', 'multiple_choice'),
                timer=request.POST.get(f'timer{i}', 30),
                order=i
            )
            
            # Handle options based on question type
            if question.question_type == 'multiple_choice':
                options = []
                for j in range(1, 5):
                    option = request.POST.get(f'answer{i}_{j}')
                    if option:
                        options.append(option)
                question.options = options
                question.save()
            
            i += 1
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def enter_pin(request):
    """View for entering quiz PIN"""
    return render(request, 'api/enter_pin.html')
def join_quiz(request, quiz_code):
    """Handle quiz joining after PIN entry"""
    quiz = get_object_or_404(Quiz, join_code=quiz_code)
    
    if request.method == 'POST':
        player_name = request.POST.get('player_name')
        if not player_name:
            return JsonResponse({
                'status': 'error',
                'message': 'Player name is required'
            }, status=400)
            
        # Store player info in session
        if 'players' not in request.session:
            request.session['players'] = {}
        
        request.session['players'][str(quiz.id)] = {
            'name': player_name,
            'score': 0
        }
        request.session.modified = True
        
        # Send WebSocket message about new player
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'quiz_{quiz.id}',
            {
                'type': 'quiz_message',
                'message': {
                    'type': 'player_joined',
                    'player_name': player_name
                }
            }
        )
        
        return JsonResponse({
            'status': 'success',
            'quiz_id': quiz.id
        })
    
    return render(request, 'api/join_quiz.html', {'quiz': quiz})


def waiting_room(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Get player name from session
    player_name = request.session.get('players', {}).get(str(quiz_id), {}).get('name', '')
    
    if not player_name:
        return redirect('api:enter_pin')
        
    return render(request, 'api/waiting_room.html', {
        'quiz': quiz,
        'player_name': player_name
    })

def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        try:
            quiz.status = 'active'
            quiz.save()
            
            # Notify all connected clients via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'quiz_{quiz_id}',
                {
                    'type': 'quiz_message',
                    'message': {
                        'type': 'quiz_start',
                        'quiz_id': quiz_id
                    }
                }
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Quiz started successfully',
                'quiz_id': quiz_id
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    # Handle GET request - show quiz start page
    if not quiz.join_code:
        quiz.generate_join_code()
        quiz.save()
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    join_url = request.build_absolute_uri(
        reverse('api:enter_pin')
    )
    qr.add_data(join_url)
    qr.make(fit=True)
    
    # Create QR code image
    img_buffer = BytesIO()
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image.save(img_buffer, format='PNG')
    qr_image_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    context = {
        'quiz': quiz,
        'qr_code': qr_image_base64,
    }
    
    return render(request, 'api/quiz_start.html', context)

import json
from django.shortcuts import render, get_object_or_404, redirect
from api.models import Quiz

def play_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    player_info = request.session.get('players', {}).get(str(quiz_id))
    
    if not player_info:
        return redirect('api:enter_pin')
    
    # Get all questions for this quiz
    questions = quiz.questions.all().order_by('order')
    questions_json = []
    
    for q in questions:
        # Ensure options are properly parsed
        options = ['True', 'False'] if q.question_type == 'true_false' else q.options

        # Handle cases where options are stored as strings
        if isinstance(options, str):  
            try:
                options = json.loads(options)  # Convert JSON string to Python list
            except json.JSONDecodeError:
                options = []  # Default to empty list if parsing fails
        
        question_data = {
            'id': q.id,
            'text': q.text,
            'type': q.question_type,
            'options': options,
            'timer': q.timer
        }
        questions_json.append(question_data)
    
    context = {
        'quiz': quiz,
        'player_name': player_info['name'],
        'questions_json': json.dumps(questions_json)  # Convert list to JSON string
    }
    
    return render(request, 'api/play_quiz.html', context)



def quiz_delete(request, quiz_id):
    if request.method == 'POST':
        try:
            quiz = get_object_or_404(Quiz, id=quiz_id)
            quiz.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Quiz deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


# Render index.html
def index(request):
    return render(request, 'api/index.html')

# Render start.html
def start(request):
    return render(request, 'api/start.html')

# Render browse.html
def browse(request):
    return render(request, 'api/browse.html')

# View to update a quiz
def quiz_update(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # Implement the update logic
    return redirect('quiz_detail', quiz_id=quiz.id)

# View to delete a quiz
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete()
    return redirect('browse')
@csrf_exempt
def create_quiz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create the quiz
            quiz = Quiz.objects.create(
                quiz_name=data.get('quiz_name', 'New Quiz')
            )
            
            # Generate join code
            join_code = quiz.generate_join_code()
            
            # Create questions
            for i, q_data in enumerate(data.get('questions', [])):
                Question.objects.create(
                    quiz=quiz,
                    text=q_data['text'],
                    question_type=q_data['type'],
                    options=q_data.get('options'),
                    correct_answer=q_data.get('correct_answer'),
                    timer=int(q_data['timer']),
                    order=i
                )

            return JsonResponse({
                'status': 'success',
                'quiz_id': quiz.id,
                'join_code': quiz.join_code,
                'message': 'Quiz created successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method is allowed'
    }, status=405)


def quiz_qr(request):
    join_code = request.GET.get('join_code')
    qr_code_url = request.GET.get('qr_code_url')
    return render(request, 'api/quiz_qr.html', {'join_code': join_code, 'qr_code_url': qr_code_url})

    
def view_quiz(request):
    if request.method == 'GET':
        fingerprint_hash = request.GET.get('fingerprint_hash')

        if not fingerprint_hash:
            return JsonResponse({'success': False, 'error': 'Fingerprint hash is required'})

        try:
            user = User.objects.get(username=fingerprint_hash)
            profile = Profile.objects.get(user=user)
            quizzes = Quiz.objects.filter(profile=profile)

            quiz_data = []
            for quiz in quizzes:
                quiz_data.append({
                    'quiz_id': quiz.id,
                    'quiz_name': quiz.quiz_name,
                    'date_created': quiz.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                })

            return render(request, 'api/browse.html', {'quizzes': quiz_data})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# API to select a quiz
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quiz_select(request, quiz_id):
    user = request.user
    profile = Profile.objects.get(user=user)
    quiz = Quiz.objects.get(id=quiz_id)
    return JsonResponse({'success': True, 'quiz_name': quiz.quiz_name})

# View to authenticate user using fingerprint
@csrf_exempt
def authenticate_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fingerprint_hash = data.get('fingerprint_hash')
            
            # Get or create the user based on the fingerprint
            user, created = User.objects.get_or_create(username=fingerprint_hash)
            profile, profile_created = Profile.objects.get_or_create(user=user)
            
            return JsonResponse({'success': True, 'user_id': user.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

import json
from django.shortcuts import render, get_object_or_404
from .models import Quiz

def host_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().order_by('order')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if data.get('action') == 'next_question':
                question_index = data.get('question_index', 0)
                if question_index < questions.count():
                    question = questions[question_index]
                    # Format question data
                    question_data = {
                        'id': question.id,
                        'text': question.text,
                        'options': question.options if question.question_type == 'multiple_choice' else ['True', 'False'],
                        'timer': question.timer,
                        'type': question.question_type
                    }
                    
                    # Send to all connected clients
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'quiz_{quiz_id}',
                        {
                            'type': 'quiz_message',
                            'message': {
                                'type': 'new_question',
                                'question': question_data
                            }
                        }
                    )
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'No more questions'
                    }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    # Handle GET request - show host interface
    questions_json = []
    for q in questions:
        questions_json.append({
            'id': q.id,
            'text': q.text,
            'type': q.question_type,
            'options': q.options if q.question_type == 'multiple_choice' else ['True', 'False'],
            'timer': q.timer
        })
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'questions_json': json.dumps(questions_json)
    }
    
    return render(request, 'api/host_quiz.html', context)
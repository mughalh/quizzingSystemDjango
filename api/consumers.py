from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Quiz, Question
import json

class QuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.quiz_id = self.scope['url_route']['kwargs']['quiz_id']
        self.room_group_name = f'quiz_{self.quiz_id}'

        try:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            print(f"WebSocket connected for quiz {self.quiz_id}")

            # Get player info using sync_to_async
            player_info = await self.get_player_info()
            if player_info and "name" in player_info:
                await self.send_player_joined(player_info["name"])
        except Exception as e:
            print(f"Error in connect: {e}")
            await self.close()

    @database_sync_to_async
    def get_player_info(self):
        players = self.scope["session"].get("players", {})
        return players.get(str(self.quiz_id))

    @database_sync_to_async
    def get_quiz_questions(self):
        quiz = Quiz.objects.get(id=self.quiz_id)
        questions = list(quiz.questions.all().values('id', 'text', 'options', 'timer'))
        return questions

    async def send_player_joined(self, player_name):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "quiz_message",
                "message": {
                    "type": "player_joined",
                    "player_name": player_name
                }
            }
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data['type'] == 'quiz_start':
                questions = await self.get_quiz_questions()
                if questions:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "quiz_message",
                            "message": {
                                "type": "new_question",
                                "question": questions[0]  # Send first question
                            }
                        }
                    )
                else:
                    print("No questions found for quiz")

        except Exception as e:
            print(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def quiz_message(self, event):
        """Handle all quiz-related messages"""
        print(f"Sending message: {event['message']}")
        await self.send(text_data=json.dumps(event["message"]))
# quizzingSystemDjango
This is a no login solution to Kahoot.it style quizzing system.

# VoteItOut - Interactive Quiz Application

A real-time quiz application built with Django and WebSockets that allows hosts to create quizzes and players to join and participate.

## Prerequisites

- Python 3.11+
- pip
- virtualenv
- Django 5.1
- Channels (for WebSocket support)
- Daphne (ASGI server)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mughalh/VoteItOut.git
cd VoteItOut
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Navigate to the project directory:
```bash
cd voteitout
```

2. Create a `.env` file:
```bash
SECRET_KEY='your-secret-key'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.10.10
```

3. Apply database migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

## Running the Application

1. Start the Daphne server:
```bash
daphne -b 192.168.10.10 -p 8000 voteitout.asgi:application
```

2. Access the application:
- Admin interface: `http://192.168.10.10:8000/admin/`
- Main application: `http://192.168.10.10:8000/`

## Debug Mode

To run in debug mode with verbose WebSocket logging:

```bash
daphne -v2 -b 192.168.10.10 -p 8000 voteitout.asgi:application
```

## Project Structure

```
voteitout/
├── api/
│   ├── templates/
│   │   └── api/
│   │       ├── play_quiz.html
│   │       ├── quiz_start.html
│   │       └── start.html
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   └── views.py
├── voteitout/
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py
└── manage.py
```

## Known Issues

1. WebSocket connection issues:
   - Check browser console (F12) for WebSocket messages
   - Verify ALLOWED_HOSTS includes your server IP
   - Monitor Daphne server logs for connection errors

2. Questions not appearing:
   - Check WebSocket connection status
   - Verify question data format in database
   - Monitor browser console for message delivery

## Debugging Steps

1. Check WebSocket connections:
```javascript
// Browser Console
socket.readyState  // Should be 1 (OPEN)
```

2. Monitor WebSocket messages:
```javascript
// Browser Console
socket.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
```

3. Test question display:
```javascript
// Browser Console
showQuestion({
    id: 1,
    text: "Test Question",
    options: ["Option 1", "Option 2", "Option 3"],
    timer: 30
});
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

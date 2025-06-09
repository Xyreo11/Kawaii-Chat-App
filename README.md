
# 🌸 KawaiiChat 🌸

A cute, socket-based chat application with a kawaii pink theme.

## Features

- 💕 Adorable pink coquette UI theme
- 👤 User authentication system
- 💬 Real-time messaging
- 📨 Offline message storage
- 🔍 Contact search
- 😊 Emoji picker

## Requirements

- Python 3.7+
- MySQL Server
- Required Python packages:
  - `tkinter` (usually comes with Python)
  - `pillow` (for image handling)
  - `customtkinter` (for enhanced UI elements)
  - `mysql-connector-python` (for database connectivity)

## Setup Instructions

### 1. Database Setup

1. Install MySQL if you don't have it already
2. Create a database and set up the tables using the provided SQL script:

```bash
mysql -u root -p < database_setup.sql
```

Alternatively, you can run the SQL commands in the `database_setup.sql` file through MySQL Workbench or another MySQL client.

### 2. Configure Server

Open `socket_server.py` and update the database configuration:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_mysql_username',
    'password': 'your_mysql_password',
    'database': 'kawaii_chat'
}
```

### 3. Install Required Packages

```bash
pip install mysql-connector-python pillow customtkinter
```

### 4. Run the Server

```bash
python socket_server.py
```

### 5. Run the Client Application

```bash
python kawaii_chat_client.py
```

## Usage

1. Register a new account or log in with existing credentials
2. Browse your contacts in the left sidebar
3. Click on a contact to start chatting
4. Use the emoji button to add cute emojis to your messages
5. Enjoy chatting with your friends! ✨

## Project Structure

- `socket_server.py`: Server-side socket handling and database operations
- `kawaii_chat_client.py`: Client application with GUI
- `database_setup.sql`: SQL script to set up the database

## Technical Details

### Socket Communication

The application uses raw TCP sockets for communication between clients and the server. Messages are serialized as JSON for easy parsing and handling.

### Database Schema

- `users`: Stores user information including credentials and online status
- `messages`: Stores all messages with sender, receiver, content, and read status

### Message Delivery

Messages are immediately delivered to online users and stored in the database for offline users. When a user logs in, any unread messages are retrieved and displayed.

## Customization

You can easily customize the appearance by modifying the color theme in the `THEME_COLORS` dictionary in the client code.

## Future Enhancements

- Group chat functionality
- File sharing capabilities
- Custom themes selection
- Profile picture upload
- Message reactions and stickers

---

🌟 Made with love for kawaii chat lovers 🌟

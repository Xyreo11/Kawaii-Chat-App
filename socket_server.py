import socket
import threading
import json
import mysql.connector
import datetime
import hashlib
import uuid
from mysql.connector import Error
import os
import sys
import base64

# Server configuration
HOST = '0.0.0.0'
PORT = 9999

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '86Qi76Lp',
    'database': 'kawaii_chat'
}

# Create database connection
def create_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def setup_database():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            display_name VARCHAR(50),
            last_seen DATETIME,
            status ENUM('online', 'offline') DEFAULT 'offline',
            profile_pic VARCHAR(255) DEFAULT 'default.png',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id VARCHAR(36) PRIMARY KEY,
            sender_id VARCHAR(36) NOT NULL,
            receiver_id VARCHAR(36) NOT NULL,
            message TEXT NOT NULL,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            read_status BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
        ''')
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database setup completed.")
    else:
        print("Failed to setup database.")

# User authentication
def authenticate_user(username, password):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Find user
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
                      (username, hashed_password))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if user:
            return user
        
    return None

# Add these new functions for profile updates
# Register new user
def register_user(username, password, display_name=None):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Generate UUID for user
        user_id = str(uuid.uuid4())
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Set display name if not provided
        if not display_name:
            display_name = username
            
        try:
            cursor.execute(
                "INSERT INTO users (id, username, password, display_name) VALUES (%s, %s, %s, %s)",
                (user_id, username, hashed_password, display_name)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error registering user: {e}")
            return False
    
    return False
# Add this new function to get complete chat history between two users
def get_chat_history(user1_id, user2_id):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Get all messages between the two users
            cursor.execute('''
                SELECT m.id, m.message, m.sent_at, m.sender_id, m.receiver_id,
                       u.username as sender_username, u.display_name as sender_display_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE (m.sender_id = %s AND m.receiver_id = %s) 
                   OR (m.sender_id = %s AND m.receiver_id = %s)
                ORDER BY m.sent_at ASC
            ''', (user1_id, user2_id, user2_id, user1_id))
            
            messages = cursor.fetchall()
            
            # Convert datetime objects to strings for JSON seri//alization
            for message in messages:
                if isinstance(message['sent_at'], datetime.datetime):
                    message['sent_at'] = message['sent_at'].isoformat()
            
            cursor.close()
            connection.close()
            return messages
        except Error as e:
            print(f"Error getting chat history: {e}")
            return []
    
    return []

# Update user status
def update_user_status(user_id, status):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                "UPDATE users SET status = %s, last_seen = NOW() WHERE id = %s",
                (status, user_id)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error updating user status: {e}")
            return False
    
    return False

# Store message
def store_message(sender_id, receiver_id, message_content):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Generate UUID for message
        message_id = str(uuid.uuid4())
        
        try:
            cursor.execute(
                "INSERT INTO messages (id, sender_id, receiver_id, message) VALUES (%s, %s, %s, %s)",
                (message_id, sender_id, receiver_id, message_content)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error storing message: {e}")
            return False
    
    return False

# Get unread messages for user
def get_unread_messages(user_id):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Get messages and sender info
            cursor.execute('''
                SELECT m.id, m.message, m.sent_at, m.sender_id, 
                       u.username as sender_username, u.display_name as sender_display_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.receiver_id = %s AND m.read_status = FALSE
                ORDER BY m.sent_at ASC
            ''', (user_id,))
            
            messages = cursor.fetchall()
            
            # Convert datetime objects to strings for JSON serialization
            for message in messages:
                if isinstance(message['sent_at'], datetime.datetime):
                    message['sent_at'] = message['sent_at'].isoformat()
            
            # Mark messages as read
            if messages:
                cursor.execute(
                    "UPDATE messages SET read_status = TRUE WHERE receiver_id = %s AND read_status = FALSE",
                    (user_id,)
                )
                connection.commit()
            
            cursor.close()
            connection.close()
            return messages
        except Error as e:
            print(f"Error getting unread messages: {e}")
            return []
    
    return []


# Get all users
def get_all_users():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT id, username, display_name, status, last_seen, profile_pic
                FROM users
            ''')
            
            users = cursor.fetchall()
            
            # Convert datetime objects to strings
            for user in users:
                if 'last_seen' in user and isinstance(user['last_seen'], datetime.datetime):
                    user['last_seen'] = user['last_seen'].isoformat()
            
            cursor.close()
            connection.close()
            return users
        except Error as e:
            print(f"Error getting users: {e}")
            return []
    
    return []

# Active clients dictionary {user_id: (client_socket, username)}
active_clients = {}

# Client handler function
def handle_client(client_socket, client_address):
    print(f"New connection from {client_address}")
    current_user = None
    buffer = ""
    
    # Initialize last activity timestamp
    last_activity = datetime.datetime.now()
    
    try:
        # Set a reasonable timeout for socket operations
        client_socket.settimeout(60)  # 60 second timeout
        
        while True:
            # Check if we need to send a heartbeat (every 30 seconds)
            now = datetime.datetime.now()
            if (now - last_activity).total_seconds() > 30:
                try:
                    # Send heartbeat
                    heartbeat = {"type": "heartbeat"}
                    client_socket.sendall((json.dumps(heartbeat) + '\n').encode('utf-8'))
                    print(f"Sent heartbeat to {client_address}")
                    last_activity = now
                except Exception as e:
                    print(f"Error sending heartbeat to {client_address}: {e}")
                    break
            
            try:
                # Try to receive data with timeout
                data = client_socket.recv(4096)
                
                if not data:
                    print(f"No data received from {client_address}, closing connection")
                    break
                    
                # Update activity timestamp on receiving data
                last_activity = datetime.datetime.now()
                
                # Handle message
                buffer += data.decode('utf-8')
                
                # Process complete messages
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    message = json.loads(line)
                    message_type = message.get('type')
                    
                    # Handle heartbeat response
                    if message_type == 'heartbeat_response' or message_type == 'client_heartbeat':
                        # Just acknowledge and continue
                        last_activity = datetime.datetime.now()
                        continue
                    
                    # Handle different message types
                    if message_type == 'login':
                        username = message.get('username')
                        password = message.get('password')
                        
                        user = authenticate_user(username, password)
                        if user:
                            current_user = user
                            
                            # Ensure any datetime objects in the user dict are converted to strings
                            user_data = {
                                'id': user['id'],
                                'username': user['username'],
                                'display_name': user['display_name']
                            }
                            # Only include these specific fields to avoid datetime fields
                            
                            active_clients[user['id']] = (client_socket, username)
                            update_user_status(user['id'], 'online')
                            
                            # Get unread messages
                            unread_messages = get_unread_messages(user['id'])
                            
                            # Get all users
                            all_users = get_all_users()
                            
                            # Send successful login response
                            response = {
                                'type': 'login_response',
                                'success': True,
                                'user': user_data,
                                'unread_messages': unread_messages,
                                'users': all_users
                            }
                        else:
                            # Send failed login response
                            response = {
                                'type': 'login_response',
                                'success': False,
                                'message': 'Invalid username or password'
                            }
                        
                        client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
                        
                    elif message_type == 'register':
                        username = message.get('username')
                        password = message.get('password')
                        display_name = message.get('display_name')
                        
                        success = register_user(username, password, display_name)
                        
                        # Send registration response
                        response = {
                            'type': 'register_response',
                            'success': success,
                            'message': 'Registration successful' if success else 'Registration failed'
                        }
                        
                        client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
                        
                    elif message_type == 'message' and current_user:
                        receiver_id = message.get('receiver_id')
                        content = message.get('content')
                        
                        # Store message in database
                        store_message(current_user['id'], receiver_id, content)
                        
                        # If receiver is active, send the message
                        if receiver_id in active_clients:
                            receiver_socket, _ = active_clients[receiver_id]
                            
                            message_to_send = {
                                'type': 'new_message',
                                'sender': {
                                    'id': current_user['id'],
                                    'username': current_user['username'],
                                    'display_name': current_user['display_name']
                                },
                                'content': content,
                                'timestamp': datetime.datetime.now().isoformat()
                            }
                            
                            receiver_socket.sendall((json.dumps(message_to_send) + '\n').encode('utf-8'))
                        
                        # Send confirmation to sender
                        response = {
                            'type': 'message_sent',
                            'success': True,
                            'receiver_id': receiver_id
                        }
                        
                        client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
                    
                    elif message_type == 'get_chat_history' and current_user:
                        other_user_id = message.get('user_id')
                        
                        # Get chat history between the two users
                        chat_history = get_chat_history(current_user['id'], other_user_id)
                        
                        response = {
                            'type': 'chat_history',
                            'user_id': other_user_id,
                            'messages': chat_history
                        }
                        
                        client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
                        
                    elif message_type == 'get_users' and current_user:
                        # Get all users
                        all_users = get_all_users()
                        
                        response = {
                            'type': 'users_list',
                            'users': all_users
                        }
                        
                        client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
                        
                    elif message_type == 'update_username' and current_user:
                        new_username = message.get('new_username')
                        success, message_text = update_username(current_user['id'], new_username)
                        
                        if success:
                            # Update current_user data
                            current_user['username'] = new_username
                            # Update active clients entry
                            active_clients[current_user['id']] = (client_socket, new_username)
                        
                        response = {
                            'type': 'username_update_response',
                            'success': success,
                            'message': message_text,
                            'new_username': new_username if success else None
                        }
                        
                        client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
                        
                        # If successful, broadcast updated users list to all clients
                        if success:
                            all_users = get_all_users()
                            users_update = {
                                'type': 'users_list',
                                'users': all_users
                            }
                            
                            for uid, (sock, _) in active_clients.items():
                                try:
                                    sock.sendall((json.dumps(users_update) + '\n').encode('utf-8'))
                                except:
                                    pass
                        
                    elif message_type == 'update_password' and current_user:
                        current_password = message.get('current_password')
                        new_password = message.get('new_password')
                        
                        success, message_text = update_password(current_user['id'], current_password, new_password)
                        
                        response = {
                            'type': 'password_update_response',
                            'success': success,
                            'message': message_text
                        }
                        
                        client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
                        
                    elif message_type == 'update_profile_pic' and current_user:
                        image_data = message.get('image_data')
                        file_extension = message.get('file_extension')
                        
                        success, message_text, filename = update_profile_pic(current_user['id'], image_data, file_extension)
                        
                        response = {
                            'type': 'profile_pic_update_response',
                            'success': success,
                            'message': message_text,
                            'filename': filename
                        }
                        
                        client_socket.sendall((json.dumps(response) + '\n').encode('utf-8'))
                        
                        # If successful, broadcast updated users list
                        if success:
                            all_users = get_all_users()
                            users_update = {
                                'type': 'users_list',
                                'users': all_users
                            }
                            
                            for uid, (sock, _) in active_clients.items():
                                try:
                                    sock.sendall((json.dumps(users_update) + '\n').encode('utf-8'))
                                except:
                                    pass
                    
            except socket.timeout:
                # Socket timeout - this is expected, just continue the loop
                continue
            except json.JSONDecodeError as e:
                print(f"JSON decode error from {client_address}: {e}")
                # Don't break, just continue and try to recover
                buffer = ""
                continue
            
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        # Clean up when client disconnects
        if current_user:
            if current_user['id'] in active_clients:
                del active_clients[current_user['id']]
            update_user_status(current_user['id'], 'offline')
        
        try:
            client_socket.close()
        except:
            pass
        print(f"Connection closed for {client_address}")

# Main server function
def start_server():
    # Setup database
    setup_database()
    
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"KawaiiChat server started on {HOST}:{PORT}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
            
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
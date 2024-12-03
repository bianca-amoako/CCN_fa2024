import threading
import pygame
import socket
import sys
import random

# Global variables
name = "test"
posx = 300
posy = 350  # Starting position of the bucket (lower part of the screen)
bucket_speed = 5  # Initial speed of the bucket
object_speed = 2  # Initial speed of falling objects
score = 0  # Player score
game_over = False  # Game over flag
lock = threading.Lock()  # Lock for synchronizing position changes

# Object class to represent falling objects
class FallingObject:
    def __init__(self, x):
        self.rect = pygame.Rect(x, 0, 25, 25)  # Random start position at the top
        self.color = (255, 0, 0)  # Red color for falling objects
    
    def fall(self, speed):
        self.rect.y += speed  # Move the object down
    
    def reset(self):
        self.rect.y = 0  # Reset object to the top

# Game Thread
def GameThread():
    global posx, posy, object_speed, bucket_speed, score, game_over

    pygame.init()
    background = (204, 230, 255)
    shapeColor = (0, 51, 204)
    shapeColorOver = (255, 0, 204)
    
    fps = pygame.time.Clock()
    screen_size = screen_width, screen_height = 600, 400
    rect1 = pygame.Rect(0, 0, 50, 25)  # The bucket size
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Catch the Falling Objects')

    colorRect = shapeColor
    colorRect2 = shapeColorOver

    # List to store falling objects
    falling_objects = []

    # Initial falling object
    falling_objects.append(FallingObject(random.randint(0, screen_width - 25)))

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Handle player input
        with lock:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and posx > 10:  # Move left
                posx -= bucket_speed
            if keys[pygame.K_d] and posx < screen_width - 50:  # Move right
                posx += bucket_speed

        # Move falling objects and check for collisions
        for obj in falling_objects:
            obj.fall(object_speed)
            if obj.rect.colliderect(rect1):  # If object hits the bucket
                falling_objects.remove(obj)
                falling_objects.append(FallingObject(random.randint(0, screen_width - 25)))  # Reset falling object
                score += 1  # Increase score
            elif obj.rect.y > screen_height:  # If object reaches bottom
                game_over = True  # End the game

        # Increase difficulty: speed up objects and the bucket
        object_speed += 0.001
        bucket_speed += 0.01

        # Generate new falling objects periodically
        if random.random() < 0.0001:  # Chance of new object falling
            falling_objects.append(FallingObject(random.randint(0, screen_width - 25)))

        # Update the bucket's position
        rect1.center = (posx, posy)

        # Draw everything
        screen.fill(background)
        
        # Draw the bucket
        pygame.draw.rect(screen, colorRect, rect1)

        # Draw the falling objects
        for obj in falling_objects:
            pygame.draw.rect(screen, obj.color, obj.rect)

        # Display the score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # If game over, display message
        if game_over:
            game_over_text = font.render("Game Over!", True, (255, 0, 0))
            screen.blit(game_over_text, (screen_width // 2 - 100, screen_height // 2 - 50))
            pygame.display.update()
            pygame.time.wait(2000)  # Wait for 2 seconds before closing
            pygame.quit()
            sys.exit()

        pygame.display.update()
        fps.tick(60)

# Server Thread
def ServerThread():
    global posy, posx
    host = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    host = s.getsockname()[0]
    s.close()
    print(host)
    port = 5000  # Port number

    server_socket = socket.socket()  # Create socket
    server_socket.bind((host, port))  # Bind address and port
    print("Server enabled...")
    server_socket.listen(2)  # Max 2 clients
    conn, address = server_socket.accept()  # Accept connection
    print("Connection from: " + str(address))    
    
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        
        print("from connected user: " + str(data))

        with lock:  # Synchronize position updates
            if data == 'w' and posy > 10:  # Prevent going off-screen (top)
                posy -= 50
            elif data == 's' and posy < 390:  # Prevent going off-screen (bottom)
                posy += 50
            elif data == 'a' and posx > 10:  # Prevent going off-screen (left)
                posx -= 50
            elif data == 'd' and posx < 590:  # Prevent going off-screen (right)
                posx += 50

        # Optionally, send an acknowledgment to the client
        conn.send("Position updated".encode())

    conn.close()  # Close connection when done

# Create and start threads
t1 = threading.Thread(target=GameThread)
t2 = threading.Thread(target=ServerThread)
t1.start()
t2.start()

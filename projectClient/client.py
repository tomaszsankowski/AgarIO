import socket
import struct
import math
import pygame
import pygame.gfxdraw
import tkinter as tk


class MyCell:
    def __init__(self, id, x, y, mass_t, color_t):
        self.id = id
        self.x = x
        self.y = y
        self.mass = mass_t
        self.color = color_t


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class GUI:
    def __init__(self):
        self.myCell = None
        self.players = []
        self.foods = []
        self.screen = None
        self.clock = None
        self.running = None
        self.speed = 5
        self.fps = 140
        self.player_name = ""

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 5000
        self.s.connect(('localhost', port))

    def receive_cell(self):
        buffer = self.s.recv(40)
        myID, x, y, mass, r, g, b = struct.unpack('i d d i i i i', buffer)
        self.myCell = MyCell(myID, x, y, mass, (r, g, b))

    def init_pygame(self):
        pygame.init()
        width = 1200
        height = 800
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Agar.io")
        self.clock = pygame.time.Clock()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def get_username(self):
        root = tk.Tk()
        root.title("mega gówno")
        entry = tk.Entry(root)
        entry.pack()
        button = tk.Button(root, text="Play", command=lambda: self.submit(entry, root))
        button.pack()
        root.mainloop()

    def submit(self, entry, root):
        self.player_name = entry.get()
        root.destroy()

    def update_cell_position(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - self.myCell.x
        dy = my - self.myCell.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        self.radius = math.sqrt(self.myCell.mass / math.pi)
        if distance > self.radius:
            angle = math.atan2(dy, dx)
            self.myCell.x += int(math.cos(angle) * self.speed)
            self.myCell.y += int(math.sin(angle) * self.speed)

    def send_position_change(self):
        data = struct.pack('i d d i i i i', self.myCell.id, self.myCell.x, self.myCell.y,
                           self.myCell.mass, self.myCell.color[0], self.myCell.color[1], self.myCell.color[2])
        self.s.sendall(data)

    def get_enemies_position(self):
        self.players = []
        buffer = self.s.recv(4)
        (enemies_number,) = struct.unpack("i", buffer)
        for i in range(enemies_number):
            buffer = self.s.recv(40)
            myID, x, y, mass, r, g, b, enemies_number = struct.unpack('i d d i i i i', buffer)
            self.players.append(MyCell(myID, x, y, mass, (r, g, b)))

    def draw_everything(self):
        self.screen.fill((255, 255, 255))
        import pygame.gfxdraw
        font = pygame.font.Font(None, 24)
        for cell in self.players:
            # bigger balck circle
            pygame.gfxdraw.aacircle(self.screen, int(cell.x), int(cell.y), int(math.sqrt(cell.mass / math.pi)) + 2,
                                    (0, 0, 0))
            pygame.gfxdraw.filled_circle(self.screen, int(cell.x), int(cell.y), int(math.sqrt(cell.mass / math.pi)) + 2,
                                         (0, 0, 0))
            # smaller circle
            pygame.gfxdraw.aacircle(self.screen, int(cell.x), int(cell.y), int(math.sqrt(cell.mass / math.pi)),
                                    cell.color)
            pygame.gfxdraw.filled_circle(self.screen, int(cell.x), int(cell.y), int(math.sqrt(cell.mass / math.pi)),
                                         cell.color)
            text_surface = font.render(self.player_name, True, (255, 255, 255))  # Tworzy obiekt Surface z tekstem
            text_rect = text_surface.get_rect(center=(int(cell.x), int(cell.y)))  # Ustala pozycję tekstu na środku koła
            self.screen.blit(text_surface, text_rect)

        for food in self.foods:
            pygame.draw.circle(self.screen, (255, 0, 0), (int(food.x), int(food.y)), math.sqrt(200 / math.pi))
        pygame.display.flip()
        self.clock.tick(self.fps)

    def recieve_int(self):
        buffer = self.s.recv(4)
        number = struct.unpack("i", buffer)[0]
        return number

    def upload_map(self):

        # clear buffers
        self.players = []
        self.foods = []

        # get enemies
        enemies_n = self.recieve_int()
        for i in range(enemies_n):
            buffer = self.s.recv(40)
            myID, x, y, mass, r, g, b = struct.unpack('i d d i i i i', buffer)
            self.players.append(MyCell(myID, x, y, mass, (r, g, b)))

        # get foods
        for i in range(10):
            buffer = self.s.recv(16)
            x, y = struct.unpack('d d', buffer)
            self.foods.append(Food(x, y))

    def run(self):
        self.get_username()
        self.receive_cell()
        self.init_pygame()
        while self.running:
            self.handle_events()
            self.update_cell_position()
            self.send_position_change()
            self.upload_map()
            self.receive_cell()
            self.draw_everything()
        # end connection
        self.myCell.id = -1
        self.send_position_change()
        self.s.close()


def main():
    gui = GUI()
    gui.run()
    return


if __name__ == "__main__":
    main()

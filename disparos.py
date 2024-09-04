import pygame
import sys
import random
import tkinter
from tkinter import messagebox
import os
import time

# Inicializar Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Crear una pantalla
screen_info = pygame.display.Info()
ALTO = screen_info.current_h
ANCHO = screen_info.current_w
screen = pygame.display.set_mode((ANCHO, ALTO))

# Rutas de acceso de las imágenes
base_dir = os.path.dirname(os.path.abspath(__file__))

RUTA_JUGADOR = os.path.join(base_dir, "jugador.png")
RUTA_ALIEN = os.path.join(base_dir, "nave_enemiga.png")
RUTA_BALA = os.path.join(base_dir, "bala.png")
RUTA_LETRA_ARCADE = os.path.join(base_dir, "letra.TTF")
RUTA_VIDA = os.path.join(base_dir, "vida.png")
RUTA_MUSICA = os.path.join(base_dir, "musica.mp3")
RUTA_SONIDO_POTENCIADOR = os.path.join(base_dir, "potenciador.mp3")
RUTA_SONIDO_GAME_OVER = os.path.join(base_dir, "game_over.mp3")
RUTA_SONIDO_DISPARO = os.path.join(base_dir, "disparo.mp3")
RUTA_PUNT_MAX = os.path.join(base_dir, "puntuacion_maxima.txt")

# Cargar sonidos
sonido_game_over = pygame.mixer.Sound(RUTA_SONIDO_GAME_OVER)
sonido_potenciador = pygame.mixer.Sound(RUTA_SONIDO_POTENCIADOR)
sonido_disparo = pygame.mixer.Sound(RUTA_SONIDO_DISPARO)
pygame.mixer.music.load(RUTA_MUSICA)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)
sonido_disparo.set_volume(0.5)

# Establecer el título de la ventana
pygame.display.set_caption("Arcade Disparos")

# Definir colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL_OSCURO = (0, 0, 66)
ROJO = (255, 0, 0)

# Función para mostrar el mensaje de Game Over
def gameover():
    root = tkinter.Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    messagebox.showinfo("GAME OVER", f"Has perdido. ¡Más suerte la próxima vez!\n\tPuntuación:{puntuacion}\n\tNº de disparos:{jugador.disparos}")
    root.destroy()
    guardar_punt_max()  # Guardar la puntuación máxima antes de salir
    pygame.quit()
    sys.exit()

# Cargar la puntuación máxima al juego
punt_max = 0

def cargar_punt_max():
    global punt_max
    try:
        with open(RUTA_PUNT_MAX, "r") as file:
            punt_max = int(file.read().strip())
    except (FileNotFoundError, ValueError):
        punt_max = 0

def guardar_punt_max():
    global punt_max, puntuacion
    if puntuacion > punt_max:
        punt_max = puntuacion
        with open(RUTA_PUNT_MAX, "w") as file:
            file.write(str(punt_max))

# Inicializar puntuación
puntuacion = 0
fuente = pygame.font.Font(RUTA_LETRA_ARCADE, 36)

def cambiar_puntuacion(cantidad):
    global puntuacion
    puntuacion += cantidad
    
    # Comprobar si la puntuación ha llegado o superado los 1000 puntos
    if puntuacion % 1000 == 0 and vidas_obj.vidas < 3:
        vidas_obj.vidas += 1  # Sumar una vida si el jugador tiene menos de 3 vidas
    
def mostrar_puntuaciones():
    texto = fuente.render(f'{puntuacion}', True, BLANCO) 
    texto_punt_max = fuente.render(f'HIGH SCORE: {punt_max}', True, BLANCO) 
    margen = 10
    x_puntuacion = ANCHO - texto.get_width() - margen
    y_puntuacion = margen
    screen.blit(texto, (x_puntuacion, y_puntuacion))
    screen.blit(texto_punt_max, ((ANCHO / 2) - (texto_punt_max.get_width() / 2), 10))

# Clase de las vidas
class Vidas:
    def __init__(self):
        # Define el número inicial de vidas
        self.vidas = 3
        self.vidas_posiciones = [(10, 10), (50, 10), (90, 10)]  # Posiciones para dibujar las vidas
        self.image = pygame.image.load(RUTA_VIDA)
        self.image = pygame.transform.scale(self.image, (30, 30))  # Escalar la imagen si es necesario

    def dibujar(self, pantalla):
        # Dibuja la imagen de vida para cada vida restante
        for i in range(self.vidas):
            pantalla.blit(self.image, self.vidas_posiciones[i])

    def decrementar(self):
        # Decrementa el contador de vidas y verifica si se han agotado
        self.vidas -= 1
        if self.vidas <= 0:
            pygame.mixer.music.set_volume(0)
            sonido_game_over.play()
            time.sleep(0.5)
            gameover()

# Clase de las estrellas de fondo
class Estrella:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 2, 2)
        self.color = BLANCO

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)

# Clase del jugador
class Jugador:
    def __init__(self, x, y):
        self.image = pygame.image.load(RUTA_JUGADOR)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocidad = 5
        self.disparos = 0

    def mover(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
        if keys[pygame.K_UP]:
            self.rect.y -= self.velocidad
        if keys[pygame.K_DOWN]:
            self.rect.y += self.velocidad

        # Limitar el movimiento a los bordes de la pantalla
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > ANCHO - self.rect.width:
            self.rect.x = ANCHO - self.rect.width
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > ALTO - self.rect.height:
            self.rect.y = ALTO - self.rect.height

    def dibujar(self, pantalla):
        pantalla.blit(self.image, self.rect)

    def disparar(self, grupo_balas):
        # Crear una nueva bala en la posición del jugador
        bala = Bala(RUTA_BALA, self.rect.centerx, self.rect.top, -7)
        grupo_balas.add(bala)
        sonido_disparo.play()
        self.disparos += 1

# Clase de la nave de la máquina
class NaveEnemiga(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocidad = 3

    def update(self):
        # La nave se mueve hacia abajo y se elimina si sale de la pantalla
        self.rect.y += self.velocidad
        if self.rect.top > ALTO:
            self.kill()

# Clase de la bala de la nave del jugador y naves enemigas
class Bala(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, velocidad):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = velocidad

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.bottom < 0 or self.rect.top > ALTO:
            self.kill()

# Crear una instancia del jugador con una posición inicial dentro de la pantalla
jugador = Jugador(300, 500)

# Crear una instancia de las vidas
vidas_obj = Vidas()

# Crear instancias de múltiples estrellas para el fondo
estrellas = [Estrella(random.randint(0, ANCHO), random.randint(0, ALTO)) for _ in range(50)]

# Crear grupos para las balas del jugador, las naves enemigas y las balas enemigas
balas_jugador = pygame.sprite.Group()
naves_enemigas = pygame.sprite.Group()

# Reloj para controlar FPS
clock = pygame.time.Clock()

# Temporizador para generar naves enemigas
ENEMY_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(ENEMY_SPAWN_EVENT, 1000)  # Generar una nave enemiga cada segundo

# Cargar la puntuación máxima al inicio
cargar_punt_max()

# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            guardar_punt_max()  # Guardar la puntuación máxima antes de salir
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                jugador.disparar(balas_jugador)  # El jugador dispara una bala
        elif event.type == ENEMY_SPAWN_EVENT:
            # Crear una nave enemiga en una posición aleatoria
            x = random.randint(0, ANCHO - 50)
            nave = NaveEnemiga(x, -50, RUTA_ALIEN)
            naves_enemigas.add(nave)

    # Obtener el estado de las teclas
    keys = pygame.key.get_pressed()

    # Mover el jugador con imagen
    jugador.mover(keys)

    # Actualizar las balas y las naves enemigas
    balas_jugador.update()
    naves_enemigas.update()

    # Detectar colisiones
    # Eliminar naves enemigas que son impactadas por las balas del jugador
    colisiones = pygame.sprite.groupcollide(naves_enemigas, balas_jugador, True, True)
    
    # Sumar puntuación si se acierta
    if colisiones:
        cambiar_puntuacion(len(colisiones) + random.randint(30, 60))  # Incrementar puntuación según el número de colisiones

    # Comprobar colisiones entre las naves enemigas y el jugador
    if pygame.sprite.spritecollide(jugador, naves_enemigas, True):
        vidas_obj.decrementar()  # Decrementa vidas y chequea si se acabaron

    # Dibujar en la pantalla
    screen.fill(AZUL_OSCURO)

    # Dibujar estrellas
    for estrella in estrellas:
        estrella.dibujar(screen)

    # Dibujar jugador
    jugador.dibujar(screen)

    # Dibujar balas y naves enemigas
    balas_jugador.draw(screen)
    naves_enemigas.draw(screen)

    # Dibujar vidas
    vidas_obj.dibujar(screen)

    # Dibujar puntuación
    mostrar_puntuaciones()  # Llamar a la función para mostrar la puntuación actual

    # Actualizar la pantalla
    pygame.display.flip()

    # Controlar FPS
    clock.tick(60)

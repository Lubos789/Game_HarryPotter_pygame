import pygame
import random

# Inicializace hry
pygame.init()

# Obrazovka
width = 1200
height = 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Mozkomor Fight")

# Nastaveni hry
fps = 60
clock = pygame.time.Clock()

# Classy
class Game:
    def __init__(self, our_player, group_of_mozkomors):
        self.score = 0
        self.round_number = 0

        self.round_time = 0
        self.slow_down_cycle = 0

        self.our_player = our_player
        self.group_of_mozkomors = group_of_mozkomors

        # Hudba v pozadi
        pygame.mixer.music.load("media/bg-music-hp.wav")
        pygame.mixer.music.play(-1, 0.0)

        # Fonty
        self.potter_font = pygame.font.Font("fonts/Harry.ttf", 24)
        self.potter_font_big = pygame.font.Font("fonts/Harry.ttf", 60)

        # Obrazek v pozadi
        self.bg_image = pygame.image.load("img/bg-dementors.png")
        self.bg_image_rect = self.bg_image.get_rect()
        self.bg_image_rect.topleft = (0, 0)

        # Obrazky
        blue_image = pygame.image.load("img/mozkomor-modry.png")
        geren_image = pygame.image.load("img/mozkomor-zeleny.png")
        purple_image = pygame.image.load("img/mozkomor-ruzovy.png")
        yellow_image = pygame.image.load("img/mozkomor-zluty.png")
        # typy mozkomoru: 0 = modry, 1 = zeleny, 2 = rozovy, 3 = zluty
        self.mozkomors_images = [blue_image, geren_image, purple_image, yellow_image]

        # generujeme mozkomora, kteroho chceme chytit)
        self.mozkomor_catch_type = random.randint(0, 3)
        self.mozkomor_catch_image = self.mozkomors_images[self.mozkomor_catch_type]

        self.mozkomor_catch_image_rect = self.mozkomor_catch_image.get_rect()
        self.mozkomor_catch_image_rect.centerx = width//2
        self.mozkomor_catch_image_rect.top = 35


    # Kod, ktery je volan stale do kola
    def update(self):
        self.slow_down_cycle += 1
        if self.slow_down_cycle == 60:
            self.round_time += 1
            self.slow_down_cycle = 0


        # Kontrolu kolize
        self.check_collisions()

    # Vykresluje vse ve hre - texty, hledaneho mozkomora, skore
    def draw(self):
        dark_yellow = pygame.Color("#938f0c")
        blue = (21, 31, 217)
        green = (24, 194, 38)
        purple = (195, 23, 189)
        yellow = (195, 181, 23)
        # typy mozkomoru: 0 = modry, 1 = zeleny, 2 = rozovy, 3 = zluty
        colors = [blue, green, purple, yellow]

        # Nastaveni textu
        catch_text = self.potter_font.render("Hunting type of Mozkomor", True, dark_yellow)
        catch_text_rect = catch_text.get_rect()
        catch_text_rect.centerx = width//2
        catch_text_rect.top = 5

        score_text = self.potter_font.render(f"Score: {self.score}", True, dark_yellow)
        score_text_rect = score_text.get_rect()
        score_text_rect.topleft = (10, 4)

        lives_text = self.potter_font.render(f"Lives: {self.our_player.lives}", True, dark_yellow)
        lives_text_rect = lives_text.get_rect()
        lives_text_rect.topleft = (10, 30)

        round_text = self.potter_font.render(f"Round: {self.round_number}", True, dark_yellow)
        round_text_rect = round_text.get_rect()
        round_text_rect.topleft = (10, 60)

        time_text = self.potter_font.render(f"Round Time: {self.round_time}", True, dark_yellow)
        time_text_rect = time_text.get_rect()
        time_text_rect.topright = (width - 10, 5)

        back_safe_zone_text = self.potter_font.render(f"Safe Zone: {self.our_player.entre_safe_zone}", True, dark_yellow)
        back_safe_zone_text_rect = back_safe_zone_text.get_rect()
        back_safe_zone_text_rect.topright = (width - 10, 35)


        # Blitting (Vykresleni do obrazovky)
        screen.blit(catch_text, catch_text_rect)
        screen.blit(score_text, score_text_rect)
        screen.blit(lives_text, lives_text_rect)
        screen.blit(round_text, round_text_rect)
        screen.blit(time_text, time_text_rect)
        screen.blit(back_safe_zone_text, back_safe_zone_text_rect)
        # Obrazek mozkomara kteroho mam chytit
        screen.blit(self.mozkomor_catch_image, self.mozkomor_catch_image_rect)
        # Tvary
        # Ramecek herni plochy
        pygame.draw.rect(screen, colors[self.mozkomor_catch_type], (0, 100, width, height - 200), 4)

    # Kontruluje kolizi Harryho s mozkomor
    def check_collisions(self):
        # S jakym mozkomorem jsme se srazili? (pygame uklada do collided_mozkomor s kym kolidoval our_player)
        collided_mozkomor = pygame.sprite.spritecollideany(self.our_player, self.group_of_mozkomors)

        if collided_mozkomor:
            # Srazili jsme se ze sprvavnym mozkomorem
            if collided_mozkomor.type == self.mozkomor_catch_type:
                # Prehrajeme zvuk chyceni spravneho mozkomora
                self.our_player.catch_sound.play()
                # zvisime zkore
                self.score += 10 * self.round_number
                # Odsraneni chyceneho mozkomora
                collided_mozkomor.remove(self.group_of_mozkomors)
                # Existuji dalsi mozkomorove ktere muzeme chytat
                if self.group_of_mozkomors:
                    self.choose_new_targete()
                else:
                    # kolo je dokoncene, vsechny mozkomory jsem chytili
                    self.our_player.reset()
                    self.start_new_round()
            else:
                self.our_player.wrong_sound.play()
                self.our_player.lives -= 1
                # dosli zivoty, je hra u konce
                if self.our_player.lives <= 0:
                    self.pause_game(f"Your Score: {self.score}", "To continue push Enter")
                    self.reset_game()
                self.our_player.reset()


    # Zahaji nove kolo - s vetsim poctem mozkomoru herni polse
    def start_new_round(self):
        # pri dokonceni kola poskytneme bonus podle toho jak rychle dokonci, podle casu
        self.score += int(100 * (self.round_number / (1 + self.round_time)))

        # Resetujem hodnoty
        self.round_time = 0
        self.slow_down_cycle = 0
        self.round_number += 1
        self.our_player.entre_safe_zone += 1

        # Vycistime zkupinu mozkomoru, abychom mohli naplnit novymi
        for deleted_mozkomor in self.group_of_mozkomors:
            self.group_of_mozkomors.remove(deleted_mozkomor)

        for i in range(self.round_number):
            self.group_of_mozkomors.add(Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164),
                                                 self.mozkomors_images[0], 0))
            self.group_of_mozkomors.add(Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164),
                                                 self.mozkomors_images[1], 1))
            self.group_of_mozkomors.add(Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164),
                                                 self.mozkomors_images[2], 2))
            self.group_of_mozkomors.add(Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164),
                                                 self.mozkomors_images[3], 3))
        # Vybrat noveho mozkomora na chytani
        self.choose_new_targete()

    # Vybira novoho mzkomara, ktereho mame chytit
    def choose_new_targete(self):
        new_mozkomor_to_catch = random.choice(self.group_of_mozkomors.sprites())
        # print(new_mozkomor_to_catch)
        # print(new_mozkomor_to_catch.type)
        self.mozkomor_catch_type = new_mozkomor_to_catch.type
        self.mozkomor_catch_image = new_mozkomor_to_catch.image


    # Pozastaveni hry - pauza pred zahajenim nove hry, na zacatku pri spusteni
    def pause_game(self, main_text, subheading_text):
        global lets_continue
        # Nastaveni barvy
        dark_yellow = pygame.Color("#938f0c")
        black = (0, 0, 0)

        # Hlavni text pro pauznuti
        main_text_create = self.potter_font_big.render(main_text, True, dark_yellow)
        main_text_create_rect = main_text_create.get_rect()
        main_text_create_rect.center = (width//2, height//2 - 30)

        # Podnadpis pro pauznuti
        subheading_text_create = self.potter_font.render(subheading_text, True, dark_yellow)
        subheading_text_create_rect = subheading_text_create.get_rect()
        subheading_text_create_rect.center = (width//2, height//2 + 80)

        # Zobrazeni hlavniho textu a podnadpisu
        screen.fill(black)
        screen.blit(main_text_create, main_text_create_rect)
        screen.blit(subheading_text_create, subheading_text_create_rect)
        pygame.display.update()

        # Zastaveni hry
        paused = True
        while paused:
            for one_event in pygame.event.get():
                if one_event.type == pygame.KEYDOWN:
                    if one_event.key == pygame.K_RETURN:
                        paused = False
                if one_event.type == pygame.QUIT:
                    paused = False
                    lets_continue = False


    # Resetuje hru do vychoziho stavu
    def reset_game(self):
        self.score = 0
        self.round_number = 0

        self.our_player.lives = 5
        self.our_player.entre_safe_zone = 3
        self.start_new_round()

        # Spusteni muziky v pozadi
        pygame.mixer.music.play(-1, 0.0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("img/potter-icon.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = width//2
        self.rect.bottom = height

        self.lives = 5
        self.entre_safe_zone = 3
        self.speed = 8

        self.catch_sound = pygame.mixer.Sound("media/expecto-patronum.mp3")
        self.catch_sound.set_volume(0.1)
        self.wrong_sound = pygame.mixer.Sound("media/wrong.wav")
        self.wrong_sound.set_volume(0.1)

    # Kod, ktery je volan stale dokola
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < width:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 100:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < height - 100:
            self.rect.y += self.speed

    # Navrat do bezpecno zony dole na horni plose
    def back_to_safe_zone(self):
        if self.entre_safe_zone > 0:
            self.entre_safe_zone -= 1
            self.rect.bottom = height

    # Vraci hrace zpet na vychozi pozici - doprostred bezpecne zony
    def reset(self):
        self.rect.centerx = width//2
        self.rect.bottom = height

class Mozkomor(pygame.sprite.Sprite):
    def __init__(self, x, y, image, mozkomor_type):
        super(). __init__()
        # nahrajeme obrazek mozkomora a umistime ho
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # typy mozkomoru: 0 = modry, 1 = zeleny, 2 = rozovy, 3 = zluty
        self.type = mozkomor_type

        # nastaveni hodoneho smeru mozkomora
        self.x = random.choice([-1, 1])
        self.y = random.choice([-1, 1])
        self.speed = random.randint(1, 5)

    # kod, ktery je volan stale dokola
    def update(self):
        # pohyb mozkomora
        self.rect.x += self.x * self.speed
        self.rect.y += self.y * self.speed

        # odraz mozkomora
        if self.rect.left < 0 or self.rect.right > width:
            self.x = -1 * self.x
        if self.rect.top < 100 or self.rect.bottom > height - 100:
            self.y = -1 * self.y

# Skupina mozkomoru
mozkomor_group = pygame.sprite.Group()
# # Testovaci mozkomorove
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-modry.png"), 0)
# mozkomor_group.add(one_mozkomor)
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-zeleny.png"), 1)
# mozkomor_group.add(one_mozkomor)
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-ruzovy.png"), 2)
# mozkomor_group.add(one_mozkomor)
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-zluty.png"), 3)
# mozkomor_group.add(one_mozkomor)


# Skupina hracu
player_group = pygame.sprite.Group()
one_player = Player()
player_group.add(one_player)

# Objekt Game
my_game = Game(one_player, mozkomor_group)
my_game.pause_game("Harry Potter and fight with Mozkomors", "Press Enter to Start Game")
my_game.start_new_round()

# Hlavni Cyklus hry
lets_continue = True
while lets_continue:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            lets_continue = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                one_player.back_to_safe_zone()

    # Vyplneni plochy
    # screen.fill((0, 0, 0))
    screen.blit(my_game.bg_image, my_game.bg_image_rect)

    # Updatujeme skupinu mozkomoru
    mozkomor_group.draw(screen)
    mozkomor_group.update()
    # Updatujem skupinu hracu (jeden hrac)
    player_group.draw(screen)
    player_group.update()
    # Updatujeme objekt vytovoreni podle classy Game
    my_game.update()
    my_game.draw()

    # Update Obrazovky
    pygame.display.update()

    # Zpomaleni cyklu
    clock.tick(fps)

# Ukonceni hry
pygame.quit()
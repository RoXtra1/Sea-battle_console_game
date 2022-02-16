from random import randint
import time

class BoardException(Exception):
    pass
class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы вне игрового поля'
class BoardUsedException(BoardException):
    def __str__(self):
        return 'Сюда уже стреляли'
class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y): # точка имеет координаты
        self.x = x
        self.y = y

    def __eq__(self, other): # упрощаем сравнивание двух точек (их координат)
        return self.x == other.x and self.y == other.y

    def __repr__(self): # показ точки
        return f'Dot({self.x}; {self.y})'

class Ship:
    def __init__(self, point, len, direction): # параметры корабля
        self.point, self.len, self.direction, self.hp = point, len, direction, len

    @property
    def dots(self):
        ship_dots = [] #список точек кораблей
        for i in range (self.len): #идем по длине корабля в нужном направлении и добавляем каждую точку в список
            cur_x = self.point.x
            cur_y = self.point.y

            if self.direction == 0: cur_x += i
            elif self.direction == 1: cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot): #подстрелена ли точка корабля
        return shot in self.dots

class Board:                                                            # класс поля
    def __init__(self, hid = False, size = 6):                          # параметры размер и нужно ли скрывать
        self.hid, self.size = hid, size

        self.deth_count = 0                                             # количество мертвых кораблей
        self.busy = []                                                  # массив занятых кораблем(корабль+вокруг) и выстрелом точек
        self.ships = []                                                 # список кораблей на доске

        self.field = [["O"] * size for _ in range(size)]                # поле с площадью size*size

    def __str__(self):                                                  # вывод корабля на доску Print(Board())
        res = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:                                                    #замена всех клеток корабля на пустые клетки
            res = res.replace("■", "O")
        return res

    def out(self, d):                                                   #проверка что точка за границами карты
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):                                #контур вокруг корабля
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for dx, dy in near:
                cur = Dot(dot.x + dx, dot.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:                                            #решает будет ли заменяться точка из списка занятых
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:                       #если точка из списка точек кораблей вне корабля или занята
                raise BoardWrongShipException()                         #получаем исключение
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):                                                  #выстрел
        if self.out(d):                                                 #если вне поля - ошибка
            raise BoardOutException()

        if d in self.busy:                                              #если точка уже занята - ошибка
            raise BoardUsedException()

        self.busy.append(d)                                             #точка становится занятой

        for ship in self.ships:
            if ship.shooten(d):
                ship.hp -= 1
                self.field[d.x][d.y] = "X"
                if ship.hp == 0:
                    self.deth_count += 1
                    self.contour(ship, verb=True)
                    print("Убил!")
                    return False                                        #после уничтожения корабля ход не делается
                else:
                    print("Ранил!")
                    return True                                         #после ранения делается

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False                                                    #и после промаха не делается

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.deth_count == len(self.ships)

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def move(self): #бесконечный цикл шагов
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(1, 6), randint(1, 6))
        print(f"Ход компьютера: {d.x} {d.y}")
        return Dot(d.x-1, d.y-1)

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size =self.size)
        tryes = 0                               #попытки создания доски
        for l in self.lens:
            while True:
                tryes += 1
                if tryes > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("+-----------------+")
        print("| Приветсвуем вас |")
        print("|     в игре      |")
        print("|   морской бой   |")
        print("+-----------------+")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_boards(self):
        print("-" * 20)
        print("Поле пользователя:")
        print(self.us.board)
        print("-" * 20)
        print("Поле компьютера:")
        print(self.ai.board)
        print("-" * 20)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                repeat = self.us.move()
            else:
                print("Компьютер думает...")
                time.sleep(3.5)
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():
                self.print_boards()
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
import pygame, sys
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
import numpy as np
import os
import pymysql
import cv2

connection = pymysql.connect(host="mysql",
                             user="root",
                             passwd="123456",
                             database="example",
                             charset="utf8")

mycursor = connection.cursor()



class Pathfinder:
    def __init__(self, matrix):

        # setup
        self.matrix = matrix  # 圍牆與道路的array
        self.grid = Grid(matrix=matrix)  # 創建網格

        # pathfinding
        self.path = []  # 創立路線空陣列

    # 畫出路線
    def draw_path(self, screen):
        if self.path:
            points = []
            for point in self.path:
                x = (point[0] * 8) + 4
                y = (point[1] * 8) + 4
                points.append((x, y))
                # 畫圓點路線
                pygame.draw.circle(screen, '#ff0000', (x, y), 3)

            # pygame.draw.lines(screen, '#4a4a4a', False, points, 5)

    def create_path(self, start_x, start_y, end_x, end_y):

        # start
        # 設定當前位置
        start = self.grid.node(start_x, start_y)

        # end
        # 設定目標點
        end = self.grid.node(end_x, end_y)

        # path A*
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        self.path, _ = finder.find_path(start, end, self.grid)

        self.path.pop(0)  # 移除第一個元素(避免蓋到當前座標)

        return self.path


def set_roomba_path(x, y, screen):
    # # 設定人物起始座標圖片
    image = pygame.image.load('selection.png').convert_alpha()

    rect = image.get_rect(center=(x, y))
    screen.blit(image, rect)


def get_map_path(start_x, start_y, end_x, end_y):
    pygame.init()
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    screen = pygame.display.set_mode((1200, 800))  # 設定畫布大小

    bg_surf = pygame.image.load('carrefour_map.png').convert()  # 設定畫布在螢幕上顯示速度
    screen.blit(bg_surf, (0, 0))  # 覆蓋整個視窗畫布  (0,0)為起始位置

    # 載入圍牆跟道路的設定csv
    with open("./csv/map_collision.csv") as file_name:
        array = np.loadtxt(file_name, delimiter=",")

    # 初始化路線物件，並匯入網格設定csv
    pathfinder = Pathfinder(array)

    # 畫當前人物座標圖示
    set_roomba_path(start_x, start_y, screen)
    # //8 是為了網格
    output_path = pathfinder.create_path(start_x // 8, start_y // 8, end_x // 8, end_y // 8)

    # 畫路線原點
    pathfinder.draw_path(screen)

    # save picture
    fname = 'map_path.png'
    pygame.image.save(screen, fname)
    print("type:", screen)
    print("file {} has been saved".format(fname))

    # 需加以下關閉避免記憶體爆掉(?)
    pygame.quit()
    sys.exit()

    return screen, output_path  # 輸出路線陣列

def get_staff_info_one():
    while True:
        name = input("請輸入商品類別:")
        if name == "": break
        sql_2 = "SELECT X , Y FROM C_10 WHERE goods ='" + name + "'"
        mycursor.execute(sql_2)
        # print(sql_2)
        staff_data = mycursor.fetchone()
        if (staff_data == None):
            print("查無此商品".format(name))
            continue

        for x in staff_data:
            print(x, type(x))

        ans = tuple([x*8 for x in staff_data])
        start_xx = 72 * 8
        start_yy = 56 * 8
        end_xx = ans[0]
        end_yy = ans[1]
        print("ans:",ans)
        print(type(ans))
        if name in sql_2:
            gc = cv2.imread('./image/carrefour_map.png', 1)
            cv2.circle(gc, ans, 4, (0, 10, 255), -1)
            # cv2.imshow('draw', gc)
            cv2.imwrite('carrefour_map.png', gc)

            # 找不到路線會回傳原始地圖與空字串
            screen, map_path = get_map_path(start_xx, start_yy, end_xx, end_yy)
            print(map_path)  # 輸出路線[陣列(tuple)]

            # save picture
            fname = 'map_path.png'
            pygame.image.save(screen, fname)
            print("type:", screen)
            print("file {} has been saved".format(fname))

            # 需加以下關閉避免記憶體爆掉(?)
            pygame.quit()
            sys.exit()

        else:
            print('沒有此商品')
            # cv2.imshow('plan', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # cv2.waitKey(1)
        return staff_data


# myresult = mycursor.fetchall()


if __name__ == "__main__":
    # # 設定實際圖檔大小的位置即可
    # start_xx = 72 * 8
    # start_yy = 58 * 8
    # end_xx = 100 * 8
    # end_yy = 57 * 8

    get_staff_info_one()
    # 找不到路線會回傳原始地圖與空字串
    # screen, map_path = get_map_path(start_xx, start_yy, end_xx, end_yy)
    # print(map_path)  # 輸出路線[陣列(tuple)]







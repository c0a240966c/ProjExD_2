import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = { #移動量辞書
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0, +5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """ 
    引数:こうかとんRectまたは爆弾Rect
    戻り値:横方向, 縦方向の画面外判定結果
    画面内ならTrue, 画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or rct.right > WIDTH:
        yoko = False
    if rct.top < 0 or rct.bottom > HEIGHT:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    """
    こうかとんが爆弾に当たった時のゲームオーバー画面を表示する関数

    引数:
        screen: 黒画面
    """
    # 半透明の黒い背景を表示
    black = pg.Surface((WIDTH, HEIGHT))
    black.set_alpha(200) #数値が高いほど透明度が低くなる
    pg.draw.rect(black, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT))  # 黒い四角を描画
    screen.blit(black, (0, 0))  # 半透明の黒いSurfaceを画面に貼り付け

    # 泣いているこうかとん画像を表示
    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.1)
    kk_rct = kk_img.get_rect()
    screen.blit(kk_img, (330, 300))
    screen.blit(kk_img, (730, 300))
    # 「Game Over」の文字を表示
    font = pg.font.Font(None, 80) # フォントオブジェクトを作成（デフォルトフォント, サイズ80）
    txt = font.render("Game Over", True, (255, 255, 255)) # テキストを白で描画
    screen.blit(txt,(400, 300))

    pg.display.update()
    time.sleep(5) #時を5秒止める
def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    爆弾の大きさに応じたSurfaceのリストと加速度リストを返す関数

    戻り値:
        爆弾画像リスト, 加速度リスト
    """
    bb_imgs = []  # 爆弾画像のリスト
    bb_accs = [a for a in range(1, 11)]  # 加速度リスト
    for r in range(1, 11):  # 1倍〜10倍
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))  # 黒背景を透明に
        bb_imgs.append(bb_img)
        bb_accs.append(r)  # 加速度：1〜10
    return bb_imgs, bb_accs
def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    """
    移動量の合計値タプルに応じて画像を回転し、向きを変えたこうかとん画像を返す関数

    引数:
        sum_mv: 押下キーによる移動量の合計タプル (x, y)

    戻り値:
        回転済みのこうかとん画像Surface
    """
    base_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)  # 基本画像を読み込み

    direction_to_angle = {
        (-5, -5): -45,
        (0, -5):  -90,
        (+5, -5): -45,
        (-5, 0):  180,
        (0, 0):     0,
        (+5, 0):    0,     # → 右を向くように変更（反転不要）
        (-5, +5): -135,
        (0, +5):  90,
        (+5, +5): -135
    }

    angle = direction_to_angle.get(sum_mv, 0)  # 該当がなければ0度
    rotated_img = pg.transform.rotate(base_img, angle)
    if sum_mv == (0, +5) or (0, -5):
        rotated_img = pg.transform.flip(rotated_img, True, False)
    if sum_mv == (-5, 0):
        rotated_img = pg.transform.flip(rotated_img, False, True)

    return rotated_img

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = get_kk_img((0, 0))
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20,20)) # 透明背景の画像
    pg.draw.circle(bb_img, (255,0,0),(10,10),10) # 中心に赤い円（爆弾）
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    
    bb_rct.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))  # ランダムな位置に配置
    clock = pg.time.Clock()
    tmr = 0
    vx, vy = +5, +5

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, delta in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += delta[0]
                sum_mv[1] += delta[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        # screen.blit(kk_img, kk_rct)
        kk_img = get_kk_img(tuple(sum_mv))  # 向きに応じて画像を回転
        screen.blit(kk_img, kk_rct)
        
        #拡大、加速
        bb_imgs, bb_accs = init_bb_imgs()
        avx = vx*bb_accs[min(tmr//500, 9)]
        avy = vy*bb_accs[min(tmr//500, 9)]
        bb_img = bb_imgs[min(tmr//500, 9)]
        bb_rct.move_ip(avx, avy)
        bb_rct.move_ip(vx, vy)

        yoko, tate = check_bound(bb_rct) 
        if not yoko: #横方向にはみ出ていたら
            vx *= -1
        if not tate: #縦方向にはみ出ていたら
            vy *= -1
        
        if kk_rct.colliderect(bb_rct): #ゲームオーバー
            gameover(screen)
            return
        
        screen.blit(bb_img, bb_rct)
    
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

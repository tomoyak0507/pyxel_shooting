import pyxel

WIDTH, HEIGHT = 160, 120
pyxel.init(WIDTH, HEIGHT, title="Mini STG")
pyxel.images[0].load(0, 0, "resource/starships.png")
pyxel.images[1].load(0, 0, "resource/bg.png")
pyxel.images[2].load(0, 0, "resource/回復.png")

TITLE, PLAY, OVER = 0, 1, 2 # 画面遷移用の定数
scene = TITLE # 現在のシーン
timer = 0 # 時間を管理
score = 0 # スコア
hisco = 5000 # ハイスコア
SHIELD_MAX = 2 # シールド最大値
shield = SHIELD_MAX # 自機のシールド

def scroll_bg(): # 背景のスクロール
    ofx = pyxel.frame_count % 16 # 画像をずらすための値を計算
    for i in range(11): # 床のスクロール
        pyxel.blt(i * 16 - ofx, HEIGHT - 16, 1, 0, 0, 16, 16)
    for i in range(1, 9): # グラデーション
        pyxel.dither(i / 8)
        pyxel.rect(0, HEIGHT - (13 - i) * 4, WIDTH, 4, 2)
    pyxel.dither(1.0)

pl_x, pl_y = 30, 40 # 自機の座標を代入する変数

def move_player(): # 自機をカーソルキーで動かす
    global pl_x, pl_y
    if pyxel.btn(pyxel.KEY_UP) and pl_y > 12: # 上キー
        pl_y -= 2
    if pyxel.btn(pyxel.KEY_DOWN) and pl_y < HEIGHT - 20: # 下キー
        pl_y += 2
    if pyxel.btn(pyxel.KEY_LEFT) and pl_x > 10: # 左キー
        pl_x -= 2
    if pyxel.btn(pyxel.KEY_RIGHT) and pl_x < WIDTH - 10: # 右キー
        pl_x += 2
    if pyxel.btnp(pyxel.KEY_SPACE, 0, 10): # スペースキー
        set_bullet(pl_x, pl_y, 10, 0)
        
# 自機から発射する弾を制御する配列
BUL_MAX = 10
bul_x  = [0] * BUL_MAX
bul_y  = [0] * BUL_MAX
bul_vx = [0] * BUL_MAX
bul_vy = [0] * BUL_MAX
bul_flag = [False] * BUL_MAX

def set_bullet(x, y, vx, vy): # 弾をセットする
    for i in range(BUL_MAX):
        if bul_flag[i] == True: continue
        bul_x[i] = x
        bul_y[i] = y
        bul_vx[i] = vx
        bul_vy[i] = vy
        bul_flag[i] = True
        break

def move_bullet(): # 弾を動かす
    for i in range(BUL_MAX):
        if bul_flag[i] == False: continue
        bul_x[i] += bul_vx[i]
        bul_y[i] += bul_vy[i]
        if bul_x[i] > WIDTH:
            bul_flag[i] = False

def draw_bullet(): # 弾を表示する
    for i in range(BUL_MAX):
        if bul_flag[i] == True:
            pyxel.blt(bul_x[i] - 4, bul_y[i] - 4, 0, 16, 0, 8, 8, 0)

# 敵機用の定数、配列
NONE, ROTATE, PARABOLA, BATTERY, BULLET, KAIHUKU = -1, 0, 1, 2, 3, 4 # 種類
EMY_MAX = 20
emy_x  = [0] * EMY_MAX
emy_y  = [0] * EMY_MAX
emy_vx = [0] * EMY_MAX
emy_vy = [0] * EMY_MAX
emy_type = [NONE] * EMY_MAX
emy_damage = [0] * EMY_MAX

def init_enemy(): # 全ての敵機を出現していない状態にする
    for i in range(EMY_MAX):
        emy_type[i] = NONE

def set_enemy(x, y, vx, vy, typ): # 敵機をセットする
    for i in range(EMY_MAX):
        if emy_type[i] != NONE: continue
        if emy_damage[i] > 0: continue
        emy_x[i] = x
        emy_y[i] = y
        emy_vx[i] = vx
        emy_vy[i] = vy
        emy_type[i] = typ
        break

def move_enemy(): # 敵機を動かす
    global score, shield
    for i in range(EMY_MAX):
        if emy_type[i] == NONE: continue

        if emy_type[i] == PARABOLA: # 放物線を描く敵の動き
            emy_vx[i] += 0.5

        if emy_type[i] == BATTERY: # 砲台が弾を撃つ
            if emy_x[i] % 60 == 30:
                set_enemy(emy_x[i] - 4, emy_y[i] - 4, -2, pyxel.rndi(-2, 0), BULLET)

        if emy_type[i] != BULLET:
            if hit_chk_emy_bul(i): # 弾とのヒットチェック
                if emy_type[i] !=  KAIHUKU:
                    
                    emy_damage[i] = 10 # 爆発演出
                    score += 100
                    emy_type[i] = NONE # 敵を消す

        if hit_chk_emy_pl(i): # 自機とのヒットチェック
            print(emy_type[i])
            if emy_type[i] ==  KAIHUKU:
               if shield< 3:
                   shield += 1

            else:
                emy_damage[i] = 10 # 爆発演出
                shield -= 1 # 自機のシールドを減らす
       
            emy_type[i] = NONE # 敵を消す
            
        emy_x[i] += emy_vx[i]
        emy_y[i] += emy_vy[i]
        if emy_x[i] < -10 or WIDTH + 10 < emy_x[i]: # 画面の外に出た
            emy_type[i] = NONE # 敵を消す

def draw_enemy(): # 敵機を表示する
    for i in range(EMY_MAX):
        if emy_damage[i] > 0: # 爆発演出
            pyxel.circ(emy_x[i], emy_y[i], 5, pyxel.rndi(7, 10))
            emy_damage[i] -= 1
        if emy_type[i] == NONE: continue
        
        ang = 0 # 画像の回転角度
        if emy_type[i] == ROTATE: # 回転する敵
            ang = pyxel.frame_count * 10

        if emy_type[i] == KAIHUKU:
            sx = 0
            pyxel.blt(emy_x[i] - 4, emy_y[i] - 4, 2, sx, 0, 16, 16, 0, ang)
        else:
            sx = 24 + emy_type[i] * 8 # 画像の切り出し位置
            pyxel.blt(emy_x[i] - 4, emy_y[i] - 4, 0, sx, 0, 8, 8, 0, ang)

def hit_chk_emy_bul(n): # 敵機と弾とのヒットチェック
    for i in range(BUL_MAX):
        if bul_flag[i] == False: continue
        dx = abs(emy_x[n] - bul_x[i]) # x軸方向の距離
        dy = abs(emy_y[n] - bul_y[i]) # y軸方向の距離
        if dx < 8 and dy < 5: # 重なる条件
            bul_flag[i] = False # 弾を消す
            return True # 弾が当たったらTrueを返す
    return False

def hit_chk_emy_pl(n): # 敵機と自機とのヒットチェック
    dx = abs(emy_x[n] - pl_x) # x軸方向の距離
    dy = abs(emy_y[n] - pl_y) # y軸方向の距離
    if dx < 10 and dy < 7: # 重なる条件
        return True # 自機とぶつかったらTrueを返す
    return False

def update(): # メイン処理（計算、判定を行う）
    global scene, timer, score, hisco, shield, pl_x, pl_y

    if scene == TITLE: # タイトル
        if pyxel.btnp(pyxel.KEY_SPACE): # SPACEキーで開始
            pl_x = 10
            pl_y = HEIGHT // 2
            init_enemy()
            scene = PLAY
            timer = 0
            score = 0
            shield = SHIELD_MAX
            pyxel.rseed(0) # 乱数の種をセット：これで敵の出現パターンを固定

    if scene == PLAY: # ゲームプレイ
        timer += 1
        if timer % 30 == 0: # 回転する敵が出現
            set_enemy(WIDTH, pyxel.rndi(12, HEIGHT - 28), pyxel.rndi(-2, -1), 0, ROTATE)
        if timer % 90 == 0: # 放物線を描く敵が出現
            set_enemy(WIDTH, HEIGHT // 2, pyxel.rndi(-12, -8), pyxel.rndi(-2, 2), PARABOLA)
        if timer % 180 == 0: # 砲台が出現
            set_enemy(WIDTH, HEIGHT - 20, -1, 0, BATTERY)
        if timer % 300 == 0: # 回復が出現
            set_enemy(WIDTH, pyxel.rndi(12, HEIGHT - 28), pyxel.rndi(-4, -3), 0, KAIHUKU)
            
        move_player() # 自機の移動
        move_bullet() # 弾の移動
        move_enemy() # 敵機の移動
        if score > hisco:
            hisco = score # ハイスコアを更新
        if shield <= 0: # シールドが無くなった
            scene = OVER
            timer = 150

    if scene == OVER: # ゲームオーバー
        timer -= 1
        if timer == 0:
            scene = TITLE

def draw(): # 描画処理
    pyxel.cls(0) # 画面をクリアする
    scroll_bg() # 画面をスクロールさせる関数を呼び出す

    if scene == TITLE: # タイトル
        pyxel.text(WIDTH / 2 - 26, HEIGHT * 0.3, "SHOOTING GAME", 11)
        pyxel.text(WIDTH / 2 - 28, HEIGHT * 0.7, "[SPACE] Start.", pyxel.rndi(7, 10))

    if scene == PLAY: # ゲームプレイ
        pyxel.blt(pl_x - 8, pl_y - 4, 0, 0, 0, 16, 8, 0) # 自機の表示
        draw_bullet() # 弾の表示
        draw_enemy() # 敵機の表示

    if scene == OVER: # ゲームオーバー
        pyxel.text(WIDTH / 2 - 18, HEIGHT * 0.3, "GAME OVER", 8)

    pyxel.text(1, 1, f'SCORE {score}', 7) # スコア
    pyxel.text(WIDTH / 2, 1, f'HI-SC {hisco}', 10) # ハイスコア
    for i in range(shield): # シールドのメーター
        pyxel.rect(1 + i * 12, HEIGHT - 4, 11, 3, 11)
        pyxel.rect(2 + i * 12, HEIGHT - 3, 9, 1, 7)

pyxel.run(update, draw)

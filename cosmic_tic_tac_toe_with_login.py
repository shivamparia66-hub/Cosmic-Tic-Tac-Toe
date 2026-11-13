# COSMIC TIC-TAC-TOE - Android/Pydroid 3 edition
# Install pygame in Pydroid 3. Keep cosmic_sound_effects folder beside this file.
import pygame, random, math, json, os, sys
pygame.init()
try:
    pygame.mixer.init()
    AUDIO=True
except pygame.error:
    AUDIO=False

# Full screen (Android may keep system navigation controls depending on OS settings)
info=pygame.display.Info()
W,H=max(320,info.current_w),max(480,info.current_h)
screen=pygame.display.set_mode((W,H), pygame.FULLSCREEN)
pygame.display.set_caption('Cosmic Tic-Tac-Toe')
clock=pygame.time.Clock()
BASE=os.path.dirname(os.path.abspath(__file__))
SAVE=os.path.join(BASE,'cosmic_save.json')
SOUND_DIR=os.path.join(BASE,'cosmic_sound_effects')
DEFAULT={'points':0,'xp':0,'level':1,'volume':70,'animations':True,'owned':['Classic'],'theme':'Classic','symbol':'Classic','wins':0,'draws':0,'losses':0}
try:
    with open(SAVE,'r') as f: data=DEFAULT|json.load(f)
except Exception: data=DEFAULT.copy()

def save():
    with open(SAVE,'w') as f: json.dump(data,f)

def load_sound(name):
    if not AUDIO: return None
    try: return pygame.mixer.Sound(os.path.join(SOUND_DIR,name+'.wav'))
    except (pygame.error,OSError): return None
SOUNDS={k:load_sound(v) for k,v in {
 'tap':'move_1_soft_tap','arcade':'move_2_arcade_blip','crystal':'move_3_crystal_ping',
 'pulse':'move_4_sci_fi_pulse','win':'victory_fanfare','draw':'draw_falling_tone','whoosh':'menu_whoosh'}.items()}

def play(name):
    s=SOUNDS.get(name)
    if s and data['volume']>0:
        s.set_volume(data['volume']/100); s.play()

BG=(5,8,28); WHITE=(240,246,255); MUTED=(150,174,215); BLUE=(0,220,255); PINK=(255,70,150); GOLD=(255,205,65); PURPLE=(160,100,255); GREEN=(70,255,190)
THEMES={'Classic':(BG,BLUE,PINK),'Ocean':((3,20,42),(50,220,255),(80,255,180)),'Sunset':((35,8,35),(255,180,60),(255,70,130)),'Emerald':((3,25,22),(80,255,170),(180,255,80))}
ITEMS=[('Classic',0),('Ocean',150),('Sunset',250),('Emerald',350),('Gold X/O',200)]
FONT={}
def fnt(n,b=False):
    k=(n,b)
    if k not in FONT: FONT[k]=pygame.font.SysFont('arial',n,bold=b)
    return FONT[k]
def txt(s,size,color,center,bold=False):
    im=fnt(size,bold).render(str(s),True,color); screen.blit(im,im.get_rect(center=center))
def button(rect,label,color=BLUE,size=20):
    r=pygame.Rect(rect); pygame.draw.rect(screen,(13,25,65),r,border_radius=14); pygame.draw.rect(screen,color,r,2,border_radius=14); txt(label,size,WHITE,r.center,True); return r

def level_from_xp(xp): return min(50,1+xp//100)
data['level']=level_from_xp(data['xp'])

# ---------------- PLAYER LOGIN / REGISTER ----------------
ACCOUNTS=os.path.join(BASE,'cosmic_users.json')
try:
    with open(ACCOUNTS,'r',encoding='utf-8') as f: accounts=json.load(f)
except Exception:
    accounts={}

auth_mode='register'
auth_fields=[['FULL NAME',''],['GMAIL ADDRESS',''],['CREATE GAME PASSWORD',''],['CONFIRM PASSWORD','']]
auth_login_fields=[['GMAIL ADDRESS',''],['GAME PASSWORD','']]
auth_active=0
auth_message='Create your player account'
auth_color=MUTED
player_name=''

def auth_fields_now():
    return auth_fields if auth_mode=='register' else auth_login_fields

def auth_hash(password,salt=None):
    salt=salt or secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),salt.encode('utf-8'),150000).hex()
    return salt,digest

def auth_save():
    with open(ACCOUNTS,'w',encoding='utf-8') as f:
        json.dump(accounts,f,indent=2)

def auth_draw():
    screen.fill(BG)
    for i in range(55):
        pygame.draw.circle(screen,(45,65,115),((i*197+29)%W,(i*113+41)%H),1)
    pw=min(int(W*.90),680); ph=min(int(H*.94),1250)
    panel=pygame.Rect((W-pw)//2,(H-ph)//2,pw,ph)
    pygame.draw.rect(screen,(13,23,58),panel,border_radius=24)
    pygame.draw.rect(screen,BLUE,panel,2,border_radius=24)
    txt('COSMIC TIC-TAC-TOE',max(25,min(38,W//10)),WHITE,(W//2,panel.top+int(ph*.065)),True)
    txt('PLAYER ACCOUNT',18,BLUE,(W//2,panel.top+int(ph*.125)),True)
    txt('CREATE ACCOUNT' if auth_mode=='register' else 'WELCOME BACK',25,WHITE,(W//2,panel.top+int(ph*.19)),True)
    fs=auth_fields_now(); top=panel.top+int(ph*.275)
    gap=int(ph*(.112 if auth_mode=='register' else .17))
    bh=max(48,int(ph*.068)); bw=int(pw*.84); left=(W-bw)//2
    auth_rects=[]
    for i,(label,value) in enumerate(fs):
        yy=top+i*gap
        txt(label,15,MUTED,(left+bw//2,yy-12),True)
        rr=pygame.Rect(left,yy,bw,bh); auth_rects.append(rr)
        pygame.draw.rect(screen,(6,12,37),rr,border_radius=10)
        pygame.draw.rect(screen,BLUE if i==auth_active else (75,95,145),rr,2,border_radius=10)
        shown=('•'*len(value)) if 'PASSWORD' in label else value
        if not shown: shown='Tap here to enter'
        im=fnt(16).render(shown,True,WHITE if value else MUTED)
        screen.blit(im,(rr.x+12,rr.y+(bh-im.get_height())//2))
    by=top+len(fs)*gap+int(ph*.018)
    auth_button=pygame.Rect(left,by,bw,max(52,int(ph*.075)))
    button(auth_button,'CREATE ACCOUNT' if auth_mode=='register' else 'LOGIN',PINK if auth_mode=='register' else BLUE,19)
    switch_y=auth_button.bottom+int(ph*.055)
    switch='Already registered? LOGIN' if auth_mode=='register' else 'New player? CREATE ACCOUNT'
    txt(switch,15,GOLD,(W//2,switch_y),True)
    txt(auth_message,14,auth_color,(W//2,min(panel.bottom-int(ph*.075),switch_y+int(ph*.075))))
    return auth_rects,auth_button,switch_y

def auth_register():
    global auth_message,auth_color,player_name
    name,email,password,confirm=[v.strip() for _,v in auth_fields]
    email=email.lower()
    if not name: auth_message,auth_color='Enter your full name.',PINK
    elif not re.fullmatch(r'[a-zA-Z0-9._%+-]+@gmail\.com',email): auth_message,auth_color='Enter a valid @gmail.com address.',PINK
    elif len(password)<6: auth_message,auth_color='Game password needs at least 6 characters.',PINK
    elif password!=confirm: auth_message,auth_color='Passwords do not match.',PINK
    elif email in accounts: auth_message,auth_color='Account already exists. Please login.',PINK
    else:
        salt,digest=auth_hash(password)
        accounts[email]={'name':name,'salt':salt,'hash':digest}
        auth_save(); player_name=name
        auth_message,auth_color='Account created! Welcome '+name+'!',GREEN
        page='home'

def auth_login():
    global auth_message,auth_color,player_name,page
    email=auth_login_fields[0][1].strip().lower(); password=auth_login_fields[1][1]
    if not re.fullmatch(r'[a-zA-Z0-9._%+-]+@gmail\.com',email):
        auth_message,auth_color='Enter a valid @gmail.com address.',PINK; return
    record=accounts.get(email)
    if not record: auth_message,auth_color='Account not found. Register first.',PINK; return
    _,digest=auth_hash(password,record['salt'])
    if secrets.compare_digest(digest,record['hash']):
        player_name=record['name']; auth_message,auth_color='Login successful!',GREEN; page='home'
    else: auth_message,auth_color='Incorrect game password.',PINK
# ----------------------------------------------------------

board=[['']*3 for _ in range(3)]; turn='X'; winner=None; win_cells=[]; mode='bot'; page='login'; setting=False; bot_wait=0

def reset():
    global board,turn,winner,win_cells,bot_wait
    
# ---------------- PLAYER LOGIN / REGISTER ----------------
ACCOUNTS=os.path.join(BASE,'cosmic_users.json')
try:
    with open(ACCOUNTS,'r',encoding='utf-8') as f: accounts=json.load(f)
except Exception:
    accounts={}

auth_mode='register'
auth_fields=[['FULL NAME',''],['GMAIL ADDRESS',''],['CREATE GAME PASSWORD',''],['CONFIRM PASSWORD','']]
auth_login_fields=[['GMAIL ADDRESS',''],['GAME PASSWORD','']]
auth_active=0
auth_message='Create your player account'
auth_color=MUTED
player_name=''

def auth_fields_now():
    return auth_fields if auth_mode=='register' else auth_login_fields

def auth_hash(password,salt=None):
    salt=salt or secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),salt.encode('utf-8'),150000).hex()
    return salt,digest

def auth_save():
    with open(ACCOUNTS,'w',encoding='utf-8') as f:
        json.dump(accounts,f,indent=2)

def auth_draw():
    screen.fill(BG)
    for i in range(55):
        pygame.draw.circle(screen,(45,65,115),((i*197+29)%W,(i*113+41)%H),1)
    pw=min(int(W*.90),680); ph=min(int(H*.94),1250)
    panel=pygame.Rect((W-pw)//2,(H-ph)//2,pw,ph)
    pygame.draw.rect(screen,(13,23,58),panel,border_radius=24)
    pygame.draw.rect(screen,BLUE,panel,2,border_radius=24)
    txt('COSMIC TIC-TAC-TOE',max(25,min(38,W//10)),WHITE,(W//2,panel.top+int(ph*.065)),True)
    txt('PLAYER ACCOUNT',18,BLUE,(W//2,panel.top+int(ph*.125)),True)
    txt('CREATE ACCOUNT' if auth_mode=='register' else 'WELCOME BACK',25,WHITE,(W//2,panel.top+int(ph*.19)),True)
    fs=auth_fields_now(); top=panel.top+int(ph*.275)
    gap=int(ph*(.112 if auth_mode=='register' else .17))
    bh=max(48,int(ph*.068)); bw=int(pw*.84); left=(W-bw)//2
    auth_rects=[]
    for i,(label,value) in enumerate(fs):
        yy=top+i*gap
        txt(label,15,MUTED,(left+bw//2,yy-12),True)
        rr=pygame.Rect(left,yy,bw,bh); auth_rects.append(rr)
        pygame.draw.rect(screen,(6,12,37),rr,border_radius=10)
        pygame.draw.rect(screen,BLUE if i==auth_active else (75,95,145),rr,2,border_radius=10)
        shown=('•'*len(value)) if 'PASSWORD' in label else value
        if not shown: shown='Tap here to enter'
        im=fnt(16).render(shown,True,WHITE if value else MUTED)
        screen.blit(im,(rr.x+12,rr.y+(bh-im.get_height())//2))
    by=top+len(fs)*gap+int(ph*.018)
    auth_button=pygame.Rect(left,by,bw,max(52,int(ph*.075)))
    button(auth_button,'CREATE ACCOUNT' if auth_mode=='register' else 'LOGIN',PINK if auth_mode=='register' else BLUE,19)
    switch_y=auth_button.bottom+int(ph*.055)
    switch='Already registered? LOGIN' if auth_mode=='register' else 'New player? CREATE ACCOUNT'
    txt(switch,15,GOLD,(W//2,switch_y),True)
    txt(auth_message,14,auth_color,(W//2,min(panel.bottom-int(ph*.075),switch_y+int(ph*.075))))
    return auth_rects,auth_button,switch_y

def auth_register():
    global auth_message,auth_color,player_name
    name,email,password,confirm=[v.strip() for _,v in auth_fields]
    email=email.lower()
    if not name: auth_message,auth_color='Enter your full name.',PINK
    elif not re.fullmatch(r'[a-zA-Z0-9._%+-]+@gmail\.com',email): auth_message,auth_color='Enter a valid @gmail.com address.',PINK
    elif len(password)<6: auth_message,auth_color='Game password needs at least 6 characters.',PINK
    elif password!=confirm: auth_message,auth_color='Passwords do not match.',PINK
    elif email in accounts: auth_message,auth_color='Account already exists. Please login.',PINK
    else:
        salt,digest=auth_hash(password)
        accounts[email]={'name':name,'salt':salt,'hash':digest}
        auth_save(); player_name=name
        auth_message,auth_color='Account created! Welcome '+name+'!',GREEN
        page='home'

def auth_login():
    global auth_message,auth_color,player_name,page
    email=auth_login_fields[0][1].strip().lower(); password=auth_login_fields[1][1]
    if not re.fullmatch(r'[a-zA-Z0-9._%+-]+@gmail\.com',email):
        auth_message,auth_color='Enter a valid @gmail.com address.',PINK; return
    record=accounts.get(email)
    if not record: auth_message,auth_color='Account not found. Register first.',PINK; return
    _,digest=auth_hash(password,record['salt'])
    if secrets.compare_digest(digest,record['hash']):
        player_name=record['name']; auth_message,auth_color='Login successful!',GREEN; page='home'
    else: auth_message,auth_color='Incorrect game password.',PINK
# ----------------------------------------------------------

board=[['']*3 for _ in range(3)]; turn='X'; winner=None; win_cells=[]; bot_wait=0

def result_check(b):
    lines=[[(r,0),(r,1),(r,2)] for r in range(3)]+[[(0,c),(1,c),(2,c)] for c in range(3)]+[[(0,0),(1,1),(2,2)],[(0,2),(1,1),(2,0)]]
    for line in lines:
        a,b1,c=line
        if b[a[0]][a[1]] and b[a[0]][a[1]]==b[b1[0]][b1[1]]==b[c[0]][c[1]]: return b[a[0]][a[1]],line
    if all(b[r][c] for r in range(3) for c in range(3)): return 'draw',[]
    return None,[]

def reward(outcome):
    if mode=='bot':
        if outcome=='X': data['points']+=100; data['xp']+=50; data['wins']+=1
        elif outcome=='draw': data['points']+=25; data['xp']+=10; data['draws']+=1
        else: data['losses']+=1
    else:
        # In 2-player mode, award the same match reward to the winning side's shared profile.
        if outcome in ('X','O'): data['points']+=100; data['xp']+=50; data['wins']+=1
        else: data['points']+=25; data['xp']+=10; data['draws']+=1
    data['level']=level_from_xp(data['xp']); save()

def finish():
    global winner,win_cells
    winner,win_cells=result_check(board)
    if winner:
        reward(winner); play('win' if winner!='draw' else 'draw')

def minimax(b,maximizing,depth=0):
    out,_=result_check(b)
    if out=='O': return 10-depth
    if out=='X': return depth-10
    if out=='draw': return 0
    vals=[]
    for r in range(3):
        for c in range(3):
            if not b[r][c]:
                b[r][c]='O' if maximizing else 'X'; vals.append(minimax(b,not maximizing,depth+1)); b[r][c]=''
    return max(vals) if maximizing else min(vals)
def bot_move():
    best=-999; choice=None
    for r,c in [(1,1),(0,0),(0,2),(2,0),(2,2),(0,1),(1,0),(1,2),(2,1)]:
        if not board[r][c]:
            board[r][c]='O'; v=minimax(board,False); board[r][c]=''
            if v>best: best=v; choice=(r,c)
    if choice: board[choice[0]][choice[1]]='O'; finish();
    if not winner: globals()['turn']='X'

def background():
    bg,xc,oc=THEMES.get(data['theme'],THEMES['Classic']); screen.fill(bg)
    for _ in range(65):
        x=random.randrange(W); y=random.randrange(H); pygame.draw.circle(screen,(70,100,180),(x,y),1)
    return xc,oc

def header(title,xc): txt(title,max(22,min(34,W//12)),WHITE,(W//2,int(H*.07)),True); pygame.draw.line(screen,xc,(W*.12,H*.12),(W*.88,H*.12),2)

def home(xc,oc):
    header('COSMIC TIC-TAC-TOE',xc)
    txt('PLAY • THINK • WIN',16,MUTED,(W//2,int(H*.16)))
    txt('X  ✦  VS  ✦  O',max(34,W//9),xc,(W//2,int(H*.29)),True)
    txt('POINTS: '+str(data['points']),20,GOLD,(W//2,int(H*.39)),True)
    txt('LEVEL: '+str(data['level'])+' / 50',18,WHITE,(W//2,int(H*.44)))
    txt('XP: '+str(data['xp']%100)+'/100',15,MUTED,(W//2,int(H*.48)))
    bw=min(W*.68,330); bh=max(48,int(H*.075)); x=(W-bw)/2
    button((x,H*.55,bw,bh),'PLAY VS COMPUTER',BLUE,18)
    button((x,H*.64,bw,bh),'2 PLAYER MODE',PINK,18)
    button((x,H*.73,bw,bh),'POINTS SHOP',GOLD,18)
    button((x,H*.82,bw,bh),'SETTINGS',PURPLE,18)

def game_draw(xc,oc):
    header('GALACTIC ARENA',xc)
    txt(('PLAYER X' if turn=='X' else ('COMPUTER' if mode=='bot' else 'PLAYER O'))+' TURN',18,xc if turn=='X' else oc,(W//2,H*.17),True)
    size=min(W*.78,H*.47); left=(W-size)/2; top=H*.25; cell=size/3
    pygame.draw.rect(screen,(8,18,52),(left,top,size,size),border_radius=14); pygame.draw.rect(screen,xc,(left,top,size,size),3,border_radius=14)
    for i in (1,2):
        pygame.draw.line(screen,(35,100,170),(left+i*cell,top),(left+i*cell,top+size),3); pygame.draw.line(screen,(35,100,170),(left,top+i*cell),(left+size,top+i*cell),3)
    for r in range(3):
        for c in range(3):
            sym=board[r][c]
            if sym:
                color=(GOLD if data['symbol']=='Gold X/O' else (xc if sym=='X' else oc)); cx=left+(c+.5)*cell; cy=top+(r+.5)*cell; d=cell*.27
                if sym=='X': pygame.draw.line(screen,color,(cx-d,cy-d),(cx+d,cy+d),max(5,int(cell*.07))); pygame.draw.line(screen,color,(cx+d,cy-d),(cx-d,cy+d),max(5,int(cell*.07)))
                else: pygame.draw.circle(screen,color,(int(cx),int(cy)),int(d),max(5,int(cell*.07)))
    if winner:
        msg='DRAW!' if winner=='draw' else ('PLAYER X WINS!' if winner=='X' else ('COMPUTER WINS!' if mode=='bot' else 'PLAYER O WINS!'))
        txt(msg,25,GOLD,(W//2,H*.77),True); txt('Points: '+str(data['points'])+'   Level: '+str(data['level']),17,WHITE,(W//2,H*.82))
    button((W*.08,H*.88,W*.38,max(42,H*.07)),'HOME',PURPLE,17)
    button((W*.54,H*.88,W*.38,max(42,H*.07)),'RESTART',BLUE,17)

def shop_draw(xc,oc):
    header('POINTS SHOP',GOLD); txt('YOUR POINTS: '+str(data['points']),20,GOLD,(W//2,H*.17),True)
    y=H*.25; bh=max(44,int(H*.09))
    for name,cost in ITEMS:
        owned=name in data['owned']; label=name+('  OWNED' if owned else '  '+str(cost)+' PTS')
        button((W*.12,y,W*.76,bh),label,GREEN if owned else GOLD,16); y+=bh+10
    button((W*.25,H*.87,W*.5,max(42,H*.07)),'BACK',PURPLE,18)

def settings_draw(xc,oc):
    header('SETTINGS',PURPLE)
    txt('VOLUME: '+str(data['volume'])+'%',20,WHITE,(W//2,H*.25),True)
    bar=pygame.Rect(W*.15,H*.32,W*.70,18); pygame.draw.rect(screen,(35,50,90),bar,border_radius=9); pygame.draw.rect(screen,GREEN,(bar.x,bar.y,bar.w*data['volume']/100,bar.h),border_radius=9)
    txt('Tap the bar to set volume (0 = mute, 100 = max)',13,MUTED,(W//2,H*.38))
    button((W*.2,H*.48,W*.6,max(45,H*.08)),'THEME: '+data['theme'],BLUE,17)
    txt('All 7 cosmic sound effects are controlled by volume.',14,MUTED,(W//2,H*.64))
    button((W*.25,H*.83,W*.5,max(42,H*.07)),'BACK',PURPLE,18)

running=True
while running:
    clock.tick(60); xc,oc=background()
    if page=='login': auth_rects,auth_button,auth_switch_y=auth_draw()
    elif page=='home': home(xc,oc)
    elif page=='game': game_draw(xc,oc)
    elif page=='shop': shop_draw(xc,oc)
    elif page=='settings': settings_draw(xc,oc)
    pygame.display.flip()
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        elif e.type==pygame.KEYDOWN:
            if page=='login':
                fs=auth_fields_now()
                if e.key==pygame.K_ESCAPE: running=False
                elif e.key==pygame.K_TAB: auth_active=(auth_active+1)%len(fs)
                elif e.key==pygame.K_BACKSPACE: fs[auth_active][1]=fs[auth_active][1][:-1]
                elif e.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
                    auth_register() if auth_mode=='register' else auth_login()
                elif e.unicode and e.unicode.isprintable() and len(fs[auth_active][1])<64:
                    fs[auth_active][1]+=e.unicode
            elif e.key in (pygame.K_ESCAPE,pygame.K_BACK):
                if page!='home': page='home'
                else: running=False
        elif e.type in (pygame.MOUSEBUTTONDOWN,pygame.FINGERDOWN):
            if e.type==pygame.FINGERDOWN: pos=(int(e.x*W),int(e.y*H))
            else: pos=e.pos
            x,y=pos; play('tap')
            if page=='login':
                fs=auth_fields_now()
                # Recompute field geometry exactly as drawn.
                pw=min(int(W*.90),680); ph=min(int(H*.94),1250)
                panel=pygame.Rect((W-pw)//2,(H-ph)//2,pw,ph)
                top=panel.top+int(ph*.275); gap=int(ph*(.112 if auth_mode=='register' else .17))
                bh=max(48,int(ph*.068)); bw=int(pw*.84); left=(W-bw)//2
                for i in range(len(fs)):
                    rr=pygame.Rect(left,top+i*gap,bw,bh)
                    if rr.collidepoint(pos): auth_active=i
                by=top+len(fs)*gap+int(ph*.018)
                btn=pygame.Rect(left,by,bw,max(52,int(ph*.075)))
                switch_y=btn.bottom+int(ph*.055)
                if btn.collidepoint(pos):
                    auth_register() if auth_mode=='register' else auth_login()
                elif abs(y-switch_y)<28:
                    auth_mode='login' if auth_mode=='register' else 'register'
                    auth_active=0; auth_message='Enter your account details'; auth_color=MUTED
            elif page=='home':
                if H*.55<y<H*.55+max(48,H*.075): mode='bot'; reset(); page='game'
                elif H*.64<y<H*.64+max(48,H*.075): mode='two'; reset(); page='game'
                elif H*.73<y<H*.73+max(48,H*.075): page='shop'
                elif H*.82<y<H*.82+max(48,H*.075): page='settings'
            elif page=='game':
                if y>H*.87:
                    if x<W*.5: page='home'
                    else: reset()
                elif not winner:
                    size=min(W*.78,H*.47); left=(W-size)/2; top=H*.25; cell=size/3
                    if left<=x<=left+size and top<=y<=top+size:
                        c=int((x-left)//cell); r=int((y-top)//cell)
                        if not board[r][c]:
                            board[r][c]=turn; play('crystal'); finish()
                            if not winner:
                                turn='O' if turn=='X' else 'X'
                                if mode=='bot' and turn=='O': bot_move()
            elif page=='shop':
                y0=H*.25; bh=max(44,int(H*.09))
                for i,(name,cost) in enumerate(ITEMS):
                    yy=y0+i*(bh+10)
                    if yy<=y<=yy+bh:
                        if name not in data['owned'] and data['points']>=cost:
                            data['points']-=cost; data['owned'].append(name); save(); play('win')
                        elif name in data['owned']:
                            if name in THEMES: data['theme']=name
                            else: data['symbol']=name
                            save()
                if y>H*.86: page='home'
            elif page=='settings':
                if H*.29<y<H*.37:
                    data['volume']=max(0,min(100,int((x-W*.15)/(W*.70)*100))); save()
                elif H*.48<y<H*.57:
                    names=[n for n in THEMES if n in data['owned']]; idx=(names.index(data['theme'])+1)%len(names); data['theme']=names[idx]; save()
                elif y>H*.82: page='home'

pygame.quit(); sys.exit()

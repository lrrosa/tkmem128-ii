# -*- coding: utf-8 -*-
"""Roteador de labirinto (A*) de duas camadas com via, para fechar uma net.

Usado quando o autorouter deixa uma ligacao em aberto e nao ha caminho simples
em L ou Z. Rasteriza tudo que ja existe na placa numa grade e busca o caminho
mais curto do pad isolado ate qualquer cobre da ilha principal da mesma net.

  "C:/Program Files/KiCad/10.0/bin/python.exe" maze.py <modulo> <net> <x> <y>
"""
import heapq, importlib, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

BOARD = importlib.import_module(sys.argv[1])
NET = sys.argv[2]
ALVO = (float(sys.argv[3]), float(sys.argv[4]))    # pad isolado
REAL = "%s/%s.kicad_pcb" % (BOARD.PROJ_DIR, BOARD.PROJ_NAME)

STEP = 0.05
MARGEM = 0.12          # compensa a discretizacao da grade
W, CLEAR = 0.25, 0.15
VIA_D, VIA_CLEAR = 0.7, 0.15
EDGE = 0.3
BW, BH = BOARD.BOARD_W, BOARD.BOARD_H
NX, NY = int(BW / STEP) + 1, int(BH / STEP) + 1
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)


def tm(v):
    return pcbnew.ToMM(v)


b = pcbnew.LoadBoard(REAL)
code = b.GetNetcodeFromNetname(NET)

blocked = [bytearray(NX * NY) for _ in LAYERS]
bloq_via = [bytearray(NX * NY) for _ in LAYERS]
goal = [bytearray(NX * NY) for _ in LAYERS]


def idx(ix, iy):
    return iy * NX + ix


def disco(grid, cx, cy, r):
    ri = int(r / STEP) + 1
    ix0, iy0 = int(cx / STEP), int(cy / STEP)
    for dy in range(-ri, ri + 1):
        iy = iy0 + dy
        if iy < 0 or iy >= NY:
            continue
        for dx in range(-ri, ri + 1):
            ix = ix0 + dx
            if ix < 0 or ix >= NX:
                continue
            if (dx * dx + dy * dy) * STEP * STEP <= r * r:
                grid[idx(ix, iy)] = 1


def linha(grid, x1, y1, x2, y2, r):
    n = max(2, int(math.hypot(x2 - x1, y2 - y1) / (STEP * 0.7)) + 1)
    for i in range(n + 1):
        t = i / float(n)
        disco(grid, x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, r)


def retangulo(grid, x1, y1, x2, y2, folga):
    for iy in range(max(0, int((y1 - folga) / STEP)),
                    min(NY, int((y2 + folga) / STEP) + 1)):
        for ix in range(max(0, int((x1 - folga) / STEP)),
                        min(NX, int((x2 + folga) / STEP) + 1)):
            grid[idx(ix, iy)] = 1


# ---- ilhas da net: o destino e a ilha principal, nao qualquer cobre ---------
pai = {}


def acha(a):
    while pai[a] != a:
        pai[a] = pai[pai[a]]
        a = pai[a]
    return a


def une(a, c):
    pai.setdefault(a, a)
    pai.setdefault(c, c)
    ra, rc = acha(a), acha(c)
    if ra != rc:
        pai[ra] = rc


def ch(x, y, ly):
    return (round(x, 2), round(y, 2), ly)


itens = []   # (tipo, dados, camadas, chaves)
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetCode() != code:
            continue
        pos = p.GetPosition()
        lys = [li for li, ly in enumerate(LAYERS) if p.IsOnLayer(ly)]
        ks = [ch(tm(pos.x), tm(pos.y), li) for li in lys]
        for k in ks:
            pai.setdefault(k, k)
        for k in ks[1:]:
            une(ks[0], k)
        bb = p.GetBoundingBox()
        itens.append(("pad", (tm(bb.GetLeft()), tm(bb.GetTop()),
                              tm(bb.GetRight()), tm(bb.GetBottom())), lys, ks))
for t in b.GetTracks():
    if t.GetNetCode() != code:
        continue
    if t.GetClass() == "PCB_VIA":
        pos = t.GetPosition()
        ks = [ch(tm(pos.x), tm(pos.y), li) for li in range(2)]
        for k in ks:
            pai.setdefault(k, k)
        une(ks[0], ks[1])
        itens.append(("via", (tm(pos.x), tm(pos.y), 0.35), [0, 1], ks))
    else:
        s_, e_ = t.GetStart(), t.GetEnd()
        li = LAYERS.index(t.GetLayer()) if t.GetLayer() in LAYERS else None
        if li is None:
            continue
        a = ch(tm(s_.x), tm(s_.y), li)
        c = ch(tm(e_.x), tm(e_.y), li)
        une(a, c)
        itens.append(("seg", (tm(s_.x), tm(s_.y), tm(e_.x), tm(e_.y),
                              tm(t.GetWidth()) / 2.0), [li], [a, c]))

grupos = {}
for it in itens:
    r = acha(it[3][0])
    grupos.setdefault(r, []).append(it)
alvo_raiz = acha(ch(ALVO[0], ALVO[1], 0))
principal = max((g for r, g in grupos.items() if r != alvo_raiz),
                key=len, default=None)
print("ilhas da net %s: %d   principal com %d itens"
      % (NET, len(grupos), len(principal) if principal else 0))
if not principal:
    raise SystemExit("nao ha outra ilha para alcancar")

for tipo, dados, lys, _ in principal:
    for li in lys:
        if tipo == "pad":
            retangulo(goal[li], dados[0], dados[1], dados[2], dados[3], 0.0)
        elif tipo == "via":
            disco(goal[li], dados[0], dados[1], dados[2])
        else:
            linha(goal[li], dados[0], dados[1], dados[2], dados[3], dados[4])

# ---- obstaculos -------------------------------------------------------------
meia = W / 2.0
for fp in b.GetFootprints():
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        r = (tm(bb.GetLeft()), tm(bb.GetTop()), tm(bb.GetRight()),
             tm(bb.GetBottom()))
        if p.GetNetCode() == code:
            continue
        for li, ly in enumerate(LAYERS):
            if p.IsOnLayer(ly):
                retangulo(blocked[li], r[0], r[1], r[2], r[3],
                          CLEAR + meia + MARGEM)
                retangulo(bloq_via[li], r[0], r[1], r[2], r[3],
                          CLEAR + VIA_D / 2.0 + MARGEM)

for t in b.GetTracks():
    if t.GetNetCode() == code:
        continue
    if t.GetClass() == "PCB_VIA":
        pos = t.GetPosition()
        for li in range(2):
            disco(blocked[li], tm(pos.x), tm(pos.y),
                  0.35 + CLEAR + meia + MARGEM)
            disco(bloq_via[li], tm(pos.x), tm(pos.y),
                  0.35 + CLEAR + VIA_D / 2.0 + MARGEM)
        continue
    s, e = t.GetStart(), t.GetEnd()
    hw = tm(t.GetWidth()) / 2.0
    li = LAYERS.index(t.GetLayer()) if t.GetLayer() in LAYERS else None
    if li is None:
        continue
    linha(blocked[li], tm(s.x), tm(s.y), tm(e.x), tm(e.y),
          hw + CLEAR + meia + MARGEM)
    linha(bloq_via[li], tm(s.x), tm(s.y), tm(e.x), tm(e.y),
          hw + CLEAR + VIA_D / 2.0 + MARGEM)

# borda da placa
for li in range(2):
    g = blocked[li]
    lim = EDGE + meia
    for iy in range(NY):
        for ix in range(NX):
            x, y = ix * STEP, iy * STEP
            if x < lim or y < lim or x > BW - lim or y > BH - lim:
                g[idx(ix, iy)] = 1

# o pad isolado e sua vizinhanca imediata nao contam como destino
def limpa(grid, cx, cy, r):
    ri = int(r / STEP) + 1
    ix0, iy0 = int(cx / STEP), int(cy / STEP)
    for dy in range(-ri, ri + 1):
        iy = iy0 + dy
        if iy < 0 or iy >= NY:
            continue
        for dx in range(-ri, ri + 1):
            ix = ix0 + dx
            if 0 <= ix < NX and (dx * dx + dy * dy) * STEP * STEP <= r * r:
                grid[idx(ix, iy)] = 0




# o pad isolado nao pode ser obstaculo de si mesmo
ini_ix, ini_iy = int(ALVO[0] / STEP), int(ALVO[1] / STEP)
for li in range(2):
    disco(blocked[li], ALVO[0], ALVO[1], 0.0)
    blocked[li][idx(ini_ix, ini_iy)] = 0

alvos = sum(sum(g) for g in goal)
print("grade %dx%d  celulas-alvo: %d" % (NX, NY, alvos))
if alvos == 0:
    raise SystemExit("ilha principal nao rasterizada")

# ---- A* --------------------------------------------------------------------
INF = float("inf")
dist = {}
start = (ini_ix, ini_iy, 0)
start2 = (ini_ix, ini_iy, 1)
pq = [(0.0, start, None), (0.0, start2, None)]
prev = {}
achou = None
VIA_COST = 3.0
viz = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

while pq:
    d, cur, par = heapq.heappop(pq)
    if cur in dist:
        continue
    dist[cur] = d
    prev[cur] = par
    ix, iy, li = cur
    if goal[li][idx(ix, iy)]:
        achou = cur
        break
    for dx, dy in viz:
        nx_, ny_ = ix + dx, iy + dy
        if nx_ < 0 or ny_ < 0 or nx_ >= NX or ny_ >= NY:
            continue
        if blocked[li][idx(nx_, ny_)]:
            continue
        nd = d + STEP * (1.4142 if dx and dy else 1.0)
        n = (nx_, ny_, li)
        if n not in dist:
            heapq.heappush(pq, (nd, n, cur))
    ol = 1 - li
    if not (bloq_via[0][idx(ix, iy)] or bloq_via[1][idx(ix, iy)]):
        n = (ix, iy, ol)
        if n not in dist:
            heapq.heappush(pq, (d + VIA_COST, n, cur))

if achou is None:
    raise SystemExit("sem caminho")

caminho = []
c = achou
while c is not None:
    caminho.append(c)
    c = prev[c]
caminho.reverse()
print("caminho com %d celulas, %.2f mm" % (len(caminho), dist[achou]))

# ---- simplifica e escreve --------------------------------------------------
pontos = []
for (ix, iy, li) in caminho:
    pontos.append((round(ix * STEP, 3), round(iy * STEP, 3), li))

simples = [pontos[0]]
for i in range(1, len(pontos) - 1):
    ax, ay, al = simples[-1]
    bx, by, bl = pontos[i]
    cx, cy, cl = pontos[i + 1]
    if al != bl or bl != cl:
        simples.append(pontos[i])
        continue
    if (bx - ax) * (cy - by) != (by - ay) * (cx - bx):
        simples.append(pontos[i])
simples.append(pontos[-1])
print("simplificado para %d vertices" % len(simples))

nvias = 0
for i in range(len(simples) - 1):
    x1, y1, l1 = simples[i]
    x2, y2, l2 = simples[i + 1]
    if l1 != l2:
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        v.SetWidth(pcbnew.FromMM(VIA_D))
        v.SetDrill(pcbnew.FromMM(0.35))
        v.SetNetCode(code)
        b.Add(v)
        nvias += 1
        continue
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    t.SetWidth(pcbnew.FromMM(W))
    t.SetLayer(LAYERS[l1])
    t.SetNetCode(code)
    b.Add(t)

# encosta no centro do pad
x0, y0, l0 = simples[0]
t = pcbnew.PCB_TRACK(b)
t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(ALVO[0]), pcbnew.FromMM(ALVO[1])))
t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x0), pcbnew.FromMM(y0)))
t.SetWidth(pcbnew.FromMM(W))
t.SetLayer(LAYERS[l0])
t.SetNetCode(code)
b.Add(t)

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(REAL, b)
print("gravado: %d vias" % nvias)

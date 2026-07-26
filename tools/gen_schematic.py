# -*- coding: utf-8 -*-
"""Gera tkmem128.kicad_sch (estilo netlist: cada pino recebe rotulo global)."""
import io, os, re, sys, uuid as _uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
BOARD = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "netlist")
PARTS, CONN = BOARD.PARTS, BOARD.CONN

PROJ = BOARD.PROJ_DIR
KILIB = "C:/Program Files/KiCad/10.0/share/kicad/symbols"
LOCAL = ("F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware/lib/tkmem128.kicad_sym")
ROOT_UUID = None  # definido em main()
PROJECT_NAME = BOARD.PROJ_NAME

SHEET_W, SHEET_H = 594.0, 420.0
STUB = 3.81


def uid():
    return str(_uuid.uuid4())


GRID = 1.27


def q(v):
    """Arredonda para 2 casas: todas as coordenadas vivem na grade de 1,27."""
    return round(float(v) + 0.0, 2)


def snap(v):
    return round(round(float(v) / GRID) * GRID, 2)


# --------------------------------------------------------------- s-expr utils
def block(text, start_tag, from_idx=0):
    i = text.find(start_tag, from_idx)
    if i < 0:
        return None, -1
    depth = 0
    for j in range(i, len(text)):
        if text[j] == '(':
            depth += 1
        elif text[j] == ')':
            depth -= 1
            if depth == 0:
                return text[i:j + 1], j + 1
    return None, -1


_libcache = {}


def libtext(lib):
    if lib not in _libcache:
        path = LOCAL if lib == "tkmem128" else "%s/%s.kicad_sym" % (KILIB, lib)
        _libcache[lib] = io.open(path, encoding="utf-8").read()
    return _libcache[lib]


def raw_symbol(lib, name):
    seg, _ = block(libtext(lib), '(symbol "%s"' % name)
    if seg is None:
        raise KeyError("simbolo %s:%s nao encontrado" % (lib, name))
    return seg


def subsymbols(seg, name):
    """Retorna os blocos (symbol "NAME_u_v" ...) internos."""
    out, idx = [], 0
    while True:
        sub, nxt = block(seg, '(symbol "%s_' % name, idx)
        if sub is None:
            break
        out.append(sub)
        idx = nxt
    return out


def load_symbol(lib, name):
    """Devolve o corpo do simbolo ja achatado (sem 'extends')."""
    seg = raw_symbol(lib, name)
    m = re.search(r'\(extends "([^"]+)"\s*\)', seg)
    if m:
        parent = m.group(1)
        pseg = load_symbol(lib, parent)
        subs = [s.replace('"%s_' % parent, '"%s_' % name, 1)
                for s in subsymbols(pseg, parent)]
        seg = seg.replace(m.group(0), "")
        seg = seg[:seg.rfind(')')] + "\n" + "\n".join(subs) + "\n\t)"
    return seg


def pins_of(seg, name):
    """[(numero, nome, x, y, rot)] do simbolo achatado."""
    out = []
    for sub in subsymbols(seg, name):
        idx = 0
        while True:
            pin, nxt = block(sub, '(pin ', idx)
            if pin is None:
                break
            idx = nxt
            at = re.search(r'\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', pin)
            num = re.search(r'\(number "([^"]*)"', pin)
            pname = re.search(r'\(name "([^"]*)"', pin)
            if at and num:
                out.append((num.group(1), pname.group(1) if pname else "",
                            float(at.group(1)), float(at.group(2)),
                            float(at.group(3))))
    return out


# ------------------------------------------------------------------ emissao
def prop(name, value, x, y, hide=False, rot=0, size=1.27, just=None):
    eff = "(font (size %s %s))" % (size, size)
    if just:
        eff = "(font (size %s %s)) (justify %s)" % (size, size, just)
    if hide:
        eff += " (hide yes)"
    return ('\t\t(property "%s" "%s"\n\t\t\t(at %s %s %s)\n'
            '\t\t\t(effects %s)\n\t\t)\n' % (name, value, x, y, rot, eff))


def wire(x1, y1, x2, y2):
    return ('\t(wire\n\t\t(pts (xy %s %s) (xy %s %s))\n'
            '\t\t(stroke (width 0) (type default))\n\t\t(uuid "%s")\n\t)\n'
            % (q(x1), q(y1), q(x2), q(y2), uid()))


def glabel(net, x, y, rot):
    just = "left" if rot == 0 else ("right" if rot == 180 else "left")
    return ('\t(global_label "%s"\n\t\t(shape bidirectional)\n'
            '\t\t(at %s %s %s)\n\t\t(fields_autoplaced yes)\n'
            '\t\t(effects (font (size 1.27 1.27)) (justify %s))\n'
            '\t\t(uuid "%s")\n\t)\n' % (net, q(x), q(y), rot, just, uid()))


# ------------------------------------------------------------- posicionamento
PLACE = BOARD.PLACE_SCH
DISC_ORIGIN = BOARD.SCH_DISC_ORIGIN
DISC_STEP = 22


def main():
    global ROOT_UUID
    import hashlib
    h = hashlib.md5(BOARD.PROJ_NAME.encode()).hexdigest()
    ROOT_UUID = "%s-%s-%s-%s-%s" % (h[:8], h[8:12], h[12:16], h[16:20], h[20:32])

    used = {}          # lib_id -> corpo achatado
    placed = []        # (ref, lib_id, val, fp, descr, x, y)

    dx, dy = DISC_ORIGIN
    n = 0
    for ref, lib_id, val, fp, descr in PARTS:
        lib, name = lib_id.split(":")
        if lib_id not in used:
            used[lib_id] = load_symbol(lib, name)
        if ref in PLACE:
            x, y = PLACE[ref]
        else:
            x, y = dx, dy + DISC_STEP * n
            n += 1
        x, y = snap(x), snap(y)
        placed.append((ref, lib_id, val, fp, descr, x, y))

    # simbolos de alimentacao + PWR_FLAG
    for lib_id in ("power:+5V", "power:GND", "power:PWR_FLAG"):
        lib, name = lib_id.split(":")
        used[lib_id] = load_symbol(lib, name)

    out = []
    out.append('(kicad_sch\n\t(version 20250114)\n\t(generator "tkmem128-gen")\n'
               '\t(generator_version "10.0")\n\t(uuid "%s")\n\t(paper "A2")\n'
               % ROOT_UUID)
    out.append('\t(title_block\n\t\t(title "TKMEM-128 KiCad - expansao de '
               '128K para TK90X/TK95")\n\t\t(rev "1.0")\n'
               '\t\t(company "Derivado de Velesoft (2009) e Luccas Eletronica '
               '(2012) - CERN-OHL-S v2")\n\t)\n')

    # ------------------------------------------------------------ lib_symbols
    out.append('\t(lib_symbols\n')
    for lib_id, body in used.items():
        lib, name = lib_id.split(":")
        renamed = body.replace('(symbol "%s"' % name, '(symbol "%s"' % lib_id, 1)
        out.append("\t" + renamed.replace("\n", "\n\t") + "\n")
    out.append('\t)\n')

    # -------------------------------------------------------------- simbolos
    for ref, lib_id, val, fp, descr, x, y in placed:
        lib, name = lib_id.split(":")
        pl = pins_of(used[lib_id], name)
        out.append('\t(symbol\n\t\t(lib_id "%s")\n\t\t(at %s %s 0)\n'
                   '\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n'
                   '\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "%s")\n'
                   % (lib_id, q(x), q(y), uid()))
        ys = q(min([y - p[3] for p in pl]) if pl else y)
        out.append(prop("Reference", ref, x, q(ys - 5.08), just="left"))
        out.append(prop("Value", val, x, q(ys - 2.54), just="left"))
        out.append(prop("Footprint", fp, x, y, hide=True))
        out.append(prop("Datasheet", "", x, y, hide=True))
        out.append(prop("Description", descr, x, y, hide=True))
        for num, _pn, px, py, rot in pl:
            out.append('\t\t(pin "%s" (uuid "%s"))\n' % (num, uid()))
        out.append('\t\t(instances\n\t\t\t(project "%s"\n'
                   '\t\t\t\t(path "/%s"\n\t\t\t\t\t(reference "%s") (unit 1)\n'
                   '\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
                   % (PROJECT_NAME, ROOT_UUID, ref))

        # stubs + rotulos
        for num, _pn, px, py, rot in pl:
            net = CONN.get(ref, {}).get(num)
            if net is None:
                continue
            ax, ay = q(x + px), q(y - py)
            if rot == 0:
                bx, by, lrot = q(ax - STUB), ay, 180
            elif rot == 180:
                bx, by, lrot = q(ax + STUB), ay, 0
            elif rot == 90:
                bx, by, lrot = ax, q(ay + STUB), 270
            else:
                bx, by, lrot = ax, q(ay - STUB), 90
            out.append(wire(ax, ay, bx, by))
            out.append(glabel(net, bx, by, lrot))

    # ------------------------------------------- power flags (+5V / GND) ERC
    for idx, (lib_id, net, px) in enumerate((("power:+5V", "+5V", snap(470.0)),
                                            ("power:GND", "GND", snap(490.0))), 1):
        lib, name = lib_id.split(":")
        pl = pins_of(used[lib_id], name)
        py = snap(380.0)
        out.append('\t(symbol\n\t\t(lib_id "%s")\n\t\t(at %s %s 0)\n'
                   '\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n'
                   '\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "%s")\n'
                   % (lib_id, q(px), q(py), uid()))
        out.append(prop("Reference", "#PWR%02d" % idx,
                        px, py, hide=True))
        out.append(prop("Value", net, px, py - 6, hide=True))
        out.append(prop("Footprint", "", px, py, hide=True))
        out.append(prop("Datasheet", "", px, py, hide=True))
        out.append(prop("Description", "", px, py, hide=True))
        out.append('\t\t(instances\n\t\t\t(project "%s"\n'
                   '\t\t\t\t(path "/%s"\n\t\t\t\t\t(reference "#PWR%02d") '
                   '(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
                   % (PROJECT_NAME, ROOT_UUID, idx))
        # PWR_FLAG no mesmo ponto
        fl = pins_of(used["power:PWR_FLAG"], "PWR_FLAG")
        fx, fy = px, q(py - 12.7)
        out.append('\t(symbol\n\t\t(lib_id "power:PWR_FLAG")\n\t\t(at %s %s 0)\n'
                   '\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n'
                   '\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "%s")\n'
                   % (q(fx), q(fy), uid()))
        out.append(prop("Reference", "#FLG%02d" % idx,
                        fx, fy, hide=True))
        out.append(prop("Value", "PWR_FLAG", fx, fy, hide=True))
        out.append(prop("Footprint", "", fx, fy, hide=True))
        out.append(prop("Datasheet", "", fx, fy, hide=True))
        out.append(prop("Description", "", fx, fy, hide=True))
        out.append('\t\t(instances\n\t\t\t(project "%s"\n'
                   '\t\t\t\t(path "/%s"\n\t\t\t\t\t(reference "#FLG%02d") '
                   '(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
                   % (PROJECT_NAME, ROOT_UUID, idx))
        for num, _pn, ppx, ppy, rot in pl + fl:
            pass
        # rotulo ligando os dois ao net
        pax, pay = q(px + pl[0][2]), q(py - pl[0][3])
        fax, fay = q(fx + fl[0][2]), q(fy - fl[0][3])
        out.append(wire(pax, pay, pax, q(pay + 6.35)))
        out.append(glabel(net, pax, q(pay + 6.35), 0))
        out.append(wire(fax, fay, fax, q(fay + 6.35)))
        out.append(glabel(net, fax, q(fay + 6.35), 0))

    out.append('\t(sheet_instances\n\t\t(path "/" (page "1"))\n\t)\n)\n')

    path = PROJ + "/" + BOARD.PROJ_NAME + ".kicad_sch"
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(out))
    print("escrito:", path)
    print("simbolos colocados:", len(placed))


if __name__ == "__main__":
    main()

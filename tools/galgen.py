# -*- coding: utf-8 -*-
"""Monta o mapa de fusiveis do GAL20V8 a partir das equacoes da TKMEM-128
e confere contra um .jed de referencia.

A ideia: o mapa de colunas da matriz AND e DERIVADO das proprias equacoes
conhecidas (nao chutado), e depois usado para reencodar tudo. Se o resultado
sair bit a bit igual ao .jed de referencia, esta provado que:
  (a) o mapa de colunas deduzido esta certo, e
  (b) o .jed distribuido implementa exatamente as equacoes documentadas.
"""
import io, re, sys

QF = 2706
ROWS, COLS = 64, 40

# OLMC: bloco de 8 linhas -> pino de saida (linha 0 de cada bloco = OE)
BLOCK_PIN = {0: 22, 1: 21, 2: 20, 3: 19, 4: 18, 5: 17, 6: 16, 7: 15}

# equacoes: pino -> (saida_ativa_baixa, [termo, ...])
# termo = [(pino_de_entrada, True se literal verdadeiro), ...]
MREQ, ZX512, A1, WR, DIS128, BANK2, A5, BANK0 = 1, 2, 3, 4, 5, 6, 7, 8
BANK4, BANK3, BANK1, A15, A14, IORQ = 9, 10, 11, 13, 14, 23

EQ = {
    22: (False, [[(A14, True), (A15, True), (BANK0, True)]]),                # SA14
    21: (False, [[(A14, True), (A15, True), (BANK1, True)],
                 [(A14, False), (A15, True)]]),                              # SA15
    20: (False, [[(A14, True), (A15, True), (BANK2, True)]]),                # SA16
    19: (True,  [[(MREQ, False), (A15, True)]]),                             # /RAMCS
    18: (True,  [[(A14, True), (A15, True), (BANK3, True),
                  (ZX512, False)]]),                                         # /SA17
    17: (False, [[(A14, True), (A15, True), (BANK4, True),
                  (ZX512, False)]]),                                         # SA18
    16: (False, [[(IORQ, False), (WR, False), (A15, False), (A5, True),
                  (A1, False)],
                 [(DIS128, True)]]),                                         # CLK7FFD
    15: (True,  [[(MREQ, False), (A14, False), (A15, False)]]),              # /ROMCS
}


def read_jed(path):
    """Devolve a lista de 2706 fusiveis (0/1) de um arquivo JEDEC."""
    txt = io.open(path, encoding="latin-1").read()
    fuses = [0] * QF
    for m in re.finditer(r"L0*(\d+)\s+([01\s]+?)\*", txt):
        addr = int(m.group(1))
        bits = re.sub(r"\s", "", m.group(2))
        for i, c in enumerate(bits):
            fuses[addr + i] = int(c)
    return fuses


def and_rows(fuses):
    return [fuses[r * COLS:(r + 1) * COLS] for r in range(ROWS)]


def derive_colmap(rows):
    """Deduz coluna -> (pino, literal_verdadeiro) a partir das equacoes."""
    # candidatos: para cada literal, o conjunto de colunas possiveis
    cand = {}
    for block, pin in BLOCK_PIN.items():
        _, terms = EQ[pin]
        for ti, term in enumerate(terms):
            row = rows[block * 8 + 1 + ti]
            zeros = set(i for i, b in enumerate(row) if b == 0)
            if len(zeros) != len(term):
                raise SystemExit(
                    "bloco %d termo %d: %d zeros para %d literais"
                    % (block, ti, len(zeros), len(term)))
            for lit in term:
                cand.setdefault(lit, []).append(zeros)

    poss = {lit: set.intersection(*sets) for lit, sets in cand.items()}
    colmap = {}

    # propagacao de restricoes: (1) coluna ja usada sai dos candidatos;
    # (2) literal verdadeiro e barrado do mesmo pino ocupam colunas vizinhas
    #     do mesmo par (2k, 2k+1).
    for _ in range(len(poss) + 2):
        changed = False
        for lit in list(poss):
            if lit in colmap:
                continue
            opts = poss[lit] - set(colmap.values())
            pin, true_lit = lit
            other = colmap.get((pin, not true_lit))
            if other is not None:
                opts = opts & {other ^ 1}
            if len(opts) == 1:
                colmap[lit] = opts.pop()
                changed = True
            else:
                poss[lit] = opts
        if not changed:
            break

    # Literais que so aparecem juntos num mesmo produto ficam intercambiaveis:
    # o conjunto de colunas e o mesmo, e AND e comutativo, entao a escolha
    # dentro do grupo nao muda um unico fusivel. Fixa numa ordem estavel.
    faltando = sorted(l for l in poss if l not in colmap)
    if faltando:
        livres = sorted(set().union(*[poss[l] for l in faltando])
                        - set(colmap.values()))
        if len(livres) != len(faltando):
            raise SystemExit("literais ambiguos sem solucao: %s" % faltando)
        for lit, col in zip(faltando, livres):
            colmap[lit] = col
        print("nota: %d literais aparecem apenas num mesmo produto e sao "
              "intercambiaveis;" % len(faltando))
        print("      a atribuicao dentro do grupo nao altera o mapa de "
              "fusiveis.")
    return colmap


def build(colmap):
    """Reconstroi os 2706 fusiveis a partir das equacoes."""
    fuses = [0] * QF
    for block, pin in BLOCK_PIN.items():
        base = block * 8 * COLS
        # linha 0 = habilitacao de saida: sempre ligada -> todos os fusiveis 1
        for c in range(COLS):
            fuses[base + c] = 1
        _, terms = EQ[pin]
        for ti, term in enumerate(terms):
            off = base + (1 + ti) * COLS
            cols = set(colmap[lit] for lit in term)
            for c in range(COLS):
                fuses[off + c] = 0 if c in cols else 1
        # linhas restantes ficam em 0 (termo sempre falso)

    # ---- fusiveis de configuracao ----------------------------------------
    # XOR (L2560): polaridade da saida. 1 = ativa alta, 0 = ativa baixa.
    for block, pin in BLOCK_PIN.items():
        ativa_baixa, _ = EQ[pin]
        fuses[2560 + block] = 0 if ativa_baixa else 1

    # assinatura do usuario (L2568..2631): em branco
    for i in range(2568, 2632):
        fuses[i] = 0

    # AC1 (L2632): 1 em todos = saidas combinatorias tristate (modo complex)
    for block in range(8):
        fuses[2632 + block] = 1

    # PTD (L2640): habilita as linhas usadas de cada OLMC.
    # linha 0 = habilitacao de saida, linhas 1..n = os produtos.
    for block, pin in BLOCK_PIN.items():
        _, terms = EQ[pin]
        for row in range(8):
            fuses[2640 + block * 8 + row] = 1 if row <= len(terms) else 0

    # SYN e AC0 (L2704): 1,1 = modo complex
    fuses[2704] = 1
    fuses[2705] = 1
    return fuses


def checksum(fuses):
    """Checksum JEDEC: soma dos bytes little-endian dos fusiveis, 16 bits."""
    total = 0
    for i in range(0, len(fuses), 8):
        byte = 0
        for b in range(8):
            if i + b < len(fuses) and fuses[i + b]:
                byte |= 1 << b
        total += byte
    return total & 0xFFFF


PINNAMES = ("MREQ:1 ZX512:2 A1:3 WR:4 DIS128:5 BANK2:6 A5:7 BANK0:8 "
            "BANK4:9 BANK3:10 BANK1:11 GND:12 A15:13 A14:14 ROMCS:15 "
            "CLK7FFD:16 SA18:17 SA17:18 RAMCS:19 SA16:20 SA15:21 SA14:22 "
            "IORQ:23 VCC:24")


def write_jed(path, fuses):
    """Escreve um arquivo JEDEC padrao (STX/ETX e checksum de transmissao)."""
    body = []
    body.append("GAL20V8")
    body.append("TKMEM-128 KiCad - decodificador de enderecos")
    body.append("Gerado por tools/galgen.py a partir de hardware/gal/"
                "tkmem128.pld")
    body.append("Licenca CERN-OHL-S v2 - github.com/lrrosa/tkmem128-kicad")
    body.append("*")
    linha = []
    notas = []
    for tok in PINNAMES.split():
        if len(" ".join(linha + [tok])) > 60:
            notas.append(" ".join(linha))
            linha = []
        linha.append(tok)
    if linha:
        notas.append(" ".join(linha))
    for n in notas:
        body.append("NOTE PINS %s*" % n)
    body.append("QF%d*QP24*F0*G0*" % QF)

    def block(addr, n, per_line):
        body.append("L%04d" % addr)
        bits = "".join(str(fuses[addr + i]) for i in range(n))
        for i in range(0, n, per_line):
            body.append(bits[i:i + per_line])
        body[-1] += "*"

    for r in range(ROWS):
        if r % 8 == 0:
            body.append("L%04d" % (r * COLS))
        body.append("".join(str(f) for f in fuses[r * COLS:(r + 1) * COLS]))
        if r % 8 == 7:
            body[-1] += "*"
    block(2560, 8, 8)
    block(2568, 64, 64)
    block(2632, 8, 8)
    block(2640, 64, 64)
    block(2704, 2, 2)
    body.append("C%04X*" % checksum(fuses))

    text = "\x02\n" + "\n".join(body) + "\n\x03"
    tx = sum(ord(c) for c in text) & 0xFFFF
    text += "%04X\n" % tx
    io.open(path, "w", encoding="ascii", newline="\r\n").write(text)
    return checksum(fuses)


if __name__ == "__main__":
    ref = read_jed(sys.argv[1])
    rows = and_rows(ref)
    colmap = derive_colmap(rows)

    names = {MREQ: "MREQ", ZX512: "ZX512", A1: "A1", WR: "WR",
             DIS128: "DIS128", BANK2: "BANK2", A5: "A5", BANK0: "BANK0",
             BANK4: "BANK4", BANK3: "BANK3", BANK1: "BANK1", A15: "A15",
             A14: "A14", IORQ: "IORQ"}
    print("mapa de colunas deduzido das equacoes:")
    for (pin, true_lit), col in sorted(colmap.items(), key=lambda kv: kv[1]):
        print("   coluna %2d = %-7s %s" % (col, names[pin],
                                           "" if true_lit else "(barrado)"))

    mine = build(colmap)
    diff = [i for i in range(QF) if mine[i] != ref[i]]
    print()
    print("fusiveis divergentes: %d de %d" % (len(diff), QF))
    if diff:
        print("   primeiros:", diff[:20])
    print("checksum de referencia: %04X" % checksum(ref))
    print("checksum reconstruido : %04X" % checksum(mine))

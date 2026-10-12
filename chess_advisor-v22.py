#!/usr/bin/env python3
"""
Chess Move Advisor v2.1
-----------------------
Enter your opponent's moves (click the board or type them) and get the best
move to play next, with an opening book, an evaluation bar and live
opening names.

Uses Stockfish if it can find it; otherwise falls back to a built-in engine.

Author: skez01  -  https://github.com/skez01
"""
import argparse
import glob
import math
import os
import random
import shutil
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

import chess
import chess.engine
import chess.polyglot

AUTHOR, AUTHOR_URL = "skez01", "https://github.com/skez01"

SQ, BAR_W, SIDE_W = 70, 22, 340
BG, PANEL, CARD = "#15161a", "#1e2025", "#2a2d35"
TEXT, MUTED = "#e8e8ea", "#9aa0aa"
ACCENT, GREEN, GOLD, RED = "#4f9cf9", "#4ade80", "#f5c451", "#f87171"
FONT = "Helvetica"
LAST_L, LAST_D = "#f7f783", "#bbcb2b"
SEL_L, SEL_D = "#f3e36b", "#d9c93a"
GLYPHS = {"p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚"}
THEMES = [("Green", "#eeeed2", "#769656"), ("Brown", "#f0d9b5", "#b58863"),
          ("Blue", "#dee3e6", "#8ca2ad"), ("Slate", "#c9d1d9", "#586374")]

# --------------------------------------------------------------------------
# Opening book: (family, name, moves).  Matching is by position, so
# transpositions are recognised automatically.
# --------------------------------------------------------------------------
OPENINGS = [
    ("Italian Game", "Italian Game", "e4 e5 Nf3 Nc6 Bc4"),
    ("Italian Game", "Giuoco Piano", "e4 e5 Nf3 Nc6 Bc4 Bc5"),
    ("Italian Game", "Giuoco Pianissimo", "e4 e5 Nf3 Nc6 Bc4 Bc5 c3 Nf6 d3"),
    ("Italian Game", "Evans Gambit", "e4 e5 Nf3 Nc6 Bc4 Bc5 b4"),
    ("Italian Game", "Two Knights Defense", "e4 e5 Nf3 Nc6 Bc4 Nf6"),
    ("Italian Game", "Two Knights: Ng5 Attack", "e4 e5 Nf3 Nc6 Bc4 Nf6 Ng5 d5 exd5"),
    ("Ruy Lopez", "Ruy Lopez", "e4 e5 Nf3 Nc6 Bb5"),
    ("Ruy Lopez", "Ruy Lopez: Morphy Defense", "e4 e5 Nf3 Nc6 Bb5 a6"),
    ("Ruy Lopez", "Ruy Lopez: Closed", "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7"),
    ("Ruy Lopez", "Ruy Lopez: Exchange", "e4 e5 Nf3 Nc6 Bb5 a6 Bxc6 dxc6"),
    ("Ruy Lopez", "Berlin Defense", "e4 e5 Nf3 Nc6 Bb5 Nf6"),
    ("Scotch Game", "Scotch Game", "e4 e5 Nf3 Nc6 d4 exd4 Nxd4"),
    ("King's Gambit", "King's Gambit Accepted", "e4 e5 f4 exf4 Nf3"),
    ("Sicilian Defense", "Sicilian Defense", "e4 c5"),
    ("Sicilian Defense", "Sicilian: Najdorf", "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6"),
    ("Sicilian Defense", "Sicilian: Dragon", "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 g6"),
    ("Sicilian Defense", "Sicilian: Sveshnikov", "e4 c5 Nf3 Nc6 d4 cxd4 Nxd4 Nf6 Nc3 e5"),
    ("Sicilian Defense", "Sicilian: Alapin", "e4 c5 c3"),
    ("Sicilian Defense", "Sicilian: Closed", "e4 c5 Nc3"),
    ("French Defense", "French Defense", "e4 e6"),
    ("French Defense", "French: Advance", "e4 e6 d4 d5 e5"),
    ("French Defense", "French: Winawer", "e4 e6 d4 d5 Nc3 Bb4"),
    ("French Defense", "French: Classical", "e4 e6 d4 d5 Nc3 Nf6"),
    ("French Defense", "French: Exchange", "e4 e6 d4 d5 exd5 exd5"),
    ("Caro-Kann Defense", "Caro-Kann Defense", "e4 c6"),
    ("Caro-Kann Defense", "Caro-Kann: Classical", "e4 c6 d4 d5 Nc3 dxe4 Nxe4 Bf5"),
    ("Caro-Kann Defense", "Caro-Kann: Advance", "e4 c6 d4 d5 e5"),
    ("Scandinavian Defense", "Scandinavian Defense", "e4 d5 exd5 Qxd5 Nc3 Qa5"),
    ("Pirc Defense", "Pirc Defense", "e4 d6 d4 Nf6 Nc3 g6"),
    ("Queen's Gambit", "Queen's Gambit", "d4 d5 c4"),
    ("Queen's Gambit", "Queen's Gambit Declined", "d4 d5 c4 e6 Nc3 Nf6 Bg5 Be7"),
    ("Queen's Gambit", "Queen's Gambit Accepted", "d4 d5 c4 dxc4 Nf3 Nf6 e3"),
    ("Slav Defense", "Slav Defense", "d4 d5 c4 c6 Nf3 Nf6 Nc3"),
    ("King's Indian", "King's Indian Defense", "d4 Nf6 c4 g6 Nc3 Bg7 e4 d6"),
    ("Nimzo-Indian", "Nimzo-Indian Defense", "d4 Nf6 c4 e6 Nc3 Bb4"),
    ("Dutch Defense", "Dutch Defense", "d4 f5 g3 Nf6 Bg2 e6"),
    ("London System", "London System", "d4 d5 Bf4"),
    ("London System", "London: Nf6 / e6 setup", "d4 d5 Bf4 Nf6 e3 e6 Nf3"),
    ("London System", "London vs Indian setup", "d4 Nf6 Bf4"),
    ("English Opening", "English Opening", "c4"),
    ("English Opening", "English: Symmetrical", "c4 c5 Nc3 Nc6 g3 g6 Bg2 Bg7"),
    ("English Opening", "English: Reversed Sicilian", "c4 e5 Nc3 Nf6 Nf3 Nc6"),
    ("Catalan", "Catalan Opening", "d4 Nf6 c4 e6 g3 d5 Bg2 Be7 Nf3 O-O"),
    ("Réti Opening", "Réti Opening", "Nf3 d5 g3 Nf6 Bg2 e6 O-O Be7"),
    ("Grünfeld Defense", "Grünfeld: Exchange", "d4 Nf6 c4 g6 Nc3 d5 cxd5 Nxd5 e4 Nxc3 bxc3"),
    ("Queen's Gambit", "Queen's Gambit Declined: Exchange", "d4 d5 c4 e6 Nc3 Nf6 cxd5 exd5 Bg5"),
    ("Sicilian Defense", "Najdorf: 6.Bg5 e6 7.f4", "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6 Bg5 e6 f4"),
    ("Vienna Game", "Vienna Game", "e4 e5 Nc3 Nf6 f4"),
]
TIMES = {"Blitz (0.5s)": 0.5, "Fast (2s)": 2.0, "Deep (10s)": 10.0, "Maximum (30s)": 30.0}
ANY, ENGINE_ONLY = "Any opening", "Engine only"
FAMILIES = list(dict.fromkeys(f for f, _, _ in OPENINGS))
STYLES = [ANY, ENGINE_ONLY] + FAMILIES


def pos_key(board):
    return " ".join(board.fen().split()[:4])


def build_book():
    names, nxt = {}, {}
    for fam, name, line in OPENINGS:
        b, steps = chess.Board(), []
        try:
            for san in line.split():
                m = b.parse_san(san)
                steps.append((pos_key(b), m))
                b.push(m)
        except ValueError:
            continue  # skip a malformed line rather than crash
        names.setdefault(pos_key(b), name)
        for key, m in steps:
            nxt.setdefault(key, {}).setdefault(m, []).append((name, fam))
    return names, nxt


NAMES, NEXT = build_book()

# --------------------------------------------------------------------------
# Built-in fallback engine (alpha-beta search, used when Stockfish is absent)
# --------------------------------------------------------------------------
VALUES = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
          chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}
MATE = 100000


def _centre(sq):
    f, r = chess.square_file(sq), chess.square_rank(sq)
    return int(3.5 - abs(3.5 - f)) + int(3.5 - abs(3.5 - r))


def evaluate(board):
    """Static score from the side-to-move's point of view."""
    total = 0
    for sq, piece in board.piece_map().items():
        v = VALUES[piece.piece_type]
        c = _centre(sq)
        if piece.piece_type in (chess.KNIGHT, chess.BISHOP):
            v += 10 * c
        elif piece.piece_type == chess.QUEEN:
            v += 2 * c
        elif piece.piece_type == chess.PAWN:
            rank = chess.square_rank(sq)
            advance = rank if piece.color == chess.WHITE else 7 - rank
            v += 8 * advance + 3 * c
        total += v if piece.color == board.turn else -v
    return total


def _order(board):
    def key(m):
        s = 0
        if board.is_capture(m):
            victim = board.piece_type_at(m.to_square) or chess.PAWN
            s += 10 * VALUES[victim] - VALUES[board.piece_type_at(m.from_square)]
        if m.promotion:
            s += 800
        if board.gives_check(m):
            s += 50
        return -s
    return sorted(board.legal_moves, key=key)


def _quiesce(board, alpha, beta, depth):
    stand = evaluate(board)
    if stand >= beta:
        return beta
    if depth == 0:
        return stand
    alpha = max(alpha, stand)
    for m in _order(board):
        if not board.is_capture(m):
            continue
        board.push(m)
        score = -_quiesce(board, -beta, -alpha, depth - 1)
        board.pop()
        if score >= beta:
            return beta
        alpha = max(alpha, score)
    return alpha


def _search(board, depth, alpha, beta, ply):
    if board.is_checkmate():
        return -MATE + ply
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    if depth == 0:
        return _quiesce(board, alpha, beta, 3)
    for m in _order(board):
        board.push(m)
        score = -_search(board, depth - 1, -beta, -alpha, ply + 1)
        board.pop()
        if score >= beta:
            return beta
        alpha = max(alpha, score)
    return alpha


def builtin_best(board, depth=3):
    board = board.copy()
    best, best_score, alpha = None, -10 * MATE, -10 * MATE
    for m in _order(board):
        board.push(m)
        score = -_search(board, depth - 1, -10 * MATE, -alpha, 1)
        board.pop()
        if score > best_score:
            best, best_score = m, score
        alpha = max(alpha, score)
    return best, best_score


# --------------------------------------------------------------------------
# Engine wrapper
# --------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))


def _is_engine_file(p):
    if not os.path.isfile(p):
        return False
    if os.name == "nt":
        return p.lower().endswith(".exe")
    return os.access(p, os.X_OK) and not p.lower().endswith(
        (".py", ".zip", ".txt", ".md", ".tar", ".gz", ".nnue", ".cpp", ".h", ".sh"))


def find_stockfish(explicit=None):
    """Return every plausible Stockfish path, best guesses first."""
    found = []
    for root in dict.fromkeys([HERE, os.getcwd()]):
        for p in glob.glob(os.path.join(root, "**", "stockfish*"), recursive=True):
            if _is_engine_file(p):
                found.append(p)
    found.sort(key=lambda p: ("avx2" not in p.lower(), len(p)))
    candidates = [explicit, os.environ.get("STOCKFISH_PATH"),
                  shutil.which("stockfish"), *found,
                  "/usr/games/stockfish", "/usr/local/bin/stockfish",
                  "/opt/homebrew/bin/stockfish"]
    return [c for c in dict.fromkeys(candidates) if c and os.path.isfile(c)]


def find_book(explicit=None):
    if explicit:
        return explicit
    for pat in ("*.bin", os.path.join("book", "*.bin")):
        hits = glob.glob(os.path.join(HERE, pat))
        if hits:
            return hits[0]
    return None


class Advisor:
    def __init__(self, stockfish_path=None, threads=None, hash_mb=1024,
                 tablebases=None, book=None):
        self.lock = threading.Lock()
        self.engine, self.reader, self.info = None, None, ""
        self.error, self.path = "", None
        for path in find_stockfish(stockfish_path):
            try:
                eng = chess.engine.SimpleEngine.popen_uci(path)
            except Exception as e:
                self.error = f"{os.path.basename(path)}: {e}"
                print("Could not start", path, "-", e)
                continue
            self.engine, self.path, self.error = eng, path, ""
            threads = threads or max(1, (os.cpu_count() or 2) - 1)
            cfg, opts = {}, eng.options
            if "Threads" in opts:
                cfg["Threads"] = threads
            if "Hash" in opts:
                cfg["Hash"] = hash_mb
            if tablebases and "SyzygyPath" in opts:
                cfg["SyzygyPath"] = tablebases
            try:
                if cfg:
                    eng.configure(cfg)
            except Exception as e:
                print("Could not apply engine settings:", e)
            self.info = f"{threads} threads, {hash_mb} MB" + (
                ", tablebases" if "SyzygyPath" in cfg else "")
            print("Using Stockfish:", path)
            break
        if not self.engine and not self.error:
            print("No Stockfish found in", HERE)
        self.name = "Stockfish" if self.engine else "Built-in engine"
        bpath = find_book(book)
        if bpath:
            try:
                self.reader = chess.polyglot.open_reader(bpath)
            except Exception:
                self.reader = None

    def analyse(self, board, seconds, on_update, stop):
        """Stream (move, centipawns, depth, nps) while the search deepens.
        Returns the final tuple, or None if there was nothing to report."""
        with self.lock:
            if stop():
                return None
            if not self.engine:
                move, cp = builtin_best(board)
                return move, cp, 3, 0
            best, last_depth = None, 0
            with self.engine.analysis(board, chess.engine.Limit(time=seconds)) as an:
                for info in an:
                    if stop():
                        break
                    pv, score = info.get("pv"), info.get("score")
                    if not pv or score is None or info.get("multipv", 1) != 1:
                        continue
                    depth = info.get("depth", 0)
                    cp = score.pov(board.turn).score(mate_score=MATE)
                    best = (pv[0], cp, depth, info.get("nps", 0))
                    if depth > last_depth and depth >= 6:
                        last_depth = depth
                        on_update(*best)
            return best

    def close(self):
        if self.reader:
            self.reader.close()
        if self.engine:
            try:
                self.engine.quit()
            except Exception:
                pass


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------
class Btn(tk.Label):
    """Flat label-button (looks the same on Windows, macOS and Linux)."""

    def __init__(self, parent, text, cmd, accent=False):
        self._bg = ACCENT if accent else CARD
        self._hv = "#6ab0ff" if accent else "#3a3e48"
        super().__init__(parent, text=text, bg=self._bg, padx=12, pady=7,
                         fg="white" if accent else TEXT, cursor="hand2",
                         font=(FONT, 10, "bold"))
        self.bind("<Enter>", lambda e: self.config(bg=self._hv))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))
        self.bind("<Button-1>", lambda e: cmd())


class App:
    def __init__(self, root, advisor):
        self.root, self.advisor = root, advisor
        self.board = chess.Board()
        self.my_color = chess.WHITE
        self.flipped = False
        self.theme = 0
        self.selected = None
        self.suggestion = self.alt = None
        self.eval_white = 0
        self.token = 0  # invalidates stale analysis results

        root.title(f"Chess Move Advisor  -  by {AUTHOR}")
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.quit)
        root.bind("<Control-z>", lambda e: self.undo())
        self.style = tk.StringVar(value=ANY)
        self.speed = tk.StringVar(value="Fast (2s)")
        self.build_ui()
        self.new_game(first=True)

    # ---- layout ----------------------------------------------------------
    def build_ui(self):
        root = self.root
        left = tk.Frame(root, bg=BG)
        left.grid(row=0, column=0, padx=(14, 8), pady=14)
        self.bar = tk.Canvas(left, width=BAR_W, height=SQ * 8, bg=BG,
                             highlightthickness=0)
        self.bar.pack(side="left", padx=(0, 8))
        self.canvas = tk.Canvas(left, width=SQ * 8, height=SQ * 8, bg=BG,
                                highlightthickness=0)
        self.canvas.pack(side="left")
        self.canvas.bind("<Button-1>", self.on_click)

        side = tk.Frame(root, bg=PANEL, width=SIDE_W)
        side.grid(row=0, column=1, sticky="ns", padx=(0, 14), pady=14)
        side.pack_propagate(False)
        p = tk.Frame(side, bg=PANEL)
        p.pack(fill="both", expand=True, padx=14, pady=12)

        tk.Label(p, text="♞ Chess Move Advisor", bg=PANEL, fg=ACCENT,
                 font=(FONT, 17, "bold")).pack(anchor="w")
        info = f"Engine: {self.advisor.name}"
        if self.advisor.info:
            info += f"  •  {self.advisor.info}"
        if self.advisor.reader:
            info += "  •  master book"
        elab = tk.Label(p, text=info, bg=PANEL, fg=MUTED, font=(FONT, 9),
                        wraplength=300, justify="left")
        elab.pack(anchor="w")
        if not self.advisor.engine:
            why = (f"Couldn't start Stockfish ({self.advisor.error})"
                   if self.advisor.error else "Stockfish not found")
            elab.config(text=f"⚠ {why} - using the weak built-in engine. "
                             "Click here to download Stockfish.",
                        fg=RED, cursor="hand2")
            elab.bind("<Button-1>", lambda e: webbrowser.open(
                "https://stockfishchess.org/download/"))
        self.status = tk.Label(p, bg=PANEL, fg=TEXT, font=(FONT, 12, "bold"))
        self.status.pack(anchor="w", pady=(8, 6))

        card = tk.Frame(p, bg=CARD)
        card.pack(fill="x")
        self.advice = tk.Label(card, bg=CARD, fg=GREEN, anchor="w",
                               font=(FONT, 16, "bold"))
        self.advice.pack(fill="x", padx=10, pady=(8, 0))
        self.advice2 = tk.Label(card, bg=CARD, fg=MUTED, anchor="w",
                                justify="left", wraplength=290, font=(FONT, 9))
        self.advice2.pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(p, text="OPENING", bg=PANEL, fg=MUTED,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(10, 0))
        self.open_name = tk.Label(p, bg=PANEL, fg=GOLD, anchor="w",
                                  font=(FONT, 12, "bold"))
        self.open_name.pack(fill="x")
        self.book_lbl = tk.Label(p, bg=PANEL, fg=MUTED, anchor="w",
                                 justify="left", wraplength=300, font=(FONT, 9))
        self.book_lbl.pack(fill="x")

        srow = tk.Frame(p, bg=PANEL)
        srow.pack(fill="x", pady=(10, 0))
        tk.Label(srow, text="Opening style", bg=PANEL, fg=TEXT,
                 font=(FONT, 10)).pack(side="left")
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("TCombobox", fieldbackground=CARD, background=CARD,
                     foreground=TEXT, arrowcolor=TEXT, bordercolor=CARD)
        st.map("TCombobox", fieldbackground=[("readonly", CARD)],
               foreground=[("readonly", TEXT)])
        self.root.option_add("*TCombobox*Listbox.background", CARD)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXT)
        cb = ttk.Combobox(srow, textvariable=self.style, values=STYLES,
                          state="readonly", width=20)
        cb.pack(side="right")
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        trow = tk.Frame(p, bg=PANEL)
        trow.pack(fill="x", pady=(6, 0))
        tk.Label(trow, text="Thinking time", bg=PANEL, fg=TEXT,
                 font=(FONT, 10)).pack(side="left")
        cb2 = ttk.Combobox(trow, textvariable=self.speed, values=list(TIMES),
                           state="readonly", width=20)
        cb2.pack(side="right")
        cb2.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        tk.Label(p, text="Opponent's move  (e4, Nf3, O-O, e2e4)", bg=PANEL,
                 fg=MUTED, font=(FONT, 9)).pack(anchor="w", pady=(10, 2))
        erow = tk.Frame(p, bg=PANEL)
        erow.pack(fill="x")
        self.entry = tk.Entry(erow, bg=CARD, fg=TEXT, insertbackground=TEXT,
                              relief="flat", font=(FONT, 13),
                              highlightthickness=1, highlightbackground=CARD,
                              highlightcolor=ACCENT)
        self.entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.entry.bind("<Return>", lambda e: self.submit_text())
        Btn(erow, "Enter", self.submit_text).pack(side="left", padx=(6, 0))

        grid = tk.Frame(p, bg=PANEL)
        grid.pack(fill="x", pady=(10, 0))
        grid.columnconfigure((0, 1), weight=1)
        Btn(grid, "Play suggestion", self.play_suggestion, True).grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=3)
        Btn(grid, "Undo", self.undo).grid(row=1, column=0, sticky="ew", padx=(0, 3), pady=3)
        Btn(grid, "Flip board", self.flip).grid(row=1, column=1, sticky="ew", padx=(3, 0), pady=3)
        self.theme_btn = Btn(grid, "Theme: Green", self.next_theme)
        self.theme_btn.grid(row=2, column=0, sticky="ew", padx=(0, 3), pady=3)
        Btn(grid, "New game", self.new_game).grid(row=2, column=1, sticky="ew", padx=(3, 0), pady=3)

        self.hist = tk.Text(p, height=3, bg=CARD, fg=MUTED, relief="flat",
                            wrap="word", font=(FONT, 9), state="disabled",
                            highlightthickness=0, padx=8, pady=6)
        self.hist.pack(fill="x", pady=(8, 0))

        foot = tk.Label(p, text=f"Made by {AUTHOR}  •  github.com/{AUTHOR}",
                        bg=PANEL, fg=MUTED, cursor="hand2", font=(FONT, 9))
        foot.pack(side="bottom", anchor="e", pady=(6, 0))
        foot.bind("<Button-1>", lambda e: webbrowser.open(AUTHOR_URL))
        foot.bind("<Enter>", lambda e: foot.config(fg=ACCENT))
        foot.bind("<Leave>", lambda e: foot.config(fg=MUTED))

    # ---- drawing ---------------------------------------------------------
    def sq_xy(self, sq):
        f, r = chess.square_file(sq), chess.square_rank(sq)
        col = 7 - f if self.flipped else f
        row = r if self.flipped else 7 - r
        return col * SQ, row * SQ

    def arrow(self, mv, color, width):
        x1, y1 = self.sq_xy(mv.from_square)
        x2, y2 = self.sq_xy(mv.to_square)
        self.canvas.create_line(
            x1 + SQ / 2, y1 + SQ / 2, x2 + SQ / 2, y2 + SQ / 2, fill=color,
            width=width, arrow=tk.LAST, capstyle="round",
            arrowshape=(int(width * 2.4), int(width * 2.8), width))

    def draw(self):
        c, b = self.canvas, self.board
        c.delete("all")
        _, lt, dk = THEMES[self.theme]
        last = b.peek() if b.move_stack else None
        check_sq = b.king(b.turn) if b.is_check() else None
        targets = ({m.to_square for m in b.legal_moves if m.from_square == self.selected}
                   if self.selected is not None else set())
        for sq in chess.SQUARES:
            x, y = self.sq_xy(sq)
            light = (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 1
            col = lt if light else dk
            if last and sq in (last.from_square, last.to_square):
                col = LAST_L if light else LAST_D
            if sq == self.selected:
                col = SEL_L if light else SEL_D
            if sq == check_sq:
                col = "#e5534b"
            c.create_rectangle(x, y, x + SQ, y + SQ, fill=col, outline="")
            ink = dk if light else lt
            if x == 0:
                c.create_text(x + 4, y + 8, text=str(chess.square_rank(sq) + 1),
                              anchor="w", fill=ink, font=(FONT, 8, "bold"))
            if y == SQ * 7:
                c.create_text(x + SQ - 4, y + SQ - 8, text="abcdefgh"[chess.square_file(sq)],
                              anchor="e", fill=ink, font=(FONT, 8, "bold"))
        font = ("Arial", int(SQ * 0.68))
        for sq, p in b.piece_map().items():
            x, y = self.sq_xy(sq)
            cx, cy, g = x + SQ / 2, y + SQ / 2, GLYPHS[p.symbol().lower()]
            if p.color == chess.WHITE:
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, -1)):
                    c.create_text(cx + dx, cy + dy, text=g, font=font, fill="#1a1a1a")
                c.create_text(cx, cy, text=g, font=font, fill="#ffffff")
            else:
                c.create_text(cx, cy, text=g, font=font, fill="#111111")
        for sq in targets:
            x, y = self.sq_xy(sq)
            if b.piece_at(sq) or b.is_en_passant(chess.Move(self.selected, sq)):
                c.create_oval(x + 4, y + 4, x + SQ - 4, y + SQ - 4, outline="#555", width=4)
            else:
                c.create_oval(x + SQ * .37, y + SQ * .37, x + SQ * .63, y + SQ * .63,
                              fill="#555", outline="")
        if self.alt:
            self.arrow(self.alt, "#f59e0b", 5)
        if self.suggestion:
            self.arrow(self.suggestion, ACCENT, 9)
        self.draw_bar()
        self.hist.config(state="normal")
        self.hist.delete("1.0", "end")
        self.hist.insert("end", self.history_text())
        self.hist.see("end")
        self.hist.config(state="disabled")

    def draw_bar(self):
        c, H, cp = self.bar, SQ * 8, self.eval_white
        c.delete("all")
        frac = 1 / (1 + math.exp(-max(-3000, min(3000, cp)) / 350))
        wh = H * frac
        w_col, b_col = "#f1f1f1", "#3a3a3a"
        if self.flipped:  # white at the top
            c.create_rectangle(0, 0, BAR_W, wh, fill=w_col, outline="")
            c.create_rectangle(0, wh, BAR_W, H, fill=b_col, outline="")
        else:
            c.create_rectangle(0, 0, BAR_W, H - wh, fill=b_col, outline="")
            c.create_rectangle(0, H - wh, BAR_W, H, fill=w_col, outline="")
        c.create_line(0, H / 2, BAR_W, H / 2, fill="#888")
        label = "M" if abs(cp) > MATE - 200 else f"{abs(cp) / 100:.1f}"
        white_end_top = self.flipped
        at_white_end = cp >= 0
        top = white_end_top == at_white_end
        c.create_text(BAR_W / 2, 10 if top else H - 10, text=label,
                      fill="#222" if at_white_end else "#eee",
                      font=(FONT, 8, "bold"))

    def history_text(self):
        b, out = chess.Board(), []
        for i, m in enumerate(self.board.move_stack):
            if i % 2 == 0:
                out.append(f"{i // 2 + 1}.")
            out.append(b.san(m))
            b.push(m)
        return " ".join(out)

    # ---- opening info ----------------------------------------------------
    def opening_name(self):
        b, found = chess.Board(), None
        for m in self.board.move_stack:
            b.push(m)
            found = NAMES.get(pos_key(b), found)
        return found

    def update_opening(self):
        found = self.opening_name()
        self.open_name.config(text=found or (
            "Starting position" if not self.board.move_stack else "Out of book"))
        rows = []
        for m, ls in NEXT.get(pos_key(self.board), {}).items():
            names = list(dict.fromkeys(n for n, _ in ls))
            more = f"  (+{len(names) - 1})" if len(names) > 1 else ""
            rows.append(f"{self.board.san(m)}  —  {names[0]}{more}")
        shown = rows[:5] + ([f"…and {len(rows) - 5} more"] if len(rows) > 5 else [])
        self.book_lbl.config(text="Book moves:\n" + "\n".join(shown) if rows
                             else "No book moves here")

    def book_choice(self):
        style = self.style.get()
        if style == ENGINE_ONLY:
            return None
        if style == ANY and self.advisor.reader:
            try:  # strongest move from the master-game book
                return self.advisor.reader.find(self.board).move, "Master book"
            except IndexError:
                pass
        cands = []
        for m, ls in NEXT.get(pos_key(self.board), {}).items():
            use = [n for n, f in ls if style == ANY or f == style]
            if use:
                cands.append((m, use[0]))
        return random.choice(cands) if cands else None

    # ---- game flow -------------------------------------------------------
    def eval_for_me(self, cp_white):
        me = cp_white if self.my_color == chess.WHITE else -cp_white
        if abs(me) > MATE - 200:
            return "Forced mate for you" if me > 0 else "You're getting mated"
        return f"Eval {me / 100:+.2f} for you"

    def refresh(self):
        self.token += 1
        self.suggestion = self.alt = None
        self.advice.config(text="")
        self.advice2.config(text="")
        b = self.board
        self.update_opening()
        if b.is_game_over():
            res = b.result()
            self.eval_white = MATE if res == "1-0" else -MATE if res == "0-1" else 0
            self.status.config(text=f"Game over  {res}", fg=GOLD)
        elif b.turn == self.my_color:
            self.status.config(text="Your move — thinking…", fg=GREEN)
            self.analyse()
        else:
            self.status.config(text="Opponent's turn — enter their move", fg=TEXT)
            if self.advisor.engine:  # builtin engine is too slow to run twice
                self.analyse()
        self.draw()

    def analyse(self):
        token, board = self.token, self.board.copy()
        mine = board.turn == self.my_color
        book = self.book_choice() if mine else None
        secs = TIMES[self.speed.get()]
        if not mine:
            secs = min(secs, 2.0)

        def stop():
            return token != self.token

        def show(move, cp, depth, nps, final):
            cpw = cp if board.turn == chess.WHITE else -cp
            san = board.san(move)
            bsan = board.san(book[0]) if book else None
            self.root.after(0, lambda: self.show_result(
                token, mine, move, san, cpw, book, bsan, depth, nps, final))

        def work():
            try:
                res = self.advisor.analyse(
                    board, secs, lambda m, c, d, n: show(m, c, d, n, False), stop)
                if res:
                    show(*res, True)
            except Exception as e:  # engine died, etc.
                msg = f"Engine error: {e}"
                self.root.after(0, lambda: self.advice2.config(text=msg))

        threading.Thread(target=work, daemon=True).start()

    def show_result(self, token, mine, move, san, cpw, book, bsan,
                    depth=0, nps=0, final=True):
        if token != self.token:
            return
        self.eval_white = cpw
        speed = (f" • {nps / 1e6:.1f}M nodes/s" if nps >= 1e6
                 else f" • {nps / 1e3:.0f}k nodes/s" if nps else "")
        ev = (self.eval_for_me(cpw) + f"\ndepth {depth}{speed}"
              + ("" if final else "  …still thinking"))
        if not mine:
            self.advice.config(text=f"Likely reply: {san}", fg=MUTED)
            self.advice2.config(text=ev)
        elif book:
            self.suggestion = book[0]
            self.alt = None if book[0] == move else move
            self.status.config(text="Your move", fg=GREEN)
            self.advice.config(text=f"Play {bsan}", fg=GREEN)
            if book[0] == move:
                self.advice2.config(text=f"Book move: {book[1]} — engine agrees\n{ev}")
            else:
                self.advice2.config(
                    text=f"Book move: {book[1]}\nEngine's pick: {san} (orange arrow)\n{ev}")
        else:
            self.suggestion = move
            self.status.config(text="Your move", fg=GREEN)
            self.advice.config(text=f"Play {san}", fg=GREEN)
            note = "" if self.style.get() == ENGINE_ONLY else "Out of book — engine move\n"
            self.advice2.config(text=note + ev)
        self.draw()

    def push(self, move):
        self.board.push(move)
        self.selected = None
        self.refresh()

    def parse(self, text):
        for fn in (self.board.parse_san, self.board.parse_uci):
            try:
                return fn(text.strip())
            except ValueError:
                continue
        return None

    def submit_text(self):
        text = self.entry.get()
        if not text.strip():
            return
        move = self.parse(text)
        if move is None:
            messagebox.showerror("Illegal move",
                                 f"'{text}' isn't a legal move in this position.")
            return
        self.entry.delete(0, "end")
        self.push(move)

    def on_click(self, event):
        col, row = event.x // SQ, event.y // SQ
        if not (0 <= col < 8 and 0 <= row < 8):
            return
        f = 7 - col if self.flipped else col
        r = row if self.flipped else 7 - row
        sq = chess.square(f, r)
        if self.selected is not None:
            move = chess.Move(self.selected, sq)
            p = self.board.piece_at(self.selected)
            if p and p.piece_type == chess.PAWN and r in (0, 7):
                move.promotion = chess.QUEEN
            if move in self.board.legal_moves:
                self.push(move)
                return
        p = self.board.piece_at(sq)
        self.selected = sq if p and p.color == self.board.turn and sq != self.selected else None
        self.draw()

    # ---- buttons ---------------------------------------------------------
    def play_suggestion(self):
        if self.suggestion:
            self.push(self.suggestion)

    def undo(self):
        if self.board.move_stack:
            self.board.pop()
            self.selected = None
            self.refresh()

    def flip(self):
        self.flipped = not self.flipped
        self.draw()

    def next_theme(self):
        self.theme = (self.theme + 1) % len(THEMES)
        self.theme_btn.config(text=f"Theme: {THEMES[self.theme][0]}")
        self.draw()

    def choose_color(self):
        win = tk.Toplevel(self.root, bg=PANEL, padx=26, pady=22)
        win.title("New game")
        win.transient(self.root)
        win.resizable(False, False)
        result = {"c": None}

        def pick(c):
            result["c"] = c
            win.destroy()

        tk.Label(win, text="Which side are you playing?", bg=PANEL, fg=TEXT,
                 font=(FONT, 13, "bold")).pack(pady=(0, 14))
        row = tk.Frame(win, bg=PANEL)
        row.pack()
        Btn(row, "♔  White", lambda: pick(chess.WHITE), True).pack(side="left", padx=6)
        Btn(row, "♚  Black", lambda: pick(chess.BLACK)).pack(side="left", padx=6)
        win.wait_visibility()
        try:
            win.grab_set()
        except tk.TclError:
            pass
        self.root.wait_window(win)
        return result["c"]

    def new_game(self, first=False):
        color = self.choose_color()
        if color is None:
            if not first:
                return
            color = chess.WHITE
        self.my_color = color
        self.flipped = color == chess.BLACK
        self.board = chess.Board()
        self.selected = None
        self.eval_white = 0
        self.refresh()

    def quit(self):
        self.advisor.close()
        self.root.destroy()


def main():
    ap = argparse.ArgumentParser(description="Chess move advisor by " + AUTHOR)
    ap.add_argument("--stockfish", help="path to a Stockfish executable")
    ap.add_argument("--threads", type=int, help="engine threads (default: CPU cores - 1)")
    ap.add_argument("--hash", type=int, default=1024, help="engine hash in MB (default 1024)")
    ap.add_argument("--tablebases", help="folder with Syzygy endgame tablebases")
    ap.add_argument("--book", help="Polyglot opening book (.bin) of master games")
    args = ap.parse_args()

    advisor = Advisor(args.stockfish, args.threads, args.hash,
                      args.tablebases, args.book)
    root = tk.Tk()
    App(root, advisor)
    root.mainloop()


if __name__ == "__main__":
    main()

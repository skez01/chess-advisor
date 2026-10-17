# ♞ Chess Move Advisor

A desktop app that opens a chess board. Enter your opponent's move (click the
board or type it) and it tells you the best move to play next.

Made by [skez01](https://github.com/skez01).

## Features

- **Best-move suggestions** shown as a blue arrow, powered by Stockfish (or a
  built-in engine if Stockfish isn't installed)
- **Opening book** with 40+ lines across 18 openings: Italian, Ruy Lopez,
  Scotch, King's Gambit, Sicilian (Najdorf, Dragon, Sveshnikov, Alapin),
  French, Caro-Kann, Scandinavian, Pirc, Queen's Gambit, Slav, King's Indian,
  Nimzo-Indian, Dutch, London System and English
- **Opening style picker**: choose "Any opening" for variety, a specific
  opening to steer the game into it, or "Engine only" for pure engine play
- **Live opening name** and a list of book moves for the current position
  (transpositions are recognised automatically)
- **Engine comparison**: when the book move differs from the engine's top
  choice, the engine's pick is shown as an orange arrow
- **Evaluation bar** beside the board, plus the opponent's likely reply
- Dark UI, four board themes, last-move and check highlights, legal-move dots

## Quick start

```bash
git clone https://github.com/skez01/chess-advisor.git
cd chess-advisor
pip install -r requirements.txt
python chess_advisor.py
```

Requires Python 3.8+ with Tkinter (included with most Python installs; on
Debian/Ubuntu: `sudo apt install python3-tk`).

## How to use

1. Choose your side when the game starts.
2. On the opponent's turn, enter their move by **clicking the board** or
   **typing it** (`e4`, `Nf3`, `O-O`, or `e2e4`) and pressing Enter.
3. On your turn, the recommended move appears as an arrow. Play it on your
   real board, then enter your move the same way (or press **Play suggestion**).
4. Use **Undo** (or Ctrl+Z) if you mistype, **Flip board** to turn the board,
   and **Theme** to change the colors.

## Stronger analysis with Stockfish (optional)

The app auto-detects [Stockfish](https://stockfishchess.org/download/) if it
is installed (`brew install stockfish`, `sudo apt install stockfish`, or
download the binary). Without it, a weaker built-in engine is used.

```bash
python chess_advisor.py --stockfish /path/to/stockfish --time 2
# or set STOCKFISH_PATH in your environment
```

The sidebar shows which engine is active.

## Adding your own openings

Edit the `OPENINGS` list near the top of `chess_advisor.py`. Each entry is
`(family, name, "space separated SAN moves")`.

## License

MIT © [skez01](https://github.com/skez01)
<img width="1774" height="1285" alt="image" src="https://github.com/user-attachments/assets/280063b9-abe4-4054-8b85-fe8385ad34a8" />
*can beat magnus carlson bot on fast mode on chess.com*

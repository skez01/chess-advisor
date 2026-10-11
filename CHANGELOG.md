# Changelog

All notable changes to this project are documented here.

## [2.0.0] - 2026-10-11

### Added
- **Opening book** with 40+ lines across 18 openings: Italian Game, Ruy Lopez, Scotch Game, King's Gambit, Sicilian (Najdorf, Dragon, Sveshnikov, Alapin, Closed), French, Caro-Kann, Scandinavian, Pirc, Queen's Gambit, Slav, King's Indian, Nimzo-Indian, Dutch, London System and English Opening.
- **Opening style picker**: choose "Any opening" for variety, a specific opening to steer the game into it, or "Engine only".
- **Live opening name** and a list of book moves for the current position. Transpositions are recognised automatically.
- **Engine comparison**: when the book move differs from the engine's top choice, the engine's pick is shown as an orange arrow.
- **Evaluation bar** next to the board.
- **"Likely reply"** hint on the opponent's turn (when Stockfish is available).
- Four **board themes** (Green, Brown, Blue, Slate) with a Theme button.
- Last-move and check highlights, capture rings, and file/rank labels on the board.
- Side-picker window when starting a new game.
- Ctrl+Z shortcut for undo.
- Clickable author link to [skez01](https://github.com/skez01) in the sidebar.

### Changed
- Redesigned dark UI with a sidebar layout.
- White pieces are now outlined so they are easier to see.
- Buttons are now custom flat buttons so they look the same on Windows, macOS and Linux.
- Evaluation is now shown from your point of view ("Eval +0.35 for you").
- README rewritten with the new features and a guide to adding your own openings.

### Fixed
- Tidied the built-in engine's quiescence search cutoff logic.

## [1.0.0] - 2026-10-11

### Added
- Desktop chess board built with Tkinter and python-chess.
- Enter the opponent's move by clicking the board or typing it (SAN or UCI).
- Best-move suggestion shown as an arrow, using Stockfish when installed.
- Built-in alpha-beta engine as a fallback when Stockfish isn't available.
- Undo, flip board and new game controls.
- Choose to play as White or Black.

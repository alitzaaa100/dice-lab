"""Dice Lab: an interactive dice game and simulator.

Pure Python, standard library only. Works in a terminal or a notebook cell.
Run with:  python dice_lab.py
"""
import random
import sys
import time

FACES = {
    1: ["         ", "    o    ", "         "],
    2: ["  o      ", "         ", "      o  "],
    3: ["  o      ", "    o    ", "      o  "],
    4: ["  o   o  ", "         ", "  o   o  "],
    5: ["  o   o  ", "    o    ", "  o   o  "],
    6: ["  o   o  ", "  o   o  ", "  o   o  "],
}
CHI_LIMIT = 11.07  # 5% critical value, 5 degrees of freedom
PAUSE = 0.0 if not sys.stdout.isatty() and "ipykernel" not in sys.modules else 1.0


def pause(seconds):
    time.sleep(seconds * PAUSE)


def draw_dice(*values):
    """Return ASCII art for one or more dice side by side."""
    top = "+---------+ " * len(values)
    rows = [top]
    for line in range(3):
        rows.append(" ".join(f"|{FACES[v][line]}|" for v in values) + " ")
    rows.append(top)
    return "\n".join(r.rstrip() for r in rows)


def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        print()
        raise SystemExit


def ask_int(prompt, low, high):
    """Accept '500', '1,000' or '10k'. Re-ask until valid."""
    while True:
        text = ask(prompt).lower().replace(",", "").replace("_", "")
        try:
            value = int(float(text[:-1]) * 1000) if text.endswith("k") else int(text)
        except ValueError:
            print("  Please enter a whole number (for example 500, 1,000 or 10k).")
            continue
        if low <= value <= high:
            return value
        print(f"  Please enter a number from {low:,} to {high:,}.")


def roll_animation():
    print("  Rolling...")
    for _ in range(4):
        print(draw_dice(random.randint(1, 6)))
        pause(0.25)
    final = random.randint(1, 6)
    print("\n  Landed on:")
    print(draw_dice(final))
    return final


# ---------------------------------------------------------------- guess game
def guess_game():
    print("\n  GUESS THE ROLL")
    print("  Guess the face. A hit scores 10 x your current streak.\n")
    score = streak = 0
    history = []
    while True:
        text = ask("  Your guess (1-6, or q to quit): ").lower()
        if text == "q":
            break
        if text not in {"1", "2", "3", "4", "5", "6"}:
            print("  Type a number from 1 to 6.")
            continue
        guess = int(text)
        roll = roll_animation()
        if roll == guess:
            streak += 1
            gained = 10 * streak
            score += gained
            print(f"  HIT! +{gained} points.")
        else:
            streak = 0
            print(f"  Missed (you guessed {guess}).")
        history.append(roll)
        print(f"  Score {score} | Streak {streak} | Last rolls: {' '.join(map(str, history[-12:]))}\n")
    print(f"\n  Final score: {score}. Odds of any single hit were 1 in 6.\n")


# -------------------------------------------------------------------- duel
def duel():
    print("\n  DICE DUEL: first to 3 round wins beats the computer.\n")
    you = cpu = 0
    while you < 3 and cpu < 3:
        ask("  Press Enter to roll... ")
        a, b = random.randint(1, 6), random.randint(1, 6)
        print("      You                 Computer")
        left = draw_dice(a).splitlines()
        right = draw_dice(b).splitlines()
        for l, r in zip(left, right):
            print(f"  {l:<22}{r}")
        if a > b:
            you += 1
            print("  You win the round!")
        elif b > a:
            cpu += 1
            print("  Computer wins the round.")
        else:
            print("  Tie, no points.")
        print(f"  Score: you {you} - computer {cpu}\n")
    print("  YOU WIN THE DUEL!\n" if you == 3 else "  The computer wins this time.\n")


# --------------------------------------------------------------- simulator
def simulate(n):
    counts = [0] * 7
    total = prev = streak = best_streak = best_face = 0
    step = max(1, n // 40)
    for i in range(1, n + 1):
        roll = random.randint(1, 6)
        counts[roll] += 1
        total += roll
        if roll == prev:
            streak += 1
        else:
            streak, prev = 1, roll
        if streak > best_streak:
            best_streak, best_face = streak, roll
        if i % step == 0 or i == n:
            done = int(i / n * 30)
            print(f"\r  Rolling [{'#' * done}{'.' * (30 - done)}] {i / n:4.0%}", end="", flush=True)
    print()
    return counts, total / n, best_streak, best_face


def show_results(n, counts, mean, best_streak, best_face):
    faces = counts[1:]
    high, low = max(faces), min(faces)
    fair = n / 6
    width = 30
    print("\n  ==== RESULTS ====")
    print(f"  Total rolls: {n:,}   (| marks the fair share of one sixth)\n")
    for face in range(1, 7):
        c = counts[face]
        bar_len = round(c / high * width)
        marker = round(fair / high * width)
        cells = ["#" if i < bar_len else " " for i in range(width + 1)]
        cells[min(marker, width)] = "|" if cells[min(marker, width)] == " " else "+"
        badge = "  <- hottest" if c == high else "  <- coldest" if c == low else ""
        print(f"  {face} {''.join(cells)} {c:>9,} ({c / n:6.2%}){badge}")
    chi = sum((c - fair) ** 2 / fair for c in faces)
    print(f"\n  Average roll: {mean:.3f} (fair dice: 3.500)")
    print(f"  Longest streak: {best_streak} in a row of face {best_face}")
    verdict = "looks fair" if chi < CHI_LIMIT else "is unusually lopsided (about a 1-in-20 event)"
    print(f"  Fairness check: chi-square {chi:.2f} (limit {CHI_LIMIT}), the result {verdict}.\n")


def lab():
    print("\n  SIMULATOR")
    while True:
        n = ask_int("  How many rolls? (1 to 5,000,000; e.g. 1000 or 10k): ", 1, 5_000_000)
        show_results(n, *simulate(n))
        if ask("  Run another? (y/n): ").lower() not in {"y", "yes"}:
            break
    print()


# -------------------------------------------------------------------- main
def main():
    print("\n  Welcome to the Dice Lab!")
    while True:
        print("  1) Guess the roll   2) Duel the computer   3) Simulator   4) Quit")
        choice = ask("  Pick a mode: ")
        if choice == "1":
            guess_game()
        elif choice == "2":
            duel()
        elif choice == "3":
            lab()
        elif choice in {"4", "q"}:
            print("\n  Thanks for playing. Bye!\n")
            break
        else:
            print("  Please choose 1, 2, 3 or 4.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Bye!\n")

class Player:
    """Tracks gold, lives, and score for the current session."""

    def __init__(self, gold: int = 150, lives: int = 10):
        self.gold = gold
        self.lives = lives
        self.score = 0

    def spend_gold(self, amount: int) -> bool:
        """Deduct gold if affordable. Returns True on success."""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def earn_gold(self, amount: int) -> None:
        self.gold += amount
        self.score += amount

    def lose_life(self) -> None:
        self.lives = max(0, self.lives - 1)

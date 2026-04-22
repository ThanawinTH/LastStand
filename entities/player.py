from config import PLAYER_START_GOLD, PLAYER_START_LIVES


class Player:
    def __init__(self) -> None:
        self.gold = PLAYER_START_GOLD
        self.lives = PLAYER_START_LIVES
        self.score = 0

        # Session statistics
        self.towers_placed = 0
        self.gold_on_upgrades = 0
        self.lives_lost = 0
        self.enemies_killed = 0

    def can_afford(self, cost: int) -> bool:
        return self.gold >= cost

    def spend_gold(self, amount: int) -> bool:
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def earn_gold(self, amount: int) -> None:
        self.gold += amount

    def lose_life(self, amount: int = 1) -> None:
        self.lives -= amount
        self.lives_lost += amount

    def add_score(self, amount: int) -> None:
        self.score += amount

    def record_upgrade_spending(self, amount: int) -> None:
        self.gold_on_upgrades += amount
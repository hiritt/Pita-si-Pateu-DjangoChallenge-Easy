from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q


class Unit(models.Model):
    class UnitType(models.TextChoices):
        INFANTRY = "Infantry", "Infantry"
        CANNON = "Cannon", "Cannon"
        CAVALRY = "Cavalry", "Cavalry"
        KNIGHT = "Knight", "Knight"

    class Team(models.TextChoices):
        BLUE = "Blue", "Blue"
        RED = "Red", "Red"

    name = models.CharField(max_length=100)
    unit_type = models.CharField(max_length=10, choices=UnitType.choices)
    team = models.CharField(max_length=4, choices=Team.choices)
    health = models.PositiveSmallIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    attack_points = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
    )
    profile_image_link = models.URLField(
        max_length=500,
        blank=True
    )

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(health__gte=0) & Q(health__lte=100),
                name="unit_health_between_0_and_100",
            ),
            models.CheckConstraint(
                condition=Q(attack_points__gte=0) & Q(attack_points__lte=50),
                name="unit_attack_between_0_and_50",
            ),
        ]

    def __str__(self):
        return f"{self.name} — {self.unit_type} ({self.team})"


class Fight(models.Model):
    # Fighter order matters: fighter_one takes the first turn.
    fighter_one = models.ForeignKey(
        Unit, related_name="fights_as_first", on_delete=models.PROTECT,
    )
    fighter_two = models.ForeignKey(
        Unit, related_name="fights_as_second", on_delete=models.PROTECT,
    )
    winner = models.ForeignKey(
        Unit, null=True, blank=True, related_name="fights_won",
        on_delete=models.PROTECT,
    )
    is_draw = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(fighter_one=F("fighter_two")),
                name="fight_two_different_units",
            ),
        ]

    @property
    def result(self):
        if self.winner_id:
            return f"Winner: {self.winner.name} ({self.winner.team})"
        return "Draw" if self.is_draw else "Not finished"

    def __str__(self):
        return f"Fight #{self.pk}: {self.fighter_one.name} vs {self.fighter_two.name}"


class AttackEvent(models.Model):
    """Immutable snapshot of one simulated attack in a fight."""
    fight = models.ForeignKey(Fight, related_name="events", on_delete=models.CASCADE)
    turn_number = models.PositiveIntegerField()
    attacker = models.ForeignKey(
        Unit, related_name="attacks_made", on_delete=models.PROTECT,
    )
    defender = models.ForeignKey(
        Unit, related_name="attacks_received", on_delete=models.PROTECT,
    )
    rolled_points = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
    )
    damage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
    )
    attacker_health = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    defender_health = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        ordering = ["turn_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["fight", "turn_number"], name="fight_unique_turn_number",
            )
        ]

    def __str__(self):
        return f"Turn {self.turn_number}: {self.attacker.name} dealt {self.damage}"

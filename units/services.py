"""Fight logic separated from HTTP views, making it easy to test."""

import random
from django.db import transaction
from django.utils import timezone

from .models import AttackEvent, Fight, Unit

# Prevent an infinite simulation if random always returns zero.
MAX_ATTACKS = 2000


class InvalidFight(ValueError):
    pass


@transaction.atomic
def simulate_fight(first_id, second_id):
    if first_id == second_id:
        raise InvalidFight("Choose two different fighters.")

    # Lock rows in a consistent order where the database supports it.
    found = {
        unit.pk: unit for unit in Unit.objects.select_for_update()
        .filter(pk__in=(first_id, second_id)).order_by("pk")
    }
    if first_id not in found or second_id not in found:
        raise InvalidFight("One of the fighters no longer exists.")
    first = found[first_id]
    second = found[second_id]

    if first.team == second.team:
        raise InvalidFight("The fighters must be on different teams.")
    if first.health == 0 or second.health == 0:
        raise InvalidFight("Both fighters need health above zero. Heal them first.")

    fight = Fight.objects.create(fighter_one=first, fighter_two=second)
    winner = None
    is_draw = True
    # If both attack values are 0, record one turn for each and finish in a draw.
    limit = 2 if first.attack_points == second.attack_points == 0 else MAX_ATTACKS

    for turn in range(1, limit + 1):
        attacker, defender = (first, second) if turn % 2 else (second, first)
        rolled = random.randint(0, attacker.attack_points)
        actual_damage = min(rolled, defender.health)
        defender.health -= actual_damage

        AttackEvent.objects.create(
            fight=fight,
            turn_number=turn,
            attacker=attacker,
            defender=defender,
            rolled_points=rolled,
            damage=actual_damage,
            attacker_health=attacker.health,
            defender_health=defender.health,
        )

        if defender.health == 0:
            winner = attacker
            is_draw = False
            break

    first.save(update_fields=["health"])
    second.save(update_fields=["health"])
    fight.winner = winner
    fight.is_draw = is_draw
    fight.finished_at = timezone.now()
    fight.save(update_fields=["winner", "is_draw", "finished_at"])
    return fight

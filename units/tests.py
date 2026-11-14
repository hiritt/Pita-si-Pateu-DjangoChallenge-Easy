from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse

from .models import AttackEvent, Fight, Unit
from .services import InvalidFight, simulate_fight


def make_unit(name="Aster", team="Blue", health=100, attack_points=35, **overrides):
    return Unit.objects.create(
        name=name, team=team, unit_type="Knight", health=health,
        attack_points=attack_points,
        profile_image_link="https://example.com/fighter.png", **overrides,
    )


class UnitFormTests(TestCase):
    def valid_data(self, **overrides):
        return {
            "name": "Aster", "unit_type": "Knight", "team": "Blue",
            "health": 100, "attack_points": 35,
            "profile_image_link": "https://example.com/fighter.png",
            **overrides,
        }

    def test_get_unit_form(self):
        response = self.client.get("/unit")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add a fighter unit")

    def test_valid_post_saves_unit(self):
        response = self.client.post("/unit", self.valid_data(), follow=True)
        self.assertEqual(Unit.objects.count(), 1)
        self.assertContains(response, "Fighter unit added successfully!")

    def test_default_health_100(self):
        self.assertEqual(Unit._meta.get_field("health").default, 100)

    def test_blank_health_uses_default_100(self):
        self.client.post("/unit", self.valid_data(health=""))
        self.assertEqual(Unit.objects.get().health, 100)

    def test_health_bounds(self):
        for value in (-1, 101):
            response = self.client.post("/unit", self.valid_data(health=value))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Unit.objects.count(), 0)
            self.assertTrue(response.context["form"].errors)

    def test_attack_bounds(self):
        for value in (-1, 51):
            response = self.client.post("/unit", self.valid_data(attack_points=value))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Unit.objects.count(), 0)
            self.assertTrue(response.context["form"].errors)

    def test_invalid_options_or_url(self):
        for overrides in (
            {"unit_type": "Dragon"}, {"team": "Green"},
            {"profile_image_link": "not-a-url"}, {"name": "   "},
        ):
            response = self.client.post("/unit", self.valid_data(**overrides))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Unit.objects.count(), 0)
            self.assertTrue(response.context["form"].errors)


class FighterPagesTests(TestCase):
    def test_list_and_details(self):
        unit = make_unit()
        listing = self.client.get("/unit/all")
        self.assertContains(listing, unit.name)
        self.assertContains(listing, 'width="50"')
        detail = self.client.get(f"/unit/{unit.pk}")
        self.assertContains(detail, "AttackPoints")
        self.assertContains(detail, unit.name)

    def test_healing_is_post_only_and_persisted(self):
        unit = make_unit(health=30)
        url = reverse("unit_heal", args=[unit.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        unit.refresh_from_db()
        self.assertEqual(unit.health, 100)
        self.assertContains(response, "healed to 100 HP")


class FightTests(TestCase):
    def setUp(self):
        self.blue = make_unit(name="Blue one", team="Blue", health=100)
        self.red = make_unit(name="Red one", team="Red", health=30)

    def test_same_team_rejected(self):
        blue2 = make_unit(name="Blue two", team="Blue")
        response = self.client.post(reverse("simulate"), {
            "fighter_one": self.blue.pk, "fighter_two": blue2.pk,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Fight.objects.count(), 0)
        self.assertContains(response, "different teams", status_code=400)

    def test_same_unit_rejected(self):
        response = self.client.post(reverse("simulate"), {
            "fighter_one": self.blue.pk, "fighter_two": self.blue.pk,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Fight.objects.count(), 0)

    def test_zero_health_cannot_fight(self):
        self.red.health = 0
        self.red.save(update_fields=["health"])
        response = self.client.post(reverse("simulate"), {
            "fighter_one": self.blue.pk, "fighter_two": self.red.pk,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Fight.objects.count(), 0)

    @patch("units.services.random.randint", return_value=50)
    def test_fight_history_and_winner(self, _randint):
        response = self.client.post(reverse("simulate"), {
            "fighter_one": self.blue.pk, "fighter_two": self.red.pk,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        fight = Fight.objects.get()
        self.assertEqual(fight.winner, self.blue)
        self.assertFalse(fight.is_draw)
        self.red.refresh_from_db()
        self.assertEqual(self.red.health, 0)
        event = fight.events.get()
        self.assertEqual(event.turn_number, 1)
        self.assertEqual(event.rolled_points, 50)
        self.assertEqual(event.damage, 30)  # Cap damage to remaining health.
        self.assertEqual(event.attacker_health, 100)
        self.assertEqual(event.defender_health, 0)
        self.assertContains(response, "Fight #")
        self.assertContains(response, "Winner:")
        stats = self.client.get("/unit/all").context["stats"]
        blue_stats = stats[0]
        red_stats = stats[1]
        self.assertEqual(blue_stats["fights"], 1)
        self.assertEqual(red_stats["fights"], 1)
        self.assertEqual(blue_stats["damage_caused"], 30)
        self.assertEqual(red_stats["damage_taken"], 30)
        self.assertEqual(blue_stats["damage_taken"], 0)

    def test_zero_attack_both_results_in_draw(self):
        self.blue.attack_points = 0
        self.red.attack_points = 0
        self.blue.save(update_fields=["attack_points"])
        self.red.save(update_fields=["attack_points"])
        fight = simulate_fight(self.blue.pk, self.red.pk)
        self.assertTrue(fight.is_draw)
        self.assertIsNone(fight.winner)
        self.assertEqual(fight.events.count(), 2)
        self.assertEqual(AttackEvent.objects.filter(damage=0).count(), 2)

    @patch("units.services.random.randint", return_value=0)
    def test_no_damage_does_not_loop_forever(self, _randint):
        with patch("units.services.MAX_ATTACKS", 4):
            fight = simulate_fight(self.blue.pk, self.red.pk)
        self.assertTrue(fight.is_draw)
        self.assertEqual(fight.events.count(), 4)

    @patch("units.services.random.randint", side_effect=[0, 30])
    def test_fighter_order_alternates(self, _randint):
        self.blue.attack_points = 0
        self.blue.health = 25
        self.red.attack_points = 30
        self.blue.save(update_fields=["attack_points", "health"])
        self.red.save(update_fields=["attack_points"])
        fight = simulate_fight(self.blue.pk, self.red.pk)
        events = list(fight.events.all())
        self.assertEqual([step.attacker_id for step in events], [self.blue.pk, self.red.pk])
        self.assertEqual([step.damage for step in events], [0, 25])
        self.assertEqual(fight.winner_id, self.red.pk)

    def test_service_rejects_invalid_team(self):
        blue2 = make_unit(name="Blue two", team="Blue")
        with self.assertRaises(InvalidFight):
            simulate_fight(self.blue.pk, blue2.pk)

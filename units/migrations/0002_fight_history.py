from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [("units", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Fight",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_draw", models.BooleanField(default=False)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("fighter_one", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="fights_as_first", to="units.unit")),
                ("fighter_two", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="fights_as_second", to="units.unit")),
                ("winner", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="fights_won", to="units.unit")),
            ],
            options={"ordering": ["-started_at", "-id"]},
        ),
        migrations.AddConstraint(
            model_name="fight",
            constraint=models.CheckConstraint(
                condition=~models.Q(fighter_one=models.F("fighter_two")),
                name="fight_two_different_units",
            ),
        ),
        migrations.CreateModel(
            name="AttackEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("turn_number", models.PositiveIntegerField()),
                ("rolled_points", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(50)])),
                ("damage", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(50)])),
                ("attacker_health", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("defender_health", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("attacker", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attacks_made", to="units.unit")),
                ("defender", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attacks_received", to="units.unit")),
                ("fight", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="units.fight")),
            ],
            options={"ordering": ["turn_number"]},
        ),
        migrations.AddConstraint(
            model_name="attackevent",
            constraint=models.UniqueConstraint(fields=("fight", "turn_number"), name="fight_unique_turn_number"),
        ),
    ]

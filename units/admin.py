from django.contrib import admin
from .models import AttackEvent, Fight, Unit

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "unit_type", "team", "health", "attack_points")
    list_filter = ("team", "unit_type")

class AttackInline(admin.TabularInline):
    model = AttackEvent
    extra = 0
    readonly_fields = (
        "turn_number", "attacker", "defender", "rolled_points", "damage",
        "attacker_health", "defender_health",
    )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Fight)
class FightAdmin(admin.ModelAdmin):
    list_display = ("id", "fighter_one", "fighter_two", "winner", "is_draw", "started_at")
    inlines = [AttackInline]

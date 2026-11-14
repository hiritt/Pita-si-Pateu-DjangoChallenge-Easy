from django.contrib import messages
from django.db import DatabaseError, transaction
from django.db.models import Q, Sum
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .forms import FightSelectionForm, UnitForm
from .models import AttackEvent, Fight, Unit
from .services import InvalidFight, simulate_fight


def add_unit(request):
    if request.method == "POST":
        form = UnitForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except DatabaseError:
                form.add_error(None, "The fighter could not be saved. Please try again.")
            else:
                messages.success(request, "Fighter unit added successfully!")
                return redirect("unit")
    elif request.method == "GET":
        form = UnitForm(initial={"health": 100})
    else:
        return HttpResponseNotAllowed(["GET", "POST"])
    return render(request, "units/unit_form.html", {"form": form})


def _list_page(request, fight_form=None, *, status=200):
    units = Unit.objects.all()
    form = fight_form if fight_form is not None else FightSelectionForm()
    stats = []
    for team, label in Unit.Team.choices:
        stats.append({
            "team": label,
            "fights": Fight.objects.filter(
                Q(fighter_one__team=team) | Q(fighter_two__team=team)
            ).count(),
            "damage_caused": AttackEvent.objects.filter(
                attacker__team=team
            ).aggregate(total=Sum("damage"))["total"] or 0,
            "damage_taken": AttackEvent.objects.filter(
                defender__team=team
            ).aggregate(total=Sum("damage"))["total"] or 0,
        })
    return render(request, "units/unit_list.html", {
        "units": units, "fight_form": form, "stats": stats,
    }, status=status)


@require_GET
def all_units(request):
    return _list_page(request)


@require_GET
def unit_detail(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id)
    fights = (Fight.objects.filter(
        Q(fighter_one=unit) | Q(fighter_two=unit)
    ).select_related("fighter_one", "fighter_two", "winner")
      .prefetch_related("events__attacker", "events__defender"))
    return render(request, "units/unit_detail.html", {"unit": unit, "fights": fights})


@require_POST
def heal_unit(request, unit_id):
    with transaction.atomic():
        unit = get_object_or_404(Unit.objects.select_for_update(), pk=unit_id)
        if unit.health < 100:
            unit.health = 100
            unit.save(update_fields=["health"])
            messages.success(request, f"{unit.name} was healed to 100 HP.")
        else:
            messages.info(request, f"{unit.name} already has full health.")
    return redirect("unit_all")


@require_POST
def simulate(request):
    form = FightSelectionForm(request.POST)
    if not form.is_valid():
        return _list_page(request, form, status=400)
    first = form.cleaned_data["fighter_one"]
    second = form.cleaned_data["fighter_two"]
    try:
        fight = simulate_fight(first.pk, second.pk)
    except InvalidFight as error:
        form.add_error(None, str(error))
        return _list_page(request, form, status=400)
    except DatabaseError:
        form.add_error(None, "The fight could not be saved. Please try again.")
        return _list_page(request, form, status=500)
    messages.success(request, f"Fight #{fight.pk} complete: {fight.result}")
    return redirect(reverse("unit_detail", args=[first.pk]) + f"#fight-{fight.pk}")

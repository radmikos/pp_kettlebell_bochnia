from django.shortcuts import get_object_or_404, render

from .models import (
    Category,
    KBSquatResult,
    OverallResult,
    Player,
    SeeSawPressResult,
    SnatchResult,
    TGUResult,
)


def create_or_update_results(category):
    for player in Player.objects.filter(categories=category):
        # Snatch
        if player.snatch_results() is not None:
            SnatchResult.objects.update_or_create(
                player=player, defaults={"result": player.snatch_results()}
            )

        # TGU
        if player.tgu_body_percent_weight() is not None:
            TGUResult.objects.update_or_create(
                player=player, defaults={"result": player.tgu_body_percent_weight()}
            )

        # See Saw Press
        if player.see_saw_press_body_percent_weight() is not None:
            SeeSawPressResult.objects.update_or_create(
                player=player,
                defaults={"result": player.see_saw_press_body_percent_weight()},
            )

        # KB Squat
        if player.kb_squat_body_percent_weight() is not None:
            KBSquatResult.objects.update_or_create(
                player=player,
                defaults={"result": player.kb_squat_body_percent_weight()},
            )


def calculate_positions(result_model, category):
    results = result_model.objects.filter(player__categories=category).order_by(
        "-result"
    )
    for position, result in enumerate(results, start=1):
        result.position = position
        result.save()


def update_overall_results(category):
    for player in Player.objects.filter(categories=category):
        overall, created = OverallResult.objects.get_or_create(player=player)

        snatch_results = SnatchResult.objects.filter(player=player).first()
        overall.snatch_points = snatch_results.position if snatch_results else 0

        tgu_result = TGUResult.objects.filter(player=player).first()
        overall.tgu_points = tgu_result.position if tgu_result else 0

        see_saw_result = SeeSawPressResult.objects.filter(player=player).first()
        overall.see_saw_press_points = see_saw_result.position if see_saw_result else 0

        kb_squat_result = KBSquatResult.objects.filter(player=player).first()
        overall.kb_squat_points = kb_squat_result.position if kb_squat_result else 0

        overall.calculate_total_points()
        overall.save()


def index(request):
    categories = Category.objects.all()
    return render(request, "index.html", {"categories": categories})


from django.shortcuts import render

from .models import Category, OverallResult, Player


def category_view(request, category_slug):
    category_mapping = {
        "amator-kobiety-do-65kg": "Amator_Kobiety_do_65kg",
        "amator-kobiety-powyzej-65kg": "Amator_Kobiety_powyżej_65kg",
        "amator-mezczyzni-do-85kg": "Amator_Mężczyźni_do_85kg",
        "amator-mezczyzni-powyzej-85kg": "Amator_Mężczyźni_powyżej_85kg",
        "masters-kobiety": "Masters_Kobiety",
        "masters-mezczyzni": "Masters_Mężczyźni",
        "najlepsza-bochnianka": "Najlepsza_Bochnianka",
        "najlepszy-bochnianin": "Najlepszy_Bochnianin",
        "pro-kobiety": "Pro_Kobiety",
        "pro-mezczyzni-do-85kg": "Pro_Mężczyźni_do_85kg",
        "pro-mezczyzni-powyzej-85kg": "Pro_Mężczyźni_powyżej_85kg",
    }

    category_name = category_mapping.get(category_slug)
    if not category_name:
        return render(request, "404.html", status=404)

    category = Category.objects.get(name=category_name)
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )

    context = {
        "category_name": category_name,
        "results": results,
    }

    return render(request, "category_template.html", context)


from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Value
from django.db.models.functions import Coalesce, Greatest
from django.shortcuts import render

from .models import (
    BestSeeSawPressResult,
    Category,
    KBSquatResult,
    OverallResult,
    Player,
    SeeSawPressResult,
    SnatchResult,
    TGUResult,
)
from django.shortcuts import render
from django.db.models import F, ExpressionWrapper, FloatField
from django.db.models.functions import Greatest
from .models import Category, Player, SnatchResult, TGUResult, SeeSawPressResult, KBSquatResult


def amator_kobiety_do_65kg(request):
    category = Category.objects.get(name='Amator_Kobiety_do_65kg')
    players = Player.objects.filter(categories=category)

    # Calculate positions for Snatch
    snatch_results = SnatchResult.objects.filter(player__in=players).order_by('-result')
    for position, result in enumerate(snatch_results, 1):
        result.position = position
        result.save()

    # Calculate positions for TGU
    tgu_results = TGUResult.objects.filter(player__in=players).order_by('-result')
    for position, result in enumerate(tgu_results, 1):
        result.position = position
        result.save()

    # Calculate positions for See Saw Press
    see_saw_results = SeeSawPressResult.objects.filter(player__in=players)
    see_saw_results = sorted(see_saw_results, key=lambda x: x.get_max_result(), reverse=True)
    for position, result in enumerate(see_saw_results, 1):
        result.position = position
        result.save()

    # Calculate positions for KB Squat
    kb_squat_results = KBSquatResult.objects.filter(player__in=players).order_by('-result')
    for position, result in enumerate(kb_squat_results, 1):
        result.position = position
        result.save()

    # Calculate overall results
    overall_results = []
    for player in players:
        snatch_points = getattr(SnatchResult.objects.filter(player=player).first(), 'position', 0)
        tgu_points = getattr(TGUResult.objects.filter(player=player).first(), 'position', 0)
        see_saw_points = getattr(SeeSawPressResult.objects.filter(player=player).first(), 'position', 0)
        kb_squat_points = getattr(KBSquatResult.objects.filter(player=player).first(), 'position', 0)

        total_points = snatch_points + tgu_points + see_saw_points + kb_squat_points

        overall_results.append({
            'player': player,
            'weight': player.weight,
            'snatch_place': snatch_points,
            'tgu_place': tgu_points,
            'press_place': see_saw_points,
            'squat_place': kb_squat_points,
            'total_points': total_points,
            'tiebreak': player.tiebreak
        })

    # Sort overall results
    overall_results.sort(key=lambda x: x['total_points'])

    # Assign final positions and calculate final scores
    for position, result in enumerate(overall_results, 1):
        result['total_place'] = position
        result['final_score'] = result['total_points'] - 0.5 if result['tiebreak'] else result['total_points']

    context = {
        'category_name': 'Amator Kobiety do 65kg',
        'overall_results': overall_results,
        'snatch_results': [
            {
                'position': result.position,
                'player': result.player,
                'weight': result.player.weight,
                'snatch_kettlebell_weight': result.player.snatch_kettlebell_weight,
                'snatch_repetitions': result.player.snatch_repetitions,
                'max_result': result.result,
                'bw_percentage': round((result.player.snatch_kettlebell_weight / result.player.weight) * 100,
                                       2) if result.player.weight and result.player.snatch_kettlebell_weight else None
            } for result in snatch_results
        ],
        'tgu_results': [
            {
                'position': result.position,
                'player': result.player,
                'weight': result.player.weight,
                'max_result': result.result,
                'bw_percentage': round(result.result, 2)
            } for result in tgu_results
        ],
        'see_saw_results': [
            {
                'position': result.position,
                'player': result.player,
                'weight': result.player.weight,
                'attempt_1': f"{result.result_left_1}/{result.result_right_1}",
                'attempt_2': f"{result.result_left_2}/{result.result_right_2}",
                'attempt_3': f"{result.result_left_3}/{result.result_right_3}",
                'max_result': result.get_max_result(),
                'bw_percentage': round((result.get_max_result() / result.player.weight) * 100,
                                       2) if result.player.weight and result.get_max_result() else None
            } for result in see_saw_results
        ],
        'kb_squat_results': [
            {
                'position': result.position,
                'player': result.player,
                'weight': result.player.weight,
                'max_result': result.result,
                'bw_percentage': round(result.result, 2)
            } for result in kb_squat_results
        ],
    }

    return render(request, 'amator-kobiety-do-65kg.html', context)


def amator_kobiety_powyzej_65kg(request):
    category = Category.objects.get(name="Amator_Kobiety_powyżej_65kg")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "amator-kobiety-powyzej-65kg.html", {"results": results})


def amator_mezczyzni_do_85kg(request):
    category = Category.objects.get(name="Pro_Mężczyźni_powyżej_85kg")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "pro_mezczyzni_powyzej_85kg.html", {"results": results})


def amator_mezczyzni_powyzej_85kg(request):
    category = Category.objects.get(name="Amator_Kobiety_do_65kg")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "amator-kobiety-do-65kg.html", {"results": results})


def masters_kobiety(request):
    category = Category.objects.get(name="Amator_Kobiety_powyżej_65kg")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "amator-kobiety-powyzej-65kg.html", {"results": results})


# Utwórz podobne funkcje dla pozostałych kategorii...


def masters_mezczyzni(request):
    category = Category.objects.get(name="Pro_Mężczyźni_powyżej_85kg")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "pro_mezczyzni_powyzej_85kg.html", {"results": results})


def najlepsza_bochnianka(request):
    category = Category.objects.get(name="Amator_Kobiety_do_65kg")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "amator-kobiety-do-65kg.html", {"results": results})


def najlepszy_bochnianin(request):
    category = Category.objects.get(name="Amator_Kobiety_powyżej_65kg")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "amator-kobiety-powyzej-65kg.html", {"results": results})


# Utwórz podobne funkcje dla pozostałych kategorii...


def pro_kobiety(request):
    category = Category.objects.get(name="Pro_Mężczyźni_powyżej_85kg")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "pro_mezczyzni_powyzej_85kg.html", {"results": results})


def pro_mezczyzni_do_85kg(request):
    category = Category.objects.get(name="Amator_Kobiety_do_65kg")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "amator-kobiety-do-65kg.html", {"results": results})


def pro_mezczyzni_powyzej_85kg(request):
    category = Category.objects.get(name="Pro_Mężczyźni_powyżej_85kg")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "pro-mezczyzni-powyzej-85kg.html", {"results": results})


def nagroda_specjalna(request):
    category = Category.objects.get(name="Nagroda_specjalna")
    results = OverallResult.objects.filter(player__categories=category).order_by(
        "final_position"
    )
    return render(request, "nagroda-specjalna.html", {"results": results})

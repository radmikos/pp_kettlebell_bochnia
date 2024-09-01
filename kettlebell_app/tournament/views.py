from django.shortcuts import render, get_object_or_404
from .models import Player, SnatchResult, TGUResult, SeeSawPressResult, KBSquatResult, OverallResult, Category


def create_or_update_results(category):
    for player in Player.objects.filter(categories=category):
        # Snatch
        if player.snatch_results() is not None:
            SnatchResult.objects.update_or_create(
                player=player,
                defaults={'result': player.snatch_results()}
            )

        # TGU
        if player.tgu_body_percent_weight() is not None:
            TGUResult.objects.update_or_create(
                player=player,
                defaults={'result': player.tgu_body_percent_weight()}
            )

        # See Saw Press
        if player.see_saw_press_body_percent_weight() is not None:
            SeeSawPressResult.objects.update_or_create(
                player=player,
                defaults={'result': player.see_saw_press_body_percent_weight()}
            )

        # KB Squat
        if player.kb_squat_body_percent_weight() is not None:
            KBSquatResult.objects.update_or_create(
                player=player,
                defaults={'result': player.kb_squat_body_percent_weight()}
            )


def calculate_positions(result_model, category):
    results = result_model.objects.filter(player__categories=category).order_by('-result')
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
    return render(request, 'index.html', {'categories': categories})


from django.shortcuts import render
from .models import Player, Category, OverallResult


def category_view(request, category_slug):
    category_mapping = {
        'amator-kobiety-do-65kg': 'Amator_Kobiety_do_65kg',
        'amator-kobiety-powyzej-65kg': 'Amator_Kobiety_powyżej_65kg',
        'amator-mezczyzni-do-85kg': 'Amator_Mężczyźni_do_85kg',
        'amator-mezczyzni-powyzej-85kg': 'Amator_Mężczyźni_powyżej_85kg',
        'masters-kobiety': 'Masters_Kobiety',
        'masters-mezczyzni': 'Masters_Mężczyźni',
        'najlepsza-bochnianka': 'Najlepsza_Bochnianka',
        'najlepszy-bochnianin': 'Najlepszy_Bochnianin',
        'pro-kobiety': 'Pro_Kobiety',
        'pro-mezczyzni-do-85kg': 'Pro_Mężczyźni_do_85kg',
        'pro-mezczyzni-powyzej-85kg': 'Pro_Mężczyźni_powyżej_85kg',
    }

    category_name = category_mapping.get(category_slug)
    if not category_name:
        return render(request, '404.html', status=404)

    category = Category.objects.get(name=category_name)
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')

    context = {
        'category_name': category_name,
        'results': results,
    }

    return render(request, 'category_template.html', context)


from django.shortcuts import render
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from .models import Category, Player, OverallResult, SnatchResult, TGUResult, SeeSawPressResult, KBSquatResult


def amator_kobiety_do_65kg(request):
    category = Category.objects.get(name='Amator_Kobiety_do_65kg')
    players = Player.objects.filter(categories=category)

    # Create default results for all players
    for player in players:
        OverallResult.objects.get_or_create(player=player, defaults={'total_points': 0})
        SnatchResult.objects.get_or_create(player=player, defaults={'result': 0})
        TGUResult.objects.get_or_create(player=player, defaults={'result': 0})
        SeeSawPressResult.objects.get_or_create(player=player, defaults={'result_left': 0, 'result_right': 0})
        KBSquatResult.objects.get_or_create(player=player, defaults={'result': 0})

    overall_results = OverallResult.objects.filter(player__in=players).order_by(
        F('total_points').desc(nulls_last=True), 'player__surname'
    )

    snatch_results = SnatchResult.objects.filter(player__in=players).order_by(
        F('result').desc(nulls_last=True), 'player__surname'
    )

    tgu_results = TGUResult.objects.filter(player__in=players).order_by(
        F('result').desc(nulls_last=True), 'player__surname'
    )

    see_saw_results = SeeSawPressResult.objects.filter(player__in=players).order_by(
        (F('result_left') + F('result_right')).desc(nulls_last=True), 'player__surname'
    )

    kb_squat_results = KBSquatResult.objects.filter(player__in=players).order_by(
        F('result').desc(nulls_last=True), 'player__surname'
    )

    context = {
        'category_name': 'Amator Kobiety do 65kg',
        'overall_results': overall_results,
        'snatch_results': snatch_results,
        'tgu_results': tgu_results,
        'see_saw_results': see_saw_results,
        'kb_squat_results': kb_squat_results,
    }

    return render(request, 'amator-kobiety-do-65kg.html', context)


def amator_kobiety_powyzej_65kg(request):
    category = Category.objects.get(name='Amator_Kobiety_powyżej_65kg')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'amator-kobiety-powyzej-65kg.html', {'results': results})


def amator_mezczyzni_do_85kg(request):
    category = Category.objects.get(name='Pro_Mężczyźni_powyżej_85kg')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'pro_mezczyzni_powyzej_85kg.html', {'results': results})


def amator_mezczyzni_powyzej_85kg(request):
    category = Category.objects.get(name='Amator_Kobiety_do_65kg')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'amator-kobiety-do-65kg.html', {'results': results})


def masters_kobiety(request):
    category = Category.objects.get(name='Amator_Kobiety_powyżej_65kg')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'amator-kobiety-powyzej-65kg.html', {'results': results})


# Utwórz podobne funkcje dla pozostałych kategorii...

def masters_mezczyzni(request):
    category = Category.objects.get(name='Pro_Mężczyźni_powyżej_85kg')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'pro_mezczyzni_powyzej_85kg.html', {'results': results})


def najlepsza_bochnianka(request):
    category = Category.objects.get(name='Amator_Kobiety_do_65kg')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'amator-kobiety-do-65kg.html', {'results': results})


def najlepszy_bochnianin(request):
    category = Category.objects.get(name='Amator_Kobiety_powyżej_65kg')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'amator-kobiety-powyzej-65kg.html', {'results': results})


# Utwórz podobne funkcje dla pozostałych kategorii...

def pro_kobiety(request):
    category = Category.objects.get(name='Pro_Mężczyźni_powyżej_85kg')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'pro_mezczyzni_powyzej_85kg.html', {'results': results})


def pro_mezczyzni_do_85kg(request):
    category = Category.objects.get(name='Amator_Kobiety_do_65kg')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'amator-kobiety-do-65kg.html', {'results': results})


def pro_mezczyzni_powyzej_85kg(request):
    category = Category.objects.get(name='Pro_Mężczyźni_powyżej_85kg')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'pro-mezczyzni-powyzej-85kg.html', {'results': results})

def nagroda_specjalna(request):
    category = Category.objects.get(name='Nagroda_specjalna')
    results = OverallResult.objects.filter(player__categories=category).order_by('final_position')
    return render(request, 'nagroda-specjalna.html', {'results': results})
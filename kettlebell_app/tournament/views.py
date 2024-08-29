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

def category_results(request, category_name):
    category = get_object_or_404(Category, name=category_name)

    create_or_update_results(category)
    calculate_positions(SnatchResult, category)
    calculate_positions(TGUResult, category)
    calculate_positions(SeeSawPressResult, category)
    calculate_positions(KBSquatResult, category)
    update_overall_results(category)

    overall_results = OverallResult.objects.filter(player__categories=category).order_by('total_points')
    snatch_results = SnatchResult.objects.filter(player__categories=category).order_by('position')
    tgu_results = TGUResult.objects.filter(player__categories=category).order_by('position')
    see_saw_press_results = SeeSawPressResult.objects.filter(player__categories=category).order_by('position')
    kb_squat_results = KBSquatResult.objects.filter(player__categories=category).order_by('position')

    context = {
        'category': category,
        'overall_results': overall_results,
        'snatch_results': snatch_results,
        'tgu_results': tgu_results,
        'see_saw_press_results': see_saw_press_results,
        'kb_squat_results': kb_squat_results,
    }
    return render(request, 'category_results.html', context)
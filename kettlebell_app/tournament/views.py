from django.shortcuts import render

from .forms import StationForm
from .models import (Category, KBSquatResult, OverallResult, PistolSquatResult,
                     Player, SeeSawPressResult, SnatchResult, TGUResult)


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
    disciplines = category.get_disciplines()
    for player in Player.objects.filter(categories=category):
        overall, created = OverallResult.objects.get_or_create(player=player)

        if "snatch" in disciplines:
            snatch_results = SnatchResult.objects.filter(player=player).first()
            overall.snatch_points = snatch_results.position if snatch_results else 0
        else:
            overall.snatch_points = 0

        overall.calculate_total_points()
        overall.save()


def index(request):
    categories = Category.objects.all()
    return render(request, "index.html", {"categories": categories})


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


def calculate_category_results(request, category_name, template_name):
    category = Category.objects.get(name=category_name)
    players = Player.objects.filter(categories=category)
    disciplines = category.get_disciplines()

    discipline_configs = {
        "snatch": {
            "model": SnatchResult,
            "calculate": lambda player, result: {
                "max_result": result.result or 0,
                "bw_percentage": round(
                    (player.snatch_kettlebell_weight / player.weight) * 100, 2
                )
                if player.weight and player.snatch_kettlebell_weight
                else 0,
                "kettlebell_weight": player.snatch_kettlebell_weight,
                "repetitions": player.snatch_repetitions,
            },
        },
        "tgu": {
            "model": TGUResult,
            "calculate": lambda player, result: {
                "max_result": result.get_max_result(),
                "bw_percentage": round(result.calculate_bw_percentage(), 2),
                "attempt_1": result.result_1,
                "attempt_2": result.result_2,
                "attempt_3": result.result_3,
            },
        },
        "see_saw_press": {
            "model": SeeSawPressResult,
            "calculate": lambda player, result: {
                "max_result": result.get_max_result(),
                "bw_percentage": round(
                    (result.get_max_result() / player.weight) * 100, 1
                )
                if player.weight
                else 0,
                "attempt_1": f"{result.result_left_1:.1f}/{result.result_right_1:.1f}",
                "attempt_2": f"{result.result_left_2:.1f}/{result.result_right_2:.1f}",
                "attempt_3": f"{result.result_left_3:.1f}/{result.result_right_3:.1f}",
            },
        },
        "kb_squat": {
            "model": KBSquatResult,
            "calculate": lambda player, result: {
                "max_result": result.get_max_result(),
                "bw_percentage": round(
                    (result.get_max_result() / player.weight) * 100, 1
                )
                if player.weight
                else 0,
                "attempt_1": f"{result.result_left_1:.1f}/{result.result_right_1:.1f}",
                "attempt_2": f"{result.result_left_2:.1f}/{result.result_right_2:.1f}",
                "attempt_3": f"{result.result_left_3:.1f}/{result.result_right_3:.1f}",
            },
        },
        "pistol_squat": {
            "model": PistolSquatResult,
            "calculate": lambda player, result: {
                "max_result": result.get_max_result(),
                "bw_percentage": round(result.calculate_bw_percentage(), 2),
                "attempt_1": result.result_1,
                "attempt_2": result.result_2,
                "attempt_3": result.result_3,
            },
        },
    }

    results = {discipline: [] for discipline in disciplines}
    overall_results = []

    for player in players:
        player_results = {"player": player, "weight": player.weight}
        total_points = 0

        for discipline in disciplines:
            config = discipline_configs.get(discipline)
            if config:
                result = config["model"].objects.filter(player=player).first()
                if result:
                    try:
                        discipline_result = {
                            "player": player,
                            "weight": player.weight,
                            **config["calculate"](player, result),
                        }
                        results[discipline].append(discipline_result)
                    except Exception as e:
                        print(
                            f"Error calculating results for {player} in {discipline}: {e}"
                        )
                        player_results[f"{discipline}_place"] = 0
                else:
                    player_results[f"{discipline}_place"] = 0
            else:
                player_results[f"{discipline}_place"] = 0

        overall_results.append(player_results)

    for discipline in disciplines:
        results[discipline].sort(key=lambda x: x["max_result"], reverse=True)
        for position, result in enumerate(results[discipline], 1):
            result["position"] = position
            for overall_result in overall_results:
                if overall_result["player"] == result["player"]:
                    overall_result[f"{discipline}_place"] = position
                    overall_result["total_points"] = (
                        overall_result.get("total_points", 0) + position
                    )

    overall_results.sort(key=lambda x: x.get("total_points", 0))
    for position, result in enumerate(overall_results, 1):
        result["total_place"] = position
        result["final_score"] = (
            result.get("total_points", 0) - 0.5
            if result["player"].tiebreak
            else result.get("total_points", 0)
        )

    context = {
        "category_name": category_name,
        "overall_results": overall_results,
        "disciplines": disciplines,
        "snatch_results": results.get("snatch", []),
        "tgu_results": results.get("tgu", []),
        "see_saw_results": results.get("see_saw_press", []),
        "kb_squat_results": results.get("kb_squat", []),
        "pistol_squat_results": results.get("pistol_squat", []),
    }

    return render(request, template_name, context)


def amator_kobiety_do_65kg(request):
    return calculate_category_results(
        request, "Amator_Kobiety_do_65kg", "amator-kobiety-do-65kg.html"
    )


def amator_kobiety_powyzej_65kg(request):
    return calculate_category_results(
        request, "Amator_Kobiety_powyżej_65kg", "amator-kobiety-powyzej-65kg.html"
    )


def amator_mezczyzni_do_85kg(request):
    return calculate_category_results(
        request, "Amator_Mężczyźni_do_85kg", "amator-mezczyzni-do-85kg.html"
    )


def amator_mezczyzni_powyzej_85kg(request):
    return calculate_category_results(
        request, "Amator_Mężczyźni_powyżej_85kg", "amator-mezczyzni-powyzej-85kg.html"
    )


def masters_kobiety(request):
    return calculate_category_results(
        request, "Masters_Kobiety", "masters-kobiety.html"
    )


def masters_mezczyzni(request):
    return calculate_category_results(
        request, "Masters_Mężczyźni", "masters-mezczyzni.html"
    )


def najlepsza_bochnianka(request):
    return calculate_category_results(
        request, "Najlepsza_Bochnianka", "najlepsza-bochnianka.html"
    )


def najlepszy_bochnianin(request):
    return calculate_category_results(
        request, "Najlepszy_Bochnianin", "najlepszy-bochnianin.html"
    )


def pro_kobiety(request):
    return calculate_category_results(request, "Pro_Kobiety", "pro-kobiety.html")


def pro_mezczyzni_do_85kg(request):
    return calculate_category_results(
        request, "Pro_Mężczyźni_do_85kg", "pro-mezczyzni-do-85kg.html"
    )


def pro_mezczyzni_powyzej_85kg(request):
    return calculate_category_results(
        request, "Pro_Mężczyźni_powyżej_85kg", "pro-mezczyzni-powyzej-85kg.html"
    )


def nagroda_specjalna(request):
    return calculate_category_results(
        request, "Nagroda_specjalna", "nagroda-specjalna.html"
    )


from django.shortcuts import render
from .forms import StationForm
from .models import Player, Category

def generate_start_list(request):
    if request.method == "POST":
        form = StationForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data["category"]
            stations = form.cleaned_data["stations"]

            category = Category.objects.get(name=category_name)
            players = Player.objects.filter(categories=category).order_by('surname', 'name')
            player_count = players.count()

            if stations == 0:
                form.add_error("stations", "Liczba stanowisk musi być większa od 0.")
                return render(request, "station_form.html", {"form": form})

            if player_count == 0:
                return render(
                    request,
                    "start_list.html",
                    {
                        "message": f"Brak zawodników w kategorii {category_name}.",
                        "category": category_name,
                        "stations": stations,
                    },
                )

            players_per_station = (player_count + stations - 1) // stations
            stations_list = [
                {
                    "station_number": i + 1,
                    "players": players[i * players_per_station : (i + 1) * players_per_station],
                }
                for i in range(stations)
            ]

            return render(
                request,
                "start_list.html",
                {
                    "stations_list": stations_list,
                    "stations": stations,
                    "category": category_name,
                },
            )
    else:
        form = StationForm()

    return render(request, "station_form.html", {"form": form})

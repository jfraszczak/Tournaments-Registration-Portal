from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from tournaments.my_functions import *

from tournaments import models
import datetime
from django.db import transaction

from itsdangerous import URLSafeTimedSerializer
from django.core.paginator import Paginator

from tournaments.forms import UserForm


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect("http://127.0.0.1:8000/tournamentsPortal/list_of_tournaments")
            return HttpResponse("User not active")
        return render(request, 'tournaments/login.html', {'correct': True, 'info': 'NULL'})
    return render(request, 'tournaments/login.html', {'correct': False, 'info': 'NULL'})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect("http://127.0.0.1:8000/tournamentsPortal/login")


def register(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():

            email = user_form.cleaned_data['email']
            first_name = user_form.cleaned_data['first_name']
            last_name = user_form.cleaned_data['last_name']
            password = user_form.cleaned_data['password']

            if len(password) < 5:
                info = 'Your password must consist of at least 5 characters'
                return render(request, 'tournaments/register.html',
                              {'user_form': user_form, 'info': info, 'error': True})

            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.username = email
            user.is_active = False

            try:
                user.save()
            except:
                info = 'This email is already taken'
                return render(request, 'tournaments/register.html',
                              {'user_form': user_form, 'info': info, 'error': True})

            current_site = get_current_site(request)
            email_subject = 'Activate Your Account'
            message = render_to_string('tournaments/activate_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            send_mail(email_subject, message, 'tournachella_kontakt@o2.pl', [email])

            info = 'We have sent you an email, please confirm your email address to complete registration'
            return render(request, 'tournaments/register.html', {'user_form': user_form, 'info': info, 'error': False})
    else:
        user_form = UserForm()

    return render(request, 'tournaments/register.html', {'user_form': user_form, 'info': 'NULL'})


def activate_account(request, uidb64, token):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect("http://127.0.0.1:8000/tournamentsPortal/list_of_tournaments")
            return HttpResponse("User not active")
        return render(request, 'tournaments/login.html', {'correct': True, 'info': 'NULL'})

    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        info = 'Your account has been activated successfully'
        return render(request, 'tournaments/login.html', {'correct': False, 'info': info})
    else:
        return HttpResponse('Activation link is invalid!')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        s = URLSafeTimedSerializer("my-secret-key")
        token = s.dumps(email)

        user = User.objects.get(username=email)

        current_site = get_current_site(request)
        email_subject = 'Reset Your Password'
        message = render_to_string('tournaments/reset_password.html', {
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })

        print(message)
        send_mail(email_subject, message, 'tournachella_kontakt@o2.pl', [email])

        info = 'Password reset link has been send. Please check your email.'
        return render(request, 'tournaments/forgot_password.html', {'info': info})

    return render(request, 'tournaments/forgot_password.html', {'info': 'NULL'})


def reset_password(request, uidb64, token):
    if request.method == 'POST':
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token) and user.is_active == True:
            password1 = request.POST.get('password_new')
            password2 = request.POST.get('password_confirm')

            if password1 == password2 and len(password1) >= 5:
                user.set_password(password1)
                user.save()
                info = 'Your password has been successfully changed'
                return render(request, 'tournaments/new_password.html', {'info': info, 'error': False})
            elif password1 == password2 and len(password1) < 5:
                info = 'Your password must consist of at least 5 characters'
                return render(request, 'tournaments/new_password.html', {'info': info, 'error': True})
            else:
                info = 'Given passwords are not the same'
                return render(request, 'tournaments/new_password.html', {'info': info, 'error': True})
        else:
            return HttpResponse('This link is inactive')

    return render(request, 'tournaments/new_password.html', {'info': 'NULL'})


def list_of_tournaments(request):
    if request.method == 'GET' and 'tournament' in request.GET:
        tournament_id = request.GET['tournament']
        if tournament_id is not None and tournament_id != '':
            tournament = models.Tournament.objects.get(id=tournament_id)
            sponsors = models.Sponsoring.objects.filter(tournament__id=tournament_id)
            all_sponsors = models.Sponsor.objects.all()

            potential_sponsors = []

            for spon in all_sponsors:
                flag = True
                for our_spon in sponsors:
                    if spon.id == our_spon.sponsor.id:
                        flag = False
                        break
                if flag:
                    potential_sponsors.append(spon)

            if len(potential_sponsors) == 0:
                potential_sponsors = None

            is_organizer = False
            if tournament.organizer == request.user:
                is_organizer = True

            return render(request, 'tournaments/tournament_detailed_info.html',
                          {'tournament': tournament,
                           'all_sponsors': potential_sponsors,
                           'sponsors': sponsors,
                           'logged_in': request.user.is_authenticated,
                           'is_organizer': is_organizer})

    if request.method == 'GET' and 'showDraw' in request.GET:
        tournament = models.Tournament.objects.get(id=request.GET['showDraw'])
        calculate_draw(tournament.id)

        matches = models.Match.objects.filter(tournament__id=tournament.id).order_by('number')
        draw = []
        if tournament.num_of_registered < tournament.limit:
            i = 1
            while 2 ** i <= tournament.num_of_registered:
                i += 1
            i -= 1
            limit = 2 ** i
        else:
            limit = tournament.limit

        tmp = []
        match_index = 0
        for i in range(limit - 1):
            if match_index < len(matches):
                if matches[match_index].number == i + 1:
                    tmp.append(matches[match_index])
                    match_index += 1
                else:
                    tmp.append(None)
            else:
                tmp.append(None)

        matches = tmp[:]
        num = len(matches)

        print(matches)

        i = 1
        previous = 0
        while limit / 2 ** i >= 1:
            print(previous, previous + limit / 2 ** i)
            stage = []
            if previous < num:
                stage = matches[previous:int(previous + limit / 2 ** i)]
                print(stage)
            draw.append(stage)
            previous = int(previous + limit / 2 ** i)
            i += 1
        print(draw)


        return render(request, 'tournaments/draw.html', {'tournament': tournament, 'draw': draw})

    if request.method == 'POST':
        if 'addSponsor' in request.POST:
            tournament_id = request.POST['tournament_info']
            sponsor_id = request.POST['sponsor']

            tournament = models.Tournament.objects.get(id=tournament_id)
            sponsor = models.Sponsor.objects.get(id=sponsor_id)

            sponsoring = models.Sponsoring(tournament=tournament, sponsor=sponsor)
            sponsoring.save()

            return HttpResponseRedirect(
                "http://127.0.0.1:8000/tournamentsPortal/list_of_tournaments/?tournament=" + str(tournament_id))

    if request.method == 'POST':
        if 'register' in request.POST:
            user_license = request.POST['user_license']
            ranking = request.POST['ranking']
            user = request.user
            tournament_id = request.POST['tournament_info']

            with transaction.atomic():
                tournament = models.Tournament.objects.select_for_update().get(id=tournament_id)
                sponsors = models.Sponsoring.objects.filter(tournament__id=tournament_id)
                all_sponsors = models.Sponsor.objects.all()

                error = None
                success = None

                if tournament.num_of_registered + 1 > tournament.limit:
                    error = 'Unfortunately there are not any remaining places for this tournament'
                else:
                    try:
                        participation = models.Participation(tournament=tournament, user=user, license=user_license,
                                                             ranking=ranking)
                        participation.save()
                    except Exception as err:
                        error = str(err)
                        if "tournaments_participation.ranking unique" in error:
                            error = "There cannot be more than one participant with the same ranking"
                        elif "tournaments_participation.license unique" in error:
                            error = "There cannot be more than one participants with the same license number"
                        elif "tournaments_participation.tournaments_participation_tournament_id_user_id_" in error:
                            error = "You have already signed up for this tournament"

                if error is None:
                    tournament.num_of_registered += 1
                    success = 'You have signed up for the tournament successfully'
                    tournament.save()

            potential_sponsors = []

            for spon in all_sponsors:
                flag = True
                for our_spon in sponsors:
                    if spon.id == our_spon.sponsor.id:
                        flag = False
                        break
                if flag:
                    potential_sponsors.append(spon)

            if len(potential_sponsors) == 0:
                potential_sponsors = None

            is_organizer = False
            if tournament.organizer == request.user:
                is_organizer = True

            return render(request, 'tournaments/tournament_detailed_info.html',
                          {'tournament': tournament,
                           'all_sponsors': potential_sponsors,
                           'sponsors': sponsors,
                           'logged_in': request.user.is_authenticated,
                           'is_organizer': is_organizer,
                           'error': error,
                           'success': success})

    if request.method == 'POST':
        if 'addTournament' in request.POST:
            if request.user.is_authenticated:
                name = request.POST['tournament_form_name']
                discipline = request.POST['discipline']
                date = request.POST['date']
                location = request.POST['location']
                deadline = request.POST['deadline']
                limit = request.POST['limit']
                seeded = request.POST['seeded']
                tournament = models.Tournament(name=name, organizer=request.user, discipline=discipline, date=date,
                                               localization=location, deadline=deadline, num_of_seeded=seeded,
                                               limit=limit)
                tournament.save()
                return HttpResponseRedirect(
                    "http://127.0.0.1:8000/tournamentsPortal/list_of_tournaments/?tournament=" + str(tournament.id))

    if request.method == 'POST':
        if 'edit' in request.POST:
            edit_id = request.POST['edit']
        else:
            edit_id = None

        if request.user.is_authenticated:
            if edit_id is not None and edit_id != '':
                name = request.POST['tournament_form_name']
                discipline = request.POST['discipline']
                date = request.POST['date']
                location = request.POST['location']
                deadline = request.POST['deadline']
                limit = request.POST['limit']
                seeded = request.POST['seeded']
                tournament = models.Tournament.objects.get(id=edit_id)
                tournament.name = name
                tournament.discipline = discipline
                tournament.date = date
                tournament.localization = location
                tournament.deadline = deadline
                tournament.limit = limit
                tournament.num_of_seeded = seeded
                tournament.save()
                return HttpResponseRedirect(
                    "http://127.0.0.1:8000/tournamentsPortal/list_of_tournaments/?tournament=" + str(tournament.id))
        else:
            return HttpResponseRedirect("http://127.0.0.1:8000/tournamentsPortal/login")

    today = datetime.date.today()

    tournaments = models.Tournament.objects.filter(date__gte=today).order_by('date')

    paginator = Paginator(tournaments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tournaments/list_of_tournaments.html',
                  {'tournaments': tournaments, 'page_obj': page_obj, 'logged_in': request.user.is_authenticated})


def my_tournaments(request):
    if request.method == 'GET' and 'tournament' in request.GET:
        tournament_id = request.GET['tournament']
        tournament = models.Tournament.objects.get(id=tournament_id)

        return HttpResponseRedirect(
            "http://127.0.0.1:8000/tournamentsPortal/list_of_tournaments/?tournament=" + str(tournament.id))

    today = datetime.date.today()
    tournaments = models.Tournament.objects.filter(date__gte=today).order_by('date')
    my_participations = models.Participation.objects.filter(user=request.user)

    my_matches = models.Match.objects.filter(user1=request.user) | models.Match.objects.filter(user2=request.user)
    my_matches = my_matches.filter(finished=False).order_by('tournament__date')

    info = None
    color = None
    if request.method == 'POST':
        print(request.POST)
        if 'setResult' in request.POST:
            print('elo')
            match_id = request.POST['match_id']
            result = request.POST['result']
            user = request.user

            with transaction.atomic():
                match = models.Match.objects.select_for_update().get(id=match_id)

                if user == match.user1:
                    if result == 'win':
                        seed = match.user1_seed
                        match.user1_decision = match.user1
                    else:
                        seed = match.user2_seed
                        match.user1_decision = match.user2
                else:
                    if result == 'win':
                        seed = match.user2_seed
                        match.user2_decision = match.user2
                    else:
                        seed = match.user1_seed
                        match.user2_decision = match.user1

                match.save()

            info = 'Your opponent still has not declared a winner.'
            color = 'primary'

            if match.user1_decision is not None and match.user2_decision is not None:
                if match.user1_decision == match.user2_decision:
                    match.winner = match.user1_decision
                    match.finished = True
                    match.save()

                    if match.tournament.num_of_registered < match.tournament.limit:
                        i = 1
                        while 2 ** i <= match.tournament.num_of_registered:
                            i += 1
                        i -= 1
                        limit = 2 ** i
                    else:
                        limit = match.tournament.limit

                    new_match_number = next_match(match.number, match.stage, limit)

                    if new_match_number < limit:

                        stage_name = calculate_stage(match.stage + 1, limit)

                        try:
                            new_match = models.Match(tournament=match.tournament, number=new_match_number,
                                                     user1=match.winner, stage=match.stage + 1, stage_name=stage_name,
                                                     user1_seed=seed)
                            new_match.save()
                        except:
                            new_match = models.Match.objects.get(tournament=match.tournament, number=new_match_number)
                            new_match.user2 = match.winner
                            new_match.user2_seed = seed
                            new_match.save()

                    info = 'Successfully declared a winner'
                    color = 'primary'

                else:
                    match.user1_decision = None
                    match.user2_decision = None
                    match.save()
                    info = 'Your answers are not consistent. Please distinguish a winner once more.'
                    color = 'danger'

    return render(request, 'tournaments/my_tournaments.html',
                  {'tournaments': my_participations,
                   'matches': my_matches,
                   'user': request.user,
                   'logged_in': request.user.is_authenticated,
                   'info': info,
                   'color': color})

"""Backfill de PracticeHistory.speed_wpm com o speed_wpm atual do usuário.

Aproximação: tentativas registradas antes desta migração não guardam a
velocidade usada no momento — usamos a preferência atual do usuário como
melhor estimativa disponível (usuários sem UserMorseSettings recebem o
default de 20 WPM, mesmo fallback do restante do backend).
"""

from django.db import migrations

DEFAULT_WPM = 20


def backfill_speed_wpm(apps, schema_editor):
    PracticeHistory = apps.get_model('practice', 'PracticeHistory')
    UserMorseSettings = apps.get_model('morse', 'UserMorseSettings')

    settings_by_user = dict(UserMorseSettings.objects.values_list('user_id', 'speed_wpm'))

    histories = list(PracticeHistory.objects.filter(speed_wpm__isnull=True).only('id', 'user_id'))
    for history in histories:
        history.speed_wpm = settings_by_user.get(history.user_id, DEFAULT_WPM)
    PracticeHistory.objects.bulk_update(histories, ['speed_wpm'], batch_size=500)


def noop_reverse(apps, schema_editor):
    # Irreversível de verdade (não há como recuperar o valor original
    # desconhecido) — no-op deixa o rollback do schema seguir sem erro.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('practice', '0002_practicehistory_speed_wpm_and_more'),
        ('morse', '0005_alter_usermorsesettings_speed_wpm'),
    ]

    operations = [
        migrations.RunPython(backfill_speed_wpm, noop_reverse),
    ]

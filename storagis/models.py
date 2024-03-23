from django.contrib.auth.models import User
from django.contrib.gis.db import models
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'gisproject.settings'
from django.conf import settings

def get_statocar_choices():
  statocar_choiches = [
    (-10,'N/D'),
    (-2,'Errore Procedura'),
    (0,'Ricevuto'),
    (1,'Validazione in corso'),
    (4,'Errori specifica'),
    (6,'Importato')
  ]
  return statocar_choiches

class progetti(models.Model):

  statocar_choices = get_statocar_choices()

  filename = models.CharField(max_length=255)
  data_caricamento = models.DateTimeField(auto_now_add=True)
  stato_caricamento = models.IntegerField(
    default=-10,
    choices=statocar_choices
  )
  owner = models.ForeignKey(User, related_name='progetti', on_delete=models.CASCADE)
  nome_progetto = models.CharField(max_length=16)
  comune = models.IntegerField()
  approvazione = models.BooleanField(null=True)
  riferimento_remoto = models.CharField(max_length=255,null=True)
  risultato_validazione = models.CharField(max_length=16000,null=True)

class tratte_ln(models.Model):
  prj = models.ForeignKey(progetti, related_name='tratte_ln', on_delete=models.CASCADE)
  idtrattaln = models.BigIntegerField(null=True)
  geom = models.GeometryField(null=True)

class nodi_pt(models.Model):
  prj = models.ForeignKey(progetti, related_name='nodi_pt', on_delete=models.CASCADE)
  idnodopt = models.BigIntegerField(null=True)
  geom = models.GeometryField(null=True)

class tratte_inf(models.Model):
  prj = models.ForeignKey(progetti, related_name='tratte_inf', on_delete=models.CASCADE)
  idtrattainf = models.BigIntegerField(null=True)
  idfeature = models.BigIntegerField(null=True)

class nodi_inf(models.Model):
  prj = models.ForeignKey(progetti, related_name='nodi_inf', on_delete=models.CASCADE)
  idnodoinf = models.BigIntegerField(null=True)
  idfeature = models.BigIntegerField(null=True)
  etichetta = models.CharField(max_length=255,null=True)

class nodi_rete(models.Model):
  prj = models.ForeignKey(progetti, related_name='nodi_rete', on_delete=models.CASCADE)
  idnodorete = models.BigIntegerField(null=True)
  idfeature = models.BigIntegerField(null=True)
  etichetta = models.CharField(max_length=255,null=True)

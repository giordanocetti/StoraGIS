from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets

from storagis.serializers import GroupSerializer, UserSerializer

from storagis.serializers import ImportProjectSerializer
from storagis.models import progetti, get_statocar_choices
from rest_framework import response, status
import uuid
from django.core.files.base import ContentFile
from django.utils import timezone

from rest_framework.views import APIView

from django.shortcuts import render

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all().order_by('-date_joined')
  serializer_class = UserSerializer
  permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
  queryset = Group.objects.all()
  serializer_class = GroupSerializer
  permission_classes = [permissions.IsAuthenticated]

class ImportProject(viewsets.ViewSet):
  serializer_class = ImportProjectSerializer
  permission_classes = [permissions.IsAuthenticated]

  def list(self, request):

    user_filter = str(request.user.id)
    user = User.objects.filter(id=request.user.id).values().first()
    uploads = list(progetti.objects.filter(owner=user['id']).values().all().order_by('-id'))

    uploads = self.tuneup(uploads, request)

    if len(uploads) > 0:
      return response.Response(uploads)
    else:
      return response.Response("Nessun caricamento trovato.")

  def tuneup(self,uploads, request):
    tuned_ups = [dict() for x in uploads]
    for i,ob in enumerate(uploads):
      tuned_ups[i]['id'] = ob['id']
      tuned_ups[i]['filename'] = ob['filename']
      tuned_ups[i]['data_caricamento'] = ob['data_caricamento'].astimezone().strftime("%d/%m/%Y %H:%M:%S")
      tuned_ups[i]['stato_caricamento'] = next(x[1] for x in get_statocar_choices() if x[0] == ob['stato_caricamento'])
      tuned_ups[i]['nome_progetto'] = ob['nome_progetto']
      tuned_ups[i]['comune'] = ob['comune']
      tuned_ups[i]['approvazione'] = ob['approvazione']
      tuned_ups[i]['risultato_validazione'] = ob['risultato_validazione']
      tuned_ups[i]['owner'] = User.objects.filter(id=ob['owner_id']).values().first()['username']
      tuned_ups[i]['ESECUZIONE APPROVAZIONE'] = request.build_absolute_uri('/approvazione/%s'%ob['id'])
      tuned_ups[i]['ESECUZIONE BOCCIATURA'] = request.build_absolute_uri('/bocciatura/%s'%ob['id'])
      tuned_ups[i]['VISUALIZZA PROGETTO'] = request.build_absolute_uri('/visualizzazione/%s'%ob['id'])

    return tuned_ups

  def create(self, request):
    serializer = ImportProjectSerializer(data=request.data)
    if not serializer.is_valid():
      return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    uploaded_filename=request.FILES['file_progetto'].name
    generated_uuid=str(uuid.uuid4())
    full_filename='/opt/storagis/data/caricamenti/%s.zip'%generated_uuid

    fout=open(full_filename, 'wb+')
    file_content=ContentFile(request.FILES['file_progetto'].read())
    stato_caricamento=-10
    data_caricamento = timezone.localtime(timezone.now())

    for chunk in file_content.chunks():
      fout.write(chunk)
    fout.close()

    if serializer.is_valid():
      serializer.save(
        owner=request.user,
        filename=generated_uuid,
        stato_caricamento=stato_caricamento,
        data_caricamento=data_caricamento,
      )
      return response.Response('Caricamento effettuato con successo.')

    return response.Response(serializer.data)

class ApprovaBoccia(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request, car_id=None):

    current_url = request.path.split('/')[1]
    approvazione=True
    approvazione_label='APPROVATO'
    if current_url == 'bocciatura':
      approvazione=False
      approvazione_label='BOCCIATO'

    if not car_id:
      return response.Response("ID CARICAMENTO NECESSARIO")

    prog = progetti.objects.filter(owner=request.user.id,id=car_id).first()
    if not prog:
      return response.Response("Non è possibile continuare, l'ID indicato è errato oppure non presente tra i tuoi caricamenti. Riprova.")

    if prog.approvazione != approvazione:
      prog.approvazione = approvazione
      prog.save()
    else:
      return response.Response("ERRORE: il progetto si trova già in stato di: %s"%(approvazione_label))

    return response.Response("SUCCESSO: il progetto è stato correttamente posto nello stato di %s."%(approvazione_label))

class VisualizzaPrj(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request, prj_id=None):

    visualizzaprj_template = 'index.html'
    geoserver_url = request.build_absolute_uri().split(request.path)[0] + '/geoserver'
    oldata = {'prj_id':prj_id,'geoserver_url':geoserver_url}

    if not prj_id:
      return response.Response("PROGETTO NON TROVATO.")

    prog = progetti.objects.filter(owner=request.user.id,id=prj_id).first()
    if not prog:
      return response.Response("PROGETTO NON TROVATO O NON APPARTENENTE ALL'UTENTE AUTENTICATO.")

    return render(request, 'index.html', oldata)


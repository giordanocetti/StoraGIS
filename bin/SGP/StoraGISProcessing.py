import traceback
import time
import os, sys
import json
import django
import pycurl
from io import BytesIO
if not '/opt/storagis/' in sys.path:
  sys.path.append('/opt/storagis/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'gisproject.settings'
django.setup()
from storagis.models import progetti
from django.apps import apps

sleeptime=1 #secondi

ct1_params={"mapping":{"nodi_pt.shp":{"idnodopt":{"titleoptions":["idnodopt"],"datatype":"int8_notnull"},"geom":{"titleoptions":["geom"],"datatype":False}},"nodi_inf.csv":{"idnodoinf":{"titleoptions":["idnodoinf"],"datatype":"int8_notnull"},"idfeature":{"titleoptions":["idfeature"],"datatype":"int8_notnull"},"etichetta":{"titleoptions":["etichetta"],"datatype":"varchar255"}},"nodi_rete.csv":{"idnodorete":{"titleoptions":["idnodorete"],"datatype":"int8_notnull"},"idfeature":{"titleoptions":["idfeature"],"datatype":"int8_notnull"},"etichetta":{"titleoptions":["etichetta"],"datatype":"varchar255"}},"tratte_ln.shp":{"idtrattaln":{"titleoptions":["idtrattaln"],"datatype":"int8_notnull"},"geom":{"titleoptions":["geom"],"datatype":False}},"tratte_inf.csv":{"idtrattainf":{"titleoptions":["idtrattainf"],"datatype":"int8_notnull"},"idfeature":{"titleoptions":["idfeature"],"datatype":"int8_notnull"}}},"constraints":{"nodi_pt.shp":{"constraint":[["idnodopt"]]},"nodi_inf.csv":{"constraint":[["idnodoinf"]]},"nodi_rete.csv":{"constraint":[["idnodorete"]]},"tratte_ln.shp":{"constraint":[["idtrattaln"]]},"tratte_inf.csv":{"constraint":[["idtrattainf"]]}},"relations":{"nodi_pt.shp":[],"nodi_inf.csv":[{"f1":"idfeature","t2":"nodi_pt.shp","f2":"idnodopt"}],"nodi_rete.csv":[{"f1":"idfeature","t2":"nodi_pt.shp","f2":"idnodopt"}],"tratte_ln.shp":[],"tratte_inf.csv":[{"f1":"idfeature","t2":"tratte_ln.shp","f2":"idtrattaln"}]},"traduzione_tabelle":{"nodi_pt.shp":"nodi_pt","nodi_inf.csv":"nodi_inf","nodi_rete.csv":"nodi_rete","tratte_ln.shp":"tratte_ln","tratte_inf.csv":"tratte_inf"}}

ps_car_url = 'https://storagisprocessing.bycloud.eu/importproject/'
ps_get_url = 'https://storagisprocessing.bycloud.eu/getproject/'
ps_user = 'utenzagenerale'
ps_pass = '%+WCk6r03B"T:1;^>8p=8\?NE1CRjH-H'

def restcall(url,post,timeout,auth,params=False,ffield=False):
  try:
    b_obj=BytesIO()
    h_obj=BytesIO()
    c=pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.CONNECTTIMEOUT, timeout)
    c.setopt(c.USERPWD, auth)
    if post is True:
      postdata=[(ffield[0],(c.FORM_FILE, ffield[1]))]
      postdata.extend([('params',params)])
      c.setopt(c.HTTPPOST,postdata)
      c.setopt(c.REFERER, 'storagis-lover')

    c.setopt(c.WRITEDATA, b_obj)
    c.setopt(c.HEADERFUNCTION, h_obj.write)
    c.perform()
    statuscode = c.getinfo(c.RESPONSE_CODE)
    c.close()
    response=b_obj.getvalue()
    return (statuscode,response)

  except Exception:
    traceback.print_exc()
    return False

primogiro = True
while True:
  if not primogiro:
    time.sleep(sleeptime)
  primogiro = False

  uploads = progetti.objects.all().order_by('id')

  for u in uploads.filter(stato_caricamento=-10):
    u.stato_caricamento = 0
    u.save()

  for u in uploads.filter(stato_caricamento=0):
    try:
      ffield = ['file_progetto','/opt/storagis/data/caricamenti/%s.zip'%u.filename]
      params = json.dumps(ct1_params)
      auth = '%s:%s'%(ps_user, ps_pass)
      esito = restcall(ps_car_url,True,60,auth,params,ffield)
      if esito is False:
        raise Exception('Errore generale.')

      statuscode, response = esito

      if statuscode != 200:
        raise Exception('Errore di autenticazione, o di servizio. Verificare i dati di accesso.')

      u.riferimento_remoto=response.decode('utf8').replace('"','')
      u.stato_caricamento=1

    except Exception:
      traceback.print_exc()
      u.stato_caricamento=-2
      continue
    finally:
      u.save()

  for u in uploads.filter(stato_caricamento=1):
    try:
      url = ps_get_url+u.riferimento_remoto
      auth = '%s:%s'%(ps_user, ps_pass)

      esito = restcall(url,False,60,auth)
      if esito is False:
        raise Exception('Errore generale.')

      statuscode, response = esito
      if statuscode == 201:
        continue

      if statuscode == 204:
        u.stato_caricamento=4
        u.risultato_validazione=response.decode('utf8')
        continue

      if statuscode != 200:
        raise Exception('Errore di autenticazione, o di servizio. Verificare i dati di accesso usando il browser.')

      response=json.loads(response.decode('utf8'))

      for k,v in response.items():
        thismodel = apps.get_model('storagis', k)

        for row in v[1:]:
          m = thismodel.objects.create(prj_id=u.id)

          for i,title in enumerate(v[0]):
            setattr(m,title,row[i])
            m.save()

      u.stato_caricamento=6

    except Exception:
      traceback.print_exc()
      u.stato_caricamento=-2
    finally:
      u.save()

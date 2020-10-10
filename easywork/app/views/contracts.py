# coding=utf-8
import pytz

from datetime import datetime
from decimal import Decimal

from django.http import JsonResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
from rest_framework import authentication, permissions
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.views import APIView
from django_coinpayments.exceptions import CoinPaymentsProviderError

from easywork.app.models import Project, Contract, Payment


class BearerTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Bearer'


class contractView(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    #
    def get(self, request, format=None):
        # '''
        # request:
        #
        # response:
        # []
        # [{"id":2,"created_date_time":"2018-08-24T16:14:52.70006Z","status":"started","project_id":2,"project_title":"facebook groups share","project_description":"share messages on facebook groups.","contractor_id":"worker","owner_id":"easywork","terms_id":3,"agent_first_name":"easywork","agent_last_name":"easywork","last_date_worked":"2018-08-24T00:00:00Z","last_date_value":40,"week_limit":0,"last_week_value":0,"last_day_value":0}]
        #
        # '''

        user = request.user
        res_arr = []

        if user.user_type == 'work':
            contracts_qs = user.contracts_as_contractor.all()
        else:
            contracts_qs = user.contracts_owned.all()

        for c in contracts_qs:
            contract_dict = {
                # 'title': p.title,
                # 'id': p.id,
                # 'description': p.description,
                # 'owner_id': p.owner.id,
                # 'created_date_time': p.created_date_time
            }
            contract_dict = {"id": c.id,
                             "created_date_time": c.created_date_time,
                             "status": c.status,
                             "project_id": c.project.id,
                             "project_title": c.project.title,
                             "project_description": c.project.description,
                             "contractor_id": c.contractor.username,
                             "owner_id": c.owner.username,
                             "terms_id": c.terms.id,
                             "agent_first_name": c.agent_first_name if c.agent_first_name is not None else "",
                             "agent_last_name": c.agent_last_name if c.agent_last_name is not None else "",
                             "last_date_worked": c.last_date_worked if c.last_date_worked is not None else "",
                             "last_date_value": c.last_date_value if c.last_date_value is not None else 0,
                             "week_limit": c.week_limit,
                             "last_week_value": c.last_week_value,
                             "last_day_value": c.last_week_value
                             }

            res_arr.append(contract_dict)

        return JsonResponse(res_arr, status=200, safe=False)



class get_contract_by_id_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    #
    def get(self, request, contract_id=None, format=None):
        # '''
        # request:
        #
        # response:
        # '''

        c = Contract.objects.get(id=contract_id)

        response = {"id": c.id,
                    "created_date_time": c.created_date_time,
                    "status": c.status,
                    "project_id": c.project.id,
                    "project_title": c.project.title,
                    "project_description": c.project.description,
                    "contractor_id": c.contractor.username,
                    "owner_id": c.owner.username,
                    "terms_id": c.terms.id,
                    "agent_first_name": c.agent_first_name,
                    "agent_last_name": c.agent_last_name,
                    "last_date_worked": c.last_date_worked,
                    "last_date_value": c.last_date_value,
                    "week_limit": c.week_limit,
                    "last_week_value": c.last_week_value,
                    "last_day_value": c.last_week_value
                    }
        return JsonResponse(response, status=200)


class get_contract_terms_by_id_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    #
    def get(self, request, contract_id=None, format=None):
        # '''
        # request:
        #
        # response:
        # {"id":3,"created_date_time":"2018-08-24T16:14:22.95369Z","currency_id":"eur","price_per_hour":5,"weekly_limit_in_hours":50}
        # '''

        c = Contract.objects.get(id=contract_id)

        response = {
            'id': c.terms.id,
            'created_date_time': c.terms.created_date_time,
            'currency_id': c.terms.currency_id,
            'price_per_hour': c.terms.price_per_hour,
            'weekly_limit_in_hours': c.terms.weekly_limit_in_hours
        }

        return JsonResponse(response, status=200)


class get_contract_totals_by_id_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (JSONParser, FormParser)

    #
    def get(self, request, contract_id=None, format=None):
        # ''' TODO: TOTALS
        # request:
        #
        # response:
        # {"last_24_hours":60,"current_week":60,"previous_week":0,"since_start":60}
        #
        # '''

        c = Contract.objects.get(id=contract_id)
        # arr = []

        response = {
            'last_24_hours': c.today_value,
            'current_week': c.current_week_value,
            'previous_week': c.last_week_value,
            'since_start': c.all_time_value,
        }
        return JsonResponse(response, status=200)


class get_contract_events_by_id_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (JSONParser, FormParser)

    #
    def get(self, request, contract_id=None, format=None):
        # ''' TODO: events
        # request:
        # https://api.easywork.me/contracts/2/events?from=2018-09-04&to=2018-09-04
        # response:
        # []
        # or
        # [{"id":57,"created_date_time":"2018-09-03T17:47:04.805308Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/174704.jpg","title":""},{"id":58,"created_date_time":"2018-09-03T17:47:29.047829Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/174729.jpg","title":""},{"id":59,"created_date_time":"2018-09-03T17:47:31.757556Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/174731.jpg","title":""},{"id":60,"created_date_time":"2018-09-03T17:50:16.227912Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/175016.jpg","title":""},{"id":61,"created_date_time":"2018-09-03T17:50:17.6198Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/175017.jpg","title":""},{"id":62,"created_date_time":"2018-09-03T17:55:47.529207Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/175547.jpg","title":""},{"id":63,"created_date_time":"2018-09-03T17:55:49.272587Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/175549.jpg","title":""},{"id":64,"created_date_time":"2018-09-03T17:56:45.337772Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/175645.jpg","title":""},{"id":65,"created_date_time":"2018-09-03T17:56:47.300448Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/175647.jpg","title":""},{"id":66,"created_date_time":"2018-09-03T18:00:52.436852Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/180052.jpg","title":""},{"id":67,"created_date_time":"2018-09-03T18:00:54.255184Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/180054.jpg","title":""},{"id":68,"created_date_time":"2018-09-03T18:04:18.002375Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/180418.jpg","title":""},{"id":69,"created_date_time":"2018-09-03T18:04:19.697758Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/180419.jpg","title":""},{"id":70,"created_date_time":"2018-09-03T18:06:28.287114Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/180628.jpg","title":""},{"id":71,"created_date_time":"2018-09-03T18:06:29.608553Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/180629.jpg","title":""},{"id":72,"created_date_time":"2018-09-03T18:09:34.711489Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/180934.jpg","title":""},{"id":73,"created_date_time":"2018-09-03T18:09:35.811601Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/180935.jpg","title":""},{"id":74,"created_date_time":"2018-09-03T18:09:49.269566Z","contract_id":2,"event_type":"log","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/180949.jpg","title":""},{"id":75,"created_date_time":"2018-09-03T18:09:50.729804Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/180950.jpg","title":""},{"id":78,"created_date_time":"2018-09-03T18:20:13.034353Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182013.jpg","title":""},{"id":79,"created_date_time":"2018-09-03T18:20:25.223349Z","contract_id":2,"event_type":"log","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182025.jpg","title":""},{"id":80,"created_date_time":"2018-09-03T18:20:26.485033Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182026.jpg","title":""},{"id":81,"created_date_time":"2018-09-03T18:20:28.978964Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182028.jpg","title":""},{"id":82,"created_date_time":"2018-09-03T18:20:42.836221Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182042.jpg","title":""},{"id":83,"created_date_time":"2018-09-03T18:21:31.099931Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182131.jpg","title":""},{"id":84,"created_date_time":"2018-09-03T18:21:37.209598Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182137.jpg","title":""},{"id":85,"created_date_time":"2018-09-03T18:23:50.371647Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182350.jpg","title":""},{"id":86,"created_date_time":"2018-09-03T18:24:13.771816Z","contract_id":2,"event_type":"log","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182413.jpg","title":""},{"id":87,"created_date_time":"2018-09-03T18:24:15.190978Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182415.jpg","title":""},{"id":88,"created_date_time":"2018-09-03T18:27:52.448071Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182752.jpg","title":""},{"id":89,"created_date_time":"2018-09-03T18:28:00.95427Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182800.jpg","title":""},{"id":94,"created_date_time":"2018-09-03T18:28:49.353365Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182849.jpg","title":""},{"id":95,"created_date_time":"2018-09-03T18:28:50.482994Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182850.jpg","title":""},{"id":96,"created_date_time":"2018-09-03T18:29:13.049021Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182913.jpg","title":""},{"id":97,"created_date_time":"2018-09-03T18:29:19.248043Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/182919.jpg","title":""},{"id":98,"created_date_time":"2018-09-03T18:32:52.889551Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/183252.jpg","title":""},{"id":99,"created_date_time":"2018-09-03T18:32:56.681104Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/183256.jpg","title":""},{"id":100,"created_date_time":"2018-09-03T18:32:57.377673Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/183257.jpg","title":""},{"id":101,"created_date_time":"2018-09-03T18:32:57.984421Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/183257.jpg","title":""},{"id":102,"created_date_time":"2018-09-03T18:32:58.377143Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/183258.jpg","title":""},{"id":103,"created_date_time":"2018-09-03T18:32:58.617706Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/183258.jpg","title":""},{"id":104,"created_date_time":"2018-09-03T18:32:58.896316Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/183258.jpg","title":""},{"id":105,"created_date_time":"2018-09-03T18:32:59.12979Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/183259.jpg","title":""},{"id":106,"created_date_time":"2018-09-03T18:32:59.353548Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/183259.jpg","title":""},{"id":107,"created_date_time":"2018-09-03T18:32:59.561792Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/183259.jpg","title":""},{"id":108,"created_date_time":"2018-09-03T18:51:00.517771Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/185100.jpg","title":""},{"id":109,"created_date_time":"2018-09-03T18:51:10.003354Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/185110.jpg","title":""},{"id":110,"created_date_time":"2018-09-03T18:51:39.038552Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/185139.jpg","title":""},{"id":111,"created_date_time":"2018-09-03T18:51:45.430276Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/185145.jpg","title":""},{"id":112,"created_date_time":"2018-09-03T18:51:49.816201Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/185149.jpg","title":""},{"id":113,"created_date_time":"2018-09-03T18:52:01.935638Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/185201.jpg","title":""},{"id":114,"created_date_time":"2018-09-03T18:56:55.029874Z","contract_id":2,"event_type":"start","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/185655.jpg","title":""},{"id":115,"created_date_time":"2018-09-03T18:56:56.601729Z","contract_id":2,"event_type":"stop","keyboard_events_count":0,"mouse_events_count":0,"screenshot_url":"https://s3-us-west-2.amazonaws.com/hourly-tracker/worker/000002/2018-09-03/185656.jpg","title":""}]
        # '''

        c = Contract.objects.get(id=contract_id)
        arr = []

        for e in c.contract_events.all():
            ## filter dates
            event = {"id": e.id,
                     "created_date_time": e.created_date_time,
                     "contract_id": e.contract.id,
                     "event_type": e.event_type,
                     "keyboard_events_count": e.keyboard_events_count,
                     "mouse_events_count": e.mouse_events_count,
                     "screenshot_url": '{0}://{1}/{2}'.format(request.scheme, request.get_host(), e.screenshot_url),
                     "title": e.title
                     }
            arr.append(event)
        return JsonResponse(arr, status=200, safe=False)


class events_contract_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request, contract_id, event_type, format=None):
        c = Contract.objects.get(id=contract_id)
        created_date_time = datetime.utcnow().replace(tzinfo=pytz.utc)

        screenshot_filename = None
        screenshot_url = None
        file = request.data.get('screenshot_file')

        if file:
            fs = FileSystemStorage('screenshots/', 'screenshots/')
            extension = file.name.split('.')[-1].lower()
            filename = 'contract_{0}/{1}.{2}'.format(c.id, created_date_time.strftime('%d_%m_%Y-%H_%M_%S'), extension)
            screenshot_filename = fs.save(filename, file)
            screenshot_url = fs.url(screenshot_filename)

        e = c.contract_events.create(
            title=request.data.get('title', ''),
            mouse_events_count=request.data.get('mouse_events_count', 0),
            keyboard_events_count=request.data.get('keyboard_events_count', 0),
            event_type=event_type,
            created_date_time=created_date_time,
            screenshot_filename=screenshot_filename,
            screenshot_url=screenshot_url
        )

        response = {
            "id": e.id,
            "created_date_time": e.created_date_time,
            "contract_id": e.contract.id,
            "event_type": e.event_type,
            "keyboard_events_count": e.keyboard_events_count,
            "mouse_events_count": e.mouse_events_count,
            "screenshot_url": '{0}://{1}/{2}'.format(request.scheme, request.get_host(), e.screenshot_url),
            "title": e.title
        }

        return JsonResponse(response, status=200)


class end_contract_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (JSONParser, FormParser)

    # @transaction.atomic()
    def post(self, request, contract_id, format=None):
        # ''' TODO: events
        # request:
        # http://127.0.0.1:8000/contracts/1/end
        # response:
        # {"code":1006,"message":"Contract ended successfully"}
        # '''

        c = Contract.objects.get(id=contract_id)
        c.status = "ended"
        c.save()
        response = {"code": 1006,
                    "message": "Contract ended successfully"}
        return JsonResponse(response, status=200)


class pause_contract_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (JSONParser, FormParser)

    # @transaction.atomic()
    def post(self, request, contract_id, format=None):
        # ''' TODO: events
        # request:
        # http://127.0.0.1:8000/contracts/1/pause
        # response:
        # {"code":1005,"message":"Contract paused successfully"}
        # '''

        c = Contract.objects.get(id=contract_id)
        c.status = "paused"
        c.save()
        response = {"code": 1005,
                    "message": "Contract paused successfully"}
        return JsonResponse(response, status=200)

class resume_contract_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (JSONParser, FormParser)

    # @transaction.atomic()
    def post(self, request, contract_id, format=None):
        # ''' TODO: events
        # request:
        # http://127.0.0.1:8000/contracts/1/resume
        # response:
        # {"code":1005,"message":"Contract resumed successfully"}
        # '''

        c = Contract.objects.get(id=contract_id)
        c.status = "started"
        c.save()
        response = {"code": 1004,
                    "message": "Contract resumed successfully"}
        return JsonResponse(response, status=200)


class screenshots_contract_handler(APIView):
    # authentication_classes = (BearerTokenAuthentication,)
    # permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, filepath, format=None):
        fs = FileSystemStorage('screenshots/', 'screenshots/')
        try:
            with fs.open(filepath) as f:
                return HttpResponse(f.read(), content_type="image/jpeg")
        except FileNotFoundError:
            return HttpResponse('File Not Found', status=404)


class pay_contract_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (JSONParser, FormParser)

    # @transaction.atomic()
    def post(self, request, contract_id, format=None):
        # ''' TODO:
        # request:
        # http://127.0.0.1:8000/contracts/1/pay
        # response:
        # {"code":1005,"message":"Contract resumed successfully"}
        # '''

        c = Contract.objects.get(id=contract_id)

        # TODO: fix to real amount
        amount = 1
        currency = c.terms.currency_id

        # TODO: remove test currency
        p = Payment(
            currency='LTCT',
            amount=amount,
            amount_paid=Decimal(0),
            status=Payment.PAYMENT_STATUS_PROVIDER_PENDING,
            author=request.user,
            contract=c
        )
        response = {}
        status = 201
        try:
            p.create_tx()
            p.status = Payment.PAYMENT_STATUS_PENDING
            p.save()
            response = {
                "id": p.provider_tx.id,
                "address": p.provider_tx.address,
                "amount": p.provider_tx.amount,
                "qrcode_url": p.provider_tx.qrcode_url,
                "status_url": p.provider_tx.status_url,
                "timeout": p.provider_tx.timeout
            }
        except CoinPaymentsProviderError as e:
            response['error'] = e
            status = 422

        return JsonResponse(response, status=status)

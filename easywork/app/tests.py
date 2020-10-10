# coding=utf-8
import datetime
import json

import pytz
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.test import force_authenticate

from  easywork.app.models import BaseUser, Project, Invitation, Term, Contract, ContractEvent
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class AccountTests(APITestCase):
    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        eprint("test_create_account")
        url = reverse('api_user_create')
        print(url)
        data = {"email": "me@easywork.me", "id": "admin", "user_type": "work", "password": "123123", "first_name": "firstname", "last_name": "lastname"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BaseUser.objects.count(), 1)
        self.assertEqual(BaseUser.objects.get().first_name, 'firstname')

    def test_get_user(self):
        """
        Test user get by id
        """
        eprint("test_get_user")
        url = reverse('api_user_create')
        data = {"email": "me@easywork.me", "id": "admin", "user_type": "work", "password": "123123", "first_name": "firstname", "last_name": "lastname"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(BaseUser.objects.count(), 1)
        self.assertEqual(BaseUser.objects.get().first_name, 'firstname')

        data_response = json.loads(response.content)
        user_id = data_response['id']
        url = reverse("api_user_get", kwargs={'user_id': user_id})

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + data_response['token'])
        response = self.client.get(url, format='json')
        new_response = json.loads(response.content)
        self.assertEqual(new_response['email'], 'me@easywork.me')
        self.assertEqual(new_response['id'], 'admin')
        self.assertEqual(new_response['is_admin'], 'false')
        self.assertEqual(new_response['user_type'], 'work')


class ProjectTests(APITestCase):
    def init(self):
        url = reverse('api_user_create')
        print(url)
        data = {"email": "me@easywork.me", "id": "admin", "user_type": "work", "password": "123123", "first_name": "firstname", "last_name": "lastename"}
        response = self.client.post(url, data, format='json')
        data_response = json.loads(response.content)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + data_response['token'])

    def test_get_projects_empty(self):
        """
        Test user get by id
        """
        eprint("test_get_projects_empty")
        self.init()
        url = reverse('api_project')
        response = self.client.get(url, format='json')

        new_response = json.loads(response.content)
        self.assertEqual(new_response, [])

    def test_create_project(self):
        """
        Test create project
        """
        eprint("test_create_project")
        self.init()
        url = reverse('api_project')
        data = {"title": "Project Test", "description": "This is the test project description"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_response = json.loads(response.content)
        self.assertEqual(new_response['title'], "Project Test")
        self.assertEqual(new_response['description'], "This is the test project description")

    def test_get_projects(self):
        """
        Test user get all loged in user projects
        """
        eprint("test_get_projects")
        self.test_create_project()
        url = reverse('api_project')
        response = self.client.get(url, format='json')

        new_response = json.loads(response.content)
        self.assertEqual(len(new_response), Project.objects.count())

    def test_get_project(self):
        """
        Test project get by id
        """
        eprint("test_get_project")
        self.test_create_project()
        url = reverse('api_project_get', kwargs={'project_id': Project.objects.first().id})
        response = self.client.get(url, format='json')

        new_response = json.loads(response.content)
        self.assertEqual(new_response['title'], Project.objects.first().title)


class InvitationTests(APITestCase):
    client_token = None
    worker_token = None

    def init(self):
        url = reverse('api_user_create')

        # Create worker
        print(url)
        data = {"email": "worker@easywork.me", "id": "worker", "user_type": "work", "password": "123123", "first_name": "Firstname", "last_name": "Lastname"}
        response = self.client.post(url, data, format='json')
        data_response = json.loads(response.content)

        self.worker_token = 'Bearer ' + data_response['token']

        # Create client
        data = {"email": "client@easywork.me", "id": "client", "user_type": "client", "password": "123123", "first_name": "Firstname", "last_name": "Lastname"}
        response = self.client.post(url, data, format='json')
        data_response = json.loads(response.content)

        self.client_token = 'Bearer ' + data_response['token']
        self.client.credentials(HTTP_AUTHORIZATION=self.client_token)

        # Create project
        url = reverse('api_project')
        data = {"title": "Project Test", "description": "This is the test project description"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_response = json.loads(response.content)
        self.assertEqual(new_response['title'], "Project Test")
        self.assertEqual(new_response['description'], "This is the test project description")

        self.assertEqual(BaseUser.objects.count(), 2)

    def test_invitations_empty(self):
        """
        Test get invitations empty
        """
        eprint("test_invitations_empty")
        self.init()
        url = reverse('api_invitation')
        response = self.client.get(url, format='json')

        new_response = json.loads(response.content)
        self.assertEqual(new_response, [])

    def test_create_invitation(self):
        """
        Test create invitation
        """
        eprint("test_create_invitation")
        self.init()
        url = reverse('api_invitation')
        data = {"project_id": Project.objects.first().id, "invitee_id": "worker", "currency_id": "eur", "price_per_hour": 0, "weekly_limit_in_hours": 0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_response = json.loads(response.content)
        self.assertEqual(new_response['owner_id'], "client")
        self.assertEqual(new_response['invitee_id'], "worker")
        self.assertEqual(new_response['status'], "pending")
        self.assertEqual(new_response['project_id'], Project.objects.first().id)
        self.assertEqual(new_response['invitee_email'], "")
        self.assertEqual(Term.objects.all().count(), 1)

        ## Accept invitation
        url = reverse('api_invitation_accept', kwargs={'invitation_id': new_response['id']})
        ## Log in as worker
        self.client.credentials(HTTP_AUTHORIZATION=self.worker_token)
        response = self.client.post(url, {}, format='json')
        parsed_response = json.loads(response.content)
        self.assertEqual(Contract.objects.all().count(), 1)
        self.assertEqual(Contract.objects.get(id=parsed_response['contract_id']).owner.username, new_response['owner_id'])

    def test_get_invitations(self):
        """
        Test get invitations
        """
        eprint("test_get_invitations")
        self.test_create_invitation()

        self.client.credentials(HTTP_AUTHORIZATION=self.worker_token)
        url = reverse('api_invitation')
        response = self.client.get(url, format='json')

        new_response = json.loads(response.content)
        self.assertEqual(len(new_response), Invitation.objects.count())


class ContractTests(APITestCase):
    client_token = None
    worker_token = None

    def init(self):
        url = reverse('api_user_create')

        # Create worker
        print(url)
        data = {"email": "me@easywork.me", "id": "worker", "user_type": "work", "password": "123123", "first_name": "Firstname", "last_name": "Lastname"}
        response = self.client.post(url, data, format='json')
        data_response = json.loads(response.content)

        self.worker_token = 'Bearer ' + data_response['token']

        # Create client
        data = {"email": "client@easywork.me", "id": "client", "user_type": "client", "password": "123123", "first_name": "Firstname", "last_name": "Lastname"}
        response = self.client.post(url, data, format='json')
        data_response = json.loads(response.content)

        self.client_token = 'Bearer ' + data_response['token']
        self.client.credentials(HTTP_AUTHORIZATION=self.client_token)

        # Create project
        url = reverse('api_project')
        data = {"title": "Project Test", "description": "This is the test project description"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_response = json.loads(response.content)
        self.assertEqual(new_response['title'], "Project Test")
        self.assertEqual(new_response['description'], "This is the test project description")

        self.assertEqual(BaseUser.objects.count(), 2)

        # Create INVITATION, Accept it so Contract is created
        url = reverse('api_invitation')
        data = {"project_id": Project.objects.first().id, "invitee_id": "worker", "currency_id": "eur", "price_per_hour": 0, "weekly_limit_in_hours": 0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_response = json.loads(response.content)
        self.assertEqual(new_response['owner_id'], "client")
        self.assertEqual(new_response['invitee_id'], "worker")
        self.assertEqual(new_response['status'], "pending")
        self.assertEqual(new_response['project_id'], Project.objects.first().id)
        self.assertEqual(new_response['invitee_email'], "")
        self.assertEqual(Term.objects.all().count(), 1)

        ## Accept invitation
        url = reverse('api_invitation_accept', kwargs={'invitation_id': new_response['id']})
        ## Log in as worker
        self.client.credentials(HTTP_AUTHORIZATION=self.worker_token)
        response = self.client.post(url, {}, format='json')
        parsed_response = json.loads(response.content)
        self.assertEqual(Contract.objects.all().count(), 1)
        self.assertEqual(Contract.objects.get(id=parsed_response['contract_id']).owner.username, new_response['owner_id'])

        #TODO: reject inviatation test.

    def test_get_contract(self):
        self.init()
        url = reverse('api_contract')

        response = self.client.get(url, format='json')
        new_response = json.loads(response.content)
        self.assertEqual(len(new_response), 1)
        self.assertEqual(Project.objects.first().id, new_response[0]['project_id'])
        self.assertEqual('worker', new_response[0]['contractor_id'])

    def test_get_contract_by_id(self):
        self.test_get_contract()
        contract = Contract.objects.first()
        url = reverse('api_contract_get', kwargs={'contract_id': contract.id})
        response = self.client.get(url, format='json')
        new_response = json.loads(response.content)
        self.assertEqual('worker', new_response['contractor_id'])
        self.assertEqual(contract.id, new_response['id'])
        # self.assertEqual(contract.created_date_time, new_response['created_date_time'])
        self.assertEqual(contract.status, new_response['status'])
        self.assertEqual(contract.project.id, new_response['project_id'])
        self.assertEqual(contract.project.title, new_response['project_title'])
        self.assertEqual(contract.project.description, new_response['project_description'])
        self.assertEqual(contract.contractor.username, new_response['contractor_id'])
        self.assertEqual(contract.owner.username, new_response['owner_id'])
        self.assertEqual(contract.terms.id, new_response['terms_id'])
        # self.assertEqual(contract.last_date_worked, new_response['last_date_worked'])
        self.assertEqual(contract.week_limit, new_response['week_limit'])

    def test_api_contract_get_terms(self):
        self.test_get_contract()
        contract = Contract.objects.first()
        url = reverse('api_contract_get_terms', kwargs={'contract_id': contract.id})

        response = self.client.get(url, format='json')
        new_response = json.loads(response.content)

        self.assertEqual(contract.terms.id, new_response['id'])
        self.assertEqual(contract.terms.currency_id, new_response['currency_id'])
        self.assertEqual(contract.terms.price_per_hour, new_response['price_per_hour'])
        self.assertEqual(contract.terms.weekly_limit_in_hours, new_response['weekly_limit_in_hours'])

    def test_api_contract_get_events(self):
        self.test_get_contract()
        contract = Contract.objects.first()

        ev1 = ContractEvent.objects.create(
            title="test",
            contract=contract,
            mouse_events_count=5,
            keyboard_events_count=123,
            event_type="start",
            created_date_time=datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
            created_date=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).date()
        )

        ev2 = ContractEvent.objects.create(
            title="test",
            contract=contract,
            mouse_events_count=2,
            keyboard_events_count=124,
            event_type="start",
            created_date_time=datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - datetime.timedelta(days=1),
            created_date=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).date() - datetime.timedelta(days=1)
        )

        url = reverse('api_contract_get_events', kwargs={'contract_id': contract.id})

        response = self.client.get(url, format='json')
        new_response = json.loads(response.content)

        self.assertEqual(len(new_response), 2)
        self.assertEqual(ev1.keyboard_events_count, new_response[0]['keyboard_events_count'])
        self.assertEqual(ev1.mouse_events_count, new_response[0]['mouse_events_count'])

    def test_api_contract_get_totals(self):
        self.test_get_contract()
        contract = Contract.objects.first()

        ev1 = ContractEvent.objects.create(
            title="test",
            contract=contract,
            mouse_events_count=5,
            keyboard_events_count=123,
            event_type="start",
            created_date_time=datetime.datetime.utcnow().replace(tzinfo=pytz.utc),
            created_date=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).date()
        )

        ev2 = ContractEvent.objects.create(
            title="test",
            contract=contract,
            mouse_events_count=2,
            keyboard_events_count=124,
            event_type="start",
            created_date_time=datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - datetime.timedelta(days=7),
            created_date=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).date() - datetime.timedelta(days=7)
        )
        ev3 = ContractEvent.objects.create(
            title="test",
            contract=contract,
            mouse_events_count=2,
            keyboard_events_count=124,
            event_type="start",
            created_date_time=datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - datetime.timedelta(days=7, minutes=1),
            created_date=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).date() - datetime.timedelta(days=7)
        )

        url = reverse('api_contract_get_totals', kwargs={'contract_id': contract.id})

        response = self.client.get(url, format='json')
        new_response = json.loads(response.content)

        self.assertEqual(new_response['last_24_hours'], 10)
        self.assertEqual(new_response['previous_week'], 20)
        '''
            'last_24_hours': c.today_value,
            'current_week': c.current_week_value,
            'previous_week': c.last_week_value,
            'since_start': c.all_time_value,
        '''

    def test_api_contract_end(self):
        url = reverse('api_contract_end', kwargs={'contract_id': Contract.objects.first()})

    def test_api_contract_pause(self):
        url = reverse('api_contract_pause', kwargs={'contract_id': Contract.objects.first()})

    def test_api_contract_resume(self):
        url = reverse('api_contract_resume', kwargs={'contract_id': Contract.objects.first()})

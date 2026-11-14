from django.test import TestCase
from django.urls import reverse

from .models import Shoot


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Shoot.objects.create(
            ady='Ali',
            fam='Amanow',
            topar='101',
            pm1_1=10,
            pm1_2=10,
            pm2_1=10,
            pm2_2=10,
            ak74=10,
            umumy=50,
        )
        Shoot.objects.create(
            ady='Begench',
            fam='Berdiyeva',
            topar='202',
            pm1_1=9,
            pm1_2=9,
            pm2_1=9,
            pm2_2=9,
            ak74=9,
            umumy=45,
        )

    def test_home_shows_all_students_when_no_group_selected(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ali')
        self.assertContains(response, 'Begench')
        self.assertEqual(response.context['selected_topar'], '')
        self.assertEqual(list(response.context['toparlar']), ['101', '202'])

    def test_home_filters_students_by_selected_group(self):
        response = self.client.get(reverse('home'), {'topar': '101'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ali')
        self.assertNotContains(response, 'Begench')
        self.assertEqual(response.context['selected_topar'], '101')
        self.assertEqual(response.context['conts'].count(), 1)

    def test_home_contains_simulator_button(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('simulyator'))
        self.assertContains(response, 'Yarag maglumatlary')


class ReitingViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Shoot.objects.create(
            ady='Ayna',
            fam='Allanazarowa',
            topar='121',
            pm1_1=10,
            pm1_2=10,
            pm2_1=9,
            pm2_2=9,
            ak74=10,
            umumy=48,
        )
        Shoot.objects.create(
            ady='Bahar',
            fam='Berdiyeva',
            topar='122',
            pm1_1=8,
            pm1_2=8,
            pm2_1=8,
            pm2_2=8,
            ak74=8,
            umumy=40,
        )
        Shoot.objects.create(
            ady='Kerim',
            fam='Saparmyradow',
            topar='221',
            pm1_1=10,
            pm1_2=10,
            pm2_1=10,
            pm2_2=10,
            ak74=10,
            umumy=50,
        )

    def test_reiting_contains_only_girls_in_girls_table_queryset(self):
        response = self.client.get(reverse('reiting'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gyzlaryn reytingi')
        self.assertEqual(list(response.context['gyzlar'].values_list('ady', flat=True)), ['Ayna', 'Bahar'])
        self.assertEqual(list(response.context['gyz_pesler'].values_list('ady', flat=True)), ['Bahar', 'Ayna'])


class SimulyatorViewTests(TestCase):
    def test_simulyator_page_contains_weapon_sections(self):
        response = self.client.get(reverse('simulyator'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PM (Pistolet Makarova)')
        self.assertContains(response, 'AK-74')
        self.assertContains(response, 'SVD')
        self.assertContains(response, 'RPG-7')
        self.assertContains(response, 'simulator-data')
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from . import models


WEAPON_GUIDE = [
    {
        'key': 'pm',
        'title': 'PM (Pistolet Makarova)',
        'subtitle': 'Ykjam hyzmat pistolety',
        'history': [
            'PM 1948-1951-nji yyllarda Nikolay Makarowyn topary tarapyndan duzuldi.',
            '1951-nji yyldan baslap Sowet Goosunynda gulluga alyndy we uzak wagtlap esasy hyzmat pistolety boldy.',
            'Ykjamlygy, ynamlylygy we seretmesi ansatlygy bilen okuw hem gulluk maksatly ulanyldy.',
        ],
        'parts': [
            'Ramka we sap',
            'Stwol',
            'Zatwor',
            'Gaytaryjy prujina',
            'Dukan',
            'Spusk skobasy',
        ],
        'steps': [
            'Dukany ayyr.',
            'Patronhanada ok yokdugyny barla.',
            'Spusk skobasyny asak cek.',
            'Zatwory yza cekip, yokary galdyr we one surr.',
            'Gaytaryjy prujinany stwoldan ayyr.',
        ],
        'assembly': [
            'Prujinany stwola gecir.',
            'Zatwory stwola oturdyp, yza cekip asak dusur.',
            'Spusk skobasyny oz yerine getir.',
            'Dukany oturt we umumy barlag et.',
        ],
        'facts': [
            'Kalibri: 9x18 mm',
            'Isleyis tipi: erkin zatwor',
            'Dukan sygymy: 8 ok',
        ],
    },
    {
        'key': 'ak74',
        'title': 'AK-74',
        'subtitle': 'Avtomatiki atys ulgamy',
        'history': [
            'AK-74 1970-nji yyllarda Mihail Kalasnikowyn ulgamyndan osdurilip tayyarlanyldy.',
            '1974-nji yyldan baslap 5.45x39 mm patron bilen hyzmata girizildi.',
            'Ynamlylygy, uzakdan dolandyrylysy we ansat sokulip-duzulmesi bilen belli boldy.',
        ],
        'parts': [
            'Priklad',
            'Qutynyn korpusy',
            'Qapag',
            'Zatwor ramasy we zatwor',
            'Gaytaryjy mehanizm',
            'Gaz turbasy',
            'Stwol',
            'Dukan',
        ],
        'steps': [
            'Dukany ayyr.',
            'Patronhanany bosadyp, howpsuzlygy barla.',
            'Qutynyn gapagyny ayyr.',
            'Gaytaryjy mehanizmi cikar.',
            'Zatwor ramasy bilen zatwory yza alyp cikar.',
            'Gaz turbasyny ayyr.',
        ],
        'assembly': [
            'Gaz turbasyny yerine oturt.',
            'Zatwor toparyny korpusa sal.',
            'Gaytaryjy mehanizmi yerine gecir.',
            'Qapagyny yap we dukany oturt.',
        ],
        'facts': [
            'Kalibri: 5.45x39 mm',
            'Isleyis tipi: gaz basymsly avtomatika',
            'Dukan sygymy: 30 ok',
        ],
    },
    {
        'key': 'svd',
        'title': 'SVD',
        'subtitle': 'Dragunow snayper tupeni',
        'history': [
            'SVD 1950-nji yyllaryn ahyrynda we 1960-njy yyllaryn basynda Yewgeniy Dragunow tarapyndan islenip duzuldi.',
            '1963-nji yyldan baslap uzak aralykdan nysana almak ucin gulluga kabul edildi.',
            'Ulgam takyk atys, ygtybarlylyk we meydan sertlerinde hyzmat etmek ucin doredildi.',
        ],
        'parts': [
            'Priklad',
            'Qutynyn korpusy',
            'Qapag',
            'Zatwor ramasy we zatwor',
            'Gaytaryjy mehanizm',
            'Gaz turbasy',
            'Stwol',
            'Optiki nysangah',
            'Dukan',
        ],
        'steps': [
            'Howpsuzlyk yagdayyny barla we dukany ayyr.',
            'Patronhanany bosadyp, okuw yolbascysyna gorkez.',
            'Optiki nysangahy goragly yagdayda ayyr.',
            'Qutynyn gapagyny we gaytaryjy mehanizmi ayyr.',
            'Zatwor toparyny korpusdan cykaryp gorkez.',
            'Gaz turbasynyn toparyny ayry gorunusde owren.',
        ],
        'assembly': [
            'Gaz turbasyny we zatwor toparyny yerine oturt.',
            'Gaytaryjy mehanizmi yerlesdir.',
            'Qapagyny yap we optiki nysangahy berkid.',
            'Dukany oturtman umumy okuw barlagyny gecir.',
        ],
        'facts': [
            'Kalibri: 7.62x54R mm',
            'Isleyis tipi: gaz basymsly yarymawtomat',
            'Dukan sygymy: 10 ok',
        ],
    },
    {
        'key': 'rpg',
        'title': 'RPG-7',
        'subtitle': 'El granatomyoty',
        'history': [
            'RPG-7 1960-njy yyllaryn basynda Sowet ulgamynda doredilen el granatomyotydyr.',
            'Yonekey gurlusy we durli okuw meydanlarynda gorkezme serisdeleri hokmunde ginden tanalyar.',
            'Okuw simulyatorynda dine gurlus we howpsuz tanyslyk maksatlary gorkezilyar.',
        ],
        'parts': [
            'Turbaly korpus',
            'Yzky soplo bolegi',
            'Tutawaclar',
            'Nysangah',
            'Spusk mehanizmi',
            'Okuw granatasy gorunusi',
        ],
        'steps': [
            'Okuw yolbascysynyn rugsady bilen howpsuzlyk yagdayyny barla.',
            'Okuw granatasynyn ayrylandygyny tassykla.',
            'Nysangah we tutawac boleklerini ayratyn gorkez.',
            'Spusk mehanizminin dasky yerlesisini owren.',
            'Turbaly korpusy we soplo bolegini ayry gorunusde gorkez.',
        ],
        'assembly': [
            'Turbaly korpusy we soplo bolegini gorkezme yagdayyna getir.',
            'Tutawaclary we nysangahy yerine yerlesdir.',
            'Okuw granatasyny ayratyn saklap, umumy barlag gecir.',
            'Simulyatory ygnalan gorunuse gaytar.',
        ],
        'facts': [
            'Gornusi: el granatomyoty',
            'Ulanylysy: okuwda gurlusy tanatmak',
            'Simulyator: howpsuz gorkezme modeli',
        ],
    },
]


WEAPON_SIMULATOR = {
    'pm': {
        'camera': [0, 2.6, 13],
        'model': {
            'url': '/static/assets/models/makarov-pm/source/makarov.fbx',
            'texture': '/static/assets/models/makarov-pm/textures/DefaultMaterial_Base_color.png',
            'normal': '/static/assets/models/makarov-pm/textures/DefaultMaterial_Normal_OpenGL.png',
            'roughness': '/static/assets/models/makarov-pm/textures/DefaultMaterial_Roughness.png',
            'metalness': '/static/assets/models/makarov-pm/textures/DefaultMaterial_Metallic.png',
            'occlusion': '/static/assets/models/makarov-pm/textures/DefaultMaterial_Mixed_AO.png',
            'assembled_pos': [0.0, 0.05, 0.0],
            'assembled_rot': [0.0, -1.57, 0.0],
            'exploded_pos': [0.0, 0.95, 0.0],
            'exploded_rot': [0.0, -1.57, 0.25],
            'fit': 7.2,
            'metalness_value': 0.48,
            'roughness_value': 0.56,
            'ao_intensity': 0.95,
            'normal_scale': [0.8, 0.8],
        },
        'parts': [
            {'name': 'Ramka', 'shape': 'box', 'size': [5.4, 0.9, 1.2], 'color': 3093061, 'order': 0, 'assembled_pos': [0.0, -0.3, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [-4.5, -1.1, 0.0], 'exploded_rot': [0.0, -0.15, 0.0]},
            {'name': 'Sap', 'shape': 'box', 'size': [1.4, 2.3, 0.95], 'color': 7166767, 'order': 0, 'assembled_pos': [-1.8, -1.4, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [-5.2, -3.0, 0.4], 'exploded_rot': [0.2, 0.3, 0.0]},
            {'name': 'Zatwor', 'shape': 'box', 'size': [5.0, 0.7, 0.95], 'color': 7700620, 'order': 4, 'assembled_pos': [0.2, 0.65, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [4.8, 2.1, 0.0], 'exploded_rot': [0.0, 0.45, 0.0]},
            {'name': 'Stwol', 'shape': 'cylinder', 'size': [0.16, 0.16, 3.4, 24], 'color': 12042763, 'order': 0, 'assembled_pos': [0.7, 0.45, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [2.0, -2.6, 0.0], 'exploded_rot': [0.0, 0.0, 1.57]},
            {'name': 'Prujina', 'shape': 'cylinder', 'size': [0.22, 0.22, 1.8, 18], 'color': 14278115, 'order': 5, 'assembled_pos': [0.85, 0.3, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [6.0, 3.0, 0.0], 'exploded_rot': [0.0, 0.0, 1.57]},
            {'name': 'Dukan', 'shape': 'box', 'size': [1.1, 2.1, 0.6], 'color': 5068384, 'order': 1, 'assembled_pos': [-1.1, -2.3, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [-2.0, -5.0, 0.0], 'exploded_rot': [0.0, 0.0, -0.25]},
        ],
    },
    'ak74': {
        'camera': [0, 3.2, 16],
        'model': {
            'url': '/static/assets/models/ak74/source/Ak_74_Low_Poly.fbx',
            'texture': '/static/assets/models/ak74/textures/T_ak74_base_color_2K.png',
            'normal': '/static/assets/models/ak74/textures/T_ak74_normal_2K.png',
            'roughness': '/static/assets/models/ak74/textures/T_ak74_roughness_2K.png',
            'metalness': '/static/assets/models/ak74/textures/T_ak74_metallic_2K.png',
            'occlusion': '/static/assets/models/ak74/textures/T_ak74_occlusion_2K.png',
            'ao': '/static/assets/models/ak74/textures/internal_ground_ao_texture.jpeg',
            'assembled_pos': [0.0, 0.15, 0.0],
            'assembled_rot': [0.0, -1.57, 0.0],
            'exploded_pos': [0.0, 1.1, 0.0],
            'exploded_rot': [0.0, -1.57, 0.25],
            'fit': 12.0,
            'metalness_value': 0.42,
            'roughness_value': 0.52,
            'ao_intensity': 1.0,
            'normal_scale': [0.82, 0.82],
        },
        'parts': [
            {'name': 'Priklad', 'shape': 'box', 'size': [2.8, 0.8, 1.0], 'color': 8215349, 'order': 0, 'assembled_pos': [-5.2, 0.2, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [-7.5, -1.5, 0.5], 'exploded_rot': [0.0, -0.25, 0.0]},
            {'name': 'Korpus', 'shape': 'box', 'size': [4.4, 1.0, 1.15], 'color': 3093061, 'order': 0, 'assembled_pos': [-1.0, 0.35, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [-1.0, -2.2, 0.0], 'exploded_rot': [0.0, 0.0, 0.0]},
            {'name': 'Qapag', 'shape': 'box', 'size': [4.0, 0.42, 1.0], 'color': 7174277, 'order': 3, 'assembled_pos': [-1.0, 1.1, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [1.5, 3.7, 0.0], 'exploded_rot': [0.0, 0.15, 0.15]},
            {'name': 'Gaytaryjy mehanizm', 'shape': 'cylinder', 'size': [0.18, 0.18, 1.9, 18], 'color': 14147045, 'order': 4, 'assembled_pos': [-2.1, 0.95, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [-0.5, 4.3, 0.0], 'exploded_rot': [0.0, 0.0, 1.57]},
            {'name': 'Zatwor topary', 'shape': 'box', 'size': [2.6, 0.55, 0.65], 'color': 8885153, 'order': 5, 'assembled_pos': [-0.4, 0.9, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [2.6, 4.4, 0.0], 'exploded_rot': [0.0, 0.3, 0.0]},
            {'name': 'Gaz turbasy', 'shape': 'cylinder', 'size': [0.18, 0.18, 3.6, 20], 'color': 9609390, 'order': 6, 'assembled_pos': [2.2, 1.1, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [6.4, 3.0, 0.0], 'exploded_rot': [0.0, 0.0, 1.57]},
            {'name': 'Stwol', 'shape': 'cylinder', 'size': [0.18, 0.18, 5.7, 24], 'color': 11911627, 'order': 0, 'assembled_pos': [4.0, 0.45, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [5.4, -2.1, 0.0], 'exploded_rot': [0.0, 0.0, 1.57]},
            {'name': 'Dukan', 'shape': 'box', 'size': [1.15, 3.0, 0.95], 'color': 6701887, 'order': 1, 'assembled_pos': [0.9, -1.55, 0.1], 'assembled_rot': [0.0, 0.0, -0.35], 'exploded_pos': [0.6, -5.0, 0.0], 'exploded_rot': [0.0, 0.0, -0.55]},
        ],
    },
    'svd': {
        'camera': [0, 3.5, 18],
        'view': {
            'rotX': 0.0,
            'rotY': 0.0,
            'rotZ': 0.0,
            'autoRotate': False,
        },
        'model': {
            'url': '/static/assets/models/svd-dragunov/source/SVD.fbx',
            'texture': '/static/assets/models/svd-dragunov/textures/SVD_low_BaseColor.png',
            'normal': '/static/assets/models/svd-dragunov/textures/SVD_low_Normal.png',
            'roughness': '/static/assets/models/svd-dragunov/textures/SVD_low_Roughness.png',
            'metalness': '/static/assets/models/svd-dragunov/textures/SVD_low_Metallic.png',
            'ao': '/static/assets/models/svd-dragunov/textures/internal_ground_ao_texture.jpeg',
            'assembled_pos': [0.0, 0.15, 0.0],
            'assembled_rot': [1.57, 3.14, 1.57],
            'exploded_pos': [0.0, 1.15, 0.0],
            'exploded_rot': [0.0, -1.57, 0.25],
            'fit': 11.5,
            'metalness_value': 0.78,
            'roughness_value': 0.42,
            'ao_intensity': 0.55,
            'normal_scale': [1.0, 1.00],
        },
        'parts': [
            {'name': 'Priklad', 'shape': 'box', 'size': [3.2, 0.75, 1.0], 'color': 8215349, 'order': 0, 'assembled_pos': [-6.2, 0.05, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [-8.0, -1.7, 0.4], 'exploded_rot': [0.0, -0.25, 0.0]},
            {'name': 'Korpus', 'shape': 'box', 'size': [4.5, 0.92, 1.05], 'color': 3093061, 'order': 0, 'assembled_pos': [-2.0, 0.25, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [-2.2, -2.3, 0.0], 'exploded_rot': [0.0, 0.0, 0.0]},
            {'name': 'Qapag', 'shape': 'box', 'size': [4.1, 0.38, 0.9], 'color': 7174277, 'order': 4, 'assembled_pos': [-2.0, 0.92, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [0.3, 3.8, 0.0], 'exploded_rot': [0.0, 0.15, 0.15]},
            {'name': 'Gaytaryjy mehanizm', 'shape': 'cylinder', 'size': [0.16, 0.16, 2.1, 18], 'color': 14147045, 'order': 4, 'assembled_pos': [-3.0, 0.78, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [-1.0, 4.4, 0.0], 'exploded_rot': [0.0, 0.0, 1.57]},
            {'name': 'Zatwor topary', 'shape': 'box', 'size': [2.7, 0.5, 0.62], 'color': 8885153, 'order': 5, 'assembled_pos': [-1.5, 0.72, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [2.0, 4.5, 0.0], 'exploded_rot': [0.0, 0.3, 0.0]},
            {'name': 'Gaz turbasy', 'shape': 'cylinder', 'size': [0.16, 0.16, 4.0, 20], 'color': 9609390, 'order': 6, 'assembled_pos': [2.0, 0.9, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [5.8, 3.3, 0.0], 'exploded_rot': [0.0, 0.0, 1.57]},
            {'name': 'Stwol', 'shape': 'cylinder', 'size': [0.14, 0.14, 7.4, 24], 'color': 11911627, 'order': 0, 'assembled_pos': [3.8, 0.28, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [5.5, -2.3, 0.0], 'exploded_rot': [0.0, 0.0, 1.57]},
            {'name': 'Optika', 'shape': 'box', 'size': [2.1, 0.45, 0.45], 'color': 2772305, 'order': 3, 'assembled_pos': [-2.2, 1.55, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [-4.8, 3.8, 0.3], 'exploded_rot': [0.0, 0.25, 0.0]},
            {'name': 'Dukan', 'shape': 'box', 'size': [1.0, 2.5, 0.85], 'color': 6701887, 'order': 1, 'assembled_pos': [-0.8, -1.35, 0.1], 'assembled_rot': [0.0, 0.0, -0.18], 'exploded_pos': [-0.8, -5.0, 0.0], 'exploded_rot': [0.0, 0.0, -0.45]},
        ],
    },
    'rpg': {
        'camera': [0, 3.3, 17],
        'model': {
            'url': '/static/assets/models/rpg-7/source/RPG-7WithRocket.fbx',
            'texture': '/static/assets/models/rpg-7/textures/RPG-7_BaseColor.png',
            'normal': '/static/assets/models/rpg-7/textures/RPG-7_Normal.png',
            'roughness': '/static/assets/models/rpg-7/textures/RPG-7_Roughness.png',
            'metalness': '/static/assets/models/rpg-7/textures/RPG-7_Metallic.png',
            'occlusion': '/static/assets/models/rpg-7/textures/RPG-7_AO.png',
            'assembled_pos': [0.0, 0.2, 0.0],
            'assembled_rot': [0.0, -1.57, 0.0],
            'exploded_pos': [0.0, 1.05, 0.0],
            'exploded_rot': [0.0, -1.57, 0.2],
            'fit': 13.2,
            'metalness_value': 0.45,
            'roughness_value': 0.55,
            'ao_intensity': 0.95,
            'normal_scale': [0.78, 0.78],
            'materials': [
                {
                    'match': ['rocket'],
                    'texture': '/static/assets/models/rpg-7/textures/RPG-7_Rocket_BaseColor.png',
                    'normal': '/static/assets/models/rpg-7/textures/RPG-7_Rocket_Normal.png',
                    'roughness': '/static/assets/models/rpg-7/textures/RPG-7_Rocket_Roughness.png',
                    'metalness': '/static/assets/models/rpg-7/textures/RPG-7_Rocket_Metallic.png',
                    'occlusion': '/static/assets/models/rpg-7/textures/RPG-7_Rocket_AO.png',
                    'metalness_value': 0.5,
                    'roughness_value': 0.48,
                },
                {
                    'match': ['rpg-7'],
                    'texture': '/static/assets/models/rpg-7/textures/RPG-7_BaseColor.png',
                    'normal': '/static/assets/models/rpg-7/textures/RPG-7_Normal.png',
                    'roughness': '/static/assets/models/rpg-7/textures/RPG-7_Roughness.png',
                    'metalness': '/static/assets/models/rpg-7/textures/RPG-7_Metallic.png',
                    'occlusion': '/static/assets/models/rpg-7/textures/RPG-7_AO.png',
                },
            ],
        },
        'parts': [
            {'name': 'Turbaly korpus', 'shape': 'cylinder', 'size': [0.42, 0.42, 8.6, 32], 'color': 4802889, 'order': 0, 'assembled_pos': [0.0, 0.3, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [0.0, -1.8, 0.0], 'exploded_rot': [0.0, 0.0, 1.57]},
            {'name': 'Yzky soplo', 'shape': 'cylinder', 'size': [0.7, 0.5, 1.0, 32], 'color': 5987163, 'order': 5, 'assembled_pos': [-4.8, 0.3, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [-7.0, 2.8, 0.0], 'exploded_rot': [0.0, 0.25, 1.57]},
            {'name': 'On tutawac', 'shape': 'box', 'size': [0.45, 1.55, 0.55], 'color': 8215349, 'order': 3, 'assembled_pos': [0.7, -0.85, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [2.6, -4.1, 0.0], 'exploded_rot': [0.0, 0.0, 0.25]},
            {'name': 'Yzky tutawac', 'shape': 'box', 'size': [0.55, 1.75, 0.6], 'color': 8215349, 'order': 3, 'assembled_pos': [-1.6, -0.95, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [-3.1, -4.3, 0.0], 'exploded_rot': [0.0, 0.0, -0.25]},
            {'name': 'Nysangah', 'shape': 'box', 'size': [1.25, 0.45, 0.45], 'color': 2772305, 'order': 3, 'assembled_pos': [1.6, 1.0, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [3.8, 3.6, 0.0], 'exploded_rot': [0.0, 0.35, 0.0]},
            {'name': 'Spusk mehanizmi', 'shape': 'box', 'size': [1.0, 0.55, 0.65], 'color': 3093061, 'order': 4, 'assembled_pos': [-0.7, -0.45, 0.0], 'assembled_rot': [0.0, 0.0, 0.0], 'exploded_pos': [-0.4, -5.1, 0.0], 'exploded_rot': [0.0, 0.2, 0.0]},
            {'name': 'Okuw granatasy', 'shape': 'cylinder', 'size': [0.55, 0.35, 2.0, 32], 'color': 7695228, 'order': 2, 'assembled_pos': [5.2, 0.3, 0.0], 'assembled_rot': [0.0, 0.0, 1.57], 'exploded_pos': [6.5, -2.7, 0.0], 'exploded_rot': [0.0, 0.0, 1.57]},
        ],
    },
}


def login_page(r):
    if r.method == 'POST':
        username = r.POST.get('username')
        password = r.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(r, user)
            return redirect('home')
        messages.error(r, 'Nadogry parol ya-da ulanjy! ')
    return render(r, 'login.html')


def regis(r):
    if r.method == 'POST':
        username = r.POST.get('usr')
        first_name = r.POST.get('at')
        last_name = r.POST.get('fam')
        password = r.POST.get('pswd')
        confirm_password = r.POST.get('pswd2')
        if password == confirm_password:
            User.objects.create_user(
                username=username,
                password=password,
                last_name=last_name,
                first_name=first_name,
            )
            messages.error(r, 'Doredildi!')
        else:
            messages.error(r, 'Doredilmedi!')
    return render(r, 'regis.html')


def logout_page(r):
    logout(r)
    return redirect('login')


def home(r):
    user = r.user
    selected_topar = r.GET.get('topar', '').strip()
    toparlar = models.Shoot.objects.order_by('topar').values_list('topar', flat=True).distinct()
    conts = models.Shoot.objects.all()

    if selected_topar:
        conts = conts.filter(topar=selected_topar)

    conts = conts.order_by('topar', 'fam', 'ady')
    context = {
        'conts': conts,
        'user': user,
        'toparlar': toparlar,
        'selected_topar': selected_topar,
    }
    return render(r, 'index.html', context)


def reiting(r):
    user = r.user
    conts = models.Shoot.objects.all().order_by('-umumy')[:5]
    pesler = models.Shoot.objects.all().order_by('umumy')[:5]
    gyzlar = models.Shoot.objects.filter(fam__iendswith='a').order_by('-umumy')[:5]
    gyz_pesler = models.Shoot.objects.filter(fam__iendswith='a').order_by('umumy')[:5]
    context = {
        'conts': conts,
        'user': user,
        'pesler': pesler,
        'gyzlar': gyzlar,
        'gyz_pesler': gyz_pesler,
    }
    return render(r, 'reiting.html', context)


def simulyator(r):
    default_weapon = 'ak74'
    default_weapon_info = next((weapon for weapon in WEAPON_GUIDE if weapon['key'] == default_weapon), WEAPON_GUIDE[0])
    viewer_data = {}
    skipped_viewer_keys = {'order', 'exploded_pos', 'exploded_rot'}

    for weapon_key, config in WEAPON_SIMULATOR.items():
        viewer_config = {
            'camera': config['camera'],
            'parts': [],
        }
        if 'view' in config:
            viewer_config['view'] = config['view']

        if 'model' in config:
            viewer_config['model'] = {
                key: value
                for key, value in config['model'].items()
                if key not in skipped_viewer_keys
            }

        for part in config.get('parts', []):
            viewer_config['parts'].append({
                key: value
                for key, value in part.items()
                if key not in skipped_viewer_keys
            })

        viewer_data[weapon_key] = viewer_config

    context = {
        'user': r.user,
        'weapons': WEAPON_GUIDE,
        'simulator_data': viewer_data,
        'default_weapon': default_weapon,
        'default_weapon_title': default_weapon_info['title'],
    }
    return render(r, 'simulyator.html', context)


@login_required
def create(r):
    if r.method == "POST":
        at = r.POST.get('at')
        fam = r.POST.get('fam')
        topar = r.POST.get('topar')
        pm1_1 = r.POST.get('pm1_1')
        pm1_2 = r.POST.get('pm1_2')
        pm2_1 = r.POST.get('pm2_1')
        pm2_2 = r.POST.get('pm2_2')
        ak74 = r.POST.get('ak74')
        umumy = int(pm1_1) + int(pm1_2) + int(pm2_1) + int(pm2_2) + int(ak74)

        models.Shoot.objects.create(
            ady=at,
            fam=fam,
            topar=topar,
            pm1_1=pm1_1,
            pm1_2=pm1_2,
            pm2_1=pm2_1,
            pm2_2=pm2_2,
            ak74=ak74,
            umumy=umumy,
        )
        return redirect('home')
    return render(r, 'create.html')


@login_required
def edit(r, id):
    shot = models.Shoot.objects.get(id=id)
    context = {
        'shot': shot,
    }
    if r.method == "POST":
        at = r.POST.get('at')
        fam = r.POST.get('fam')
        topar = r.POST.get('topar')
        pm1_1 = r.POST.get('pm1_1')
        pm1_2 = r.POST.get('pm1_2')
        pm2_1 = r.POST.get('pm2_1')
        pm2_2 = r.POST.get('pm2_2')
        ak74 = r.POST.get('ak74')

        shot.umumy = int(pm1_1) + int(pm1_2) + int(pm2_1) + int(pm2_2) + int(ak74)
        shot.ady = at
        shot.fam = fam
        shot.topar = topar
        shot.pm1_1 = pm1_1
        shot.pm1_2 = pm1_2
        shot.pm2_1 = pm2_1
        shot.pm2_2 = pm2_2
        shot.ak74 = ak74
        shot.save()
        return redirect('home')
    return render(r, 'edit.html', context)


@login_required
def delete(r, id):
    c = models.Shoot.objects.get(id=id)
    c.delete()
    return redirect('home')
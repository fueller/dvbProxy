#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()

import time
import os
import requests
import sys
from gevent.pywsgi import WSGIServer
from flask import Flask, Response, request, jsonify, abort, render_template

import untangle
import code

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

# URL format: <protocol>://<username>:<password>@<hostname>:<port>, example: https://test:1234@localhost:9981
config = {
    'bindAddr': os.environ.get('DVB_BINDADDR') or '',
    'dvbURL': os.environ.get('DVB_URL') or 'http://192.168.1.11:8100',
    'dvbStreamURL': os.environ.get('DVB_STREAM_URL') or 'http://192.168.1.11:8101',
    'dvbProxyURL': os.environ.get('DVB_PROXY_URL') or 'http://localhost',
    'tunerCount': os.environ.get('DVB_TUNER_COUNT') or 6,  # number of tuners in DVBLink
    'dvbWeight': os.environ.get('DVB_WEIGHT') or 300,  # subscription priority
    'chunkSize': os.environ.get('DVB_CHUNK_SIZE') or 1024*1024,  # usually you don't need to edit this
    'streamProfile': os.environ.get('DVB_PROFILE') or 'pass'  # specifiy a stream profile that you want to use for adhoc transcoding in DVBLink, e.g. mp4
}

discoverData = {
    'FriendlyName': 'dvbProxy',
    'Manufacturer' : 'Silicondust',
    'ModelNumber': 'HDTC-2US',
    'FirmwareName': 'hdhomeruntc_atsc',
    'TunerCount': int(config['tunerCount']),
    'FirmwareVersion': '20150826',
    'DeviceID': '12345678',
    'DeviceAuth': 'test1234',
    'BaseURL': '%s' % config['dvbProxyURL'],
    'LineupURL': '%s/lineup.json' % config['dvbProxyURL']
}

@app.route('/discover.json')
def discover():
    return jsonify(discoverData)


@app.route('/lineup_status.json')
def status():
    return jsonify({
        'ScanInProgress': 0,
        'ScanPossible': 1,
        'Source': "Cable",
        'SourceList': ['Cable', 'Satellite']
    })


@app.route('/lineup.json')
def lineup():
    lineup = []

    for c in _get_channels():
        if c['enabled']:
            url = '%s/dvblink/direct?channel=%s' % (config['dvbURL'], c['id'])

            lineup.append({'GuideNumber': str(c['number']),
                           'GuideName': c['name'],
                           'URL': url
                           })

    return jsonify(lineup)


@app.route('/lineup.post', methods=['GET', 'POST'])
def lineup_post():
    return ''

@app.route('/')
@app.route('/device.xml')
def device():
    return render_template('device.xml',data = discoverData),{'Content-Type': 'application/xml'}


def _get_channels():
    url = '%s/api/channel/grid?start=0&limit=999999' % config['dvbURL']
    url = '%s/cs/' % config['dvbURL']
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = {'command': 'get_channels'}

    try:
        r = requests.post(url, headers=headers, data=data)
        tree = untangle.parse(r.content)
        d = tree.response.xml_result.cdata
        dd = untangle.parse(d)

        entries = []

        for channel in dd.channels.channel:
            if int(channel.channel_number.cdata) > 0:
                entries.append({'enabled': True,
                                'id': channel.channel_id.cdata,
                                'dvblink_id': channel.channel_dvblink_id.cdata,
                                'name': channel.channel_name.cdata,
                                'logo': channel.channel_logo.cdata,
                                'type': channel.channel_type.cdata,
                                'number': channel.channel_number.cdata,
                                'subnumber': channel.channel_subnumber.cdata})

        return entries

    except Exception as e:
        print('An error occured: ' + repr(e))


if __name__ == '__main__':
    http = WSGIServer((config['bindAddr'], 5004), app.wsgi_app)
    http.serve_forever()

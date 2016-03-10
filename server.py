#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import StringIO
except ImportError:
    from io import StringIO

import os
import yaml

from flask import Flask, render_template, request
from PIL import Image, ImageFont, ImageDraw


class ZeApp(Flask):

    def __init__(self, *args, **kwargs):
        super(ZeApp, self).__init__(__name__, *args, **kwargs)
        self.settings = {}

    def load_config(self, path='config.yml'):
        with open(path, 'r') as f:
            self.settings = yaml.load(f)
            self.debug = self.settings.get('debug', False)

    def run(self):
        if not self.settings:
            self.load_config()

        port = self.settings.get('port', 8000)
        super(ZeApp, self).run(host='0.0.0.0', port=port)


app = ZeApp()


def generate_image(color, image, nick, lane):
    path_im = app.settings.get('image_path_format') % {'color': color, 'image': image}

    if os.path.exists(path_im):
        nick_cfg = app.settings.get('nick')
        lane_cfg = app.settings.get('lane')

        img = Image.open(path_im)
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype(nick_cfg['font_path'], nick_cfg['font_size'])
        draw.text((nick_cfg['text_x'], nick_cfg['text_y']), nick, (255, 255, 255), font=font)

        font = ImageFont.truetype(lane_cfg['font_path'], lane_cfg['font_size'])
        draw.text((lane_cfg['text_x'], lane_cfg['text_y']), lane, (255, 255, 255), font=font)

        output = StringIO.StringIO()
        img.save(output, format='PNG')
        im = output.getvalue()
        output.close()

        return im

    return None


@app.route('/')
def index():
    context = {
        'site_name': app.settings.get('site_name'),
        'colors': app.settings.get('colors'),
        'images': app.settings.get('images'),
        'ga': app.settings.get('ga'),
    }
    return render_template('index.html', **context)


@app.route('/sample/<color>/<image>')
def sample(color=None, image=None):
    path_im = app.settings.get('image_path_format') % {'color': color, 'image': image}

    if os.path.exists(path_im):
        with open(path_im) as f:
            headers = {
                'Content-Type': 'image/png',
            }
            return f.read(), 200, headers

    return '', 404


@app.route('/generate', methods=['POST'])
def generate():
    nick = request.form.get('nick')
    lane = request.form.get('lane')
    color = request.form.get('color')
    image = request.form.get('image')

    try:
        im = generate_image(color, image, nick, lane)
    except:
        pass
    else:
        if im:
            headers = {
                'Content-Type': 'image/png',
                'Content-Disposition': 'attachment; filename="cover.png"',
            }
            return im, 200, headers

    context = {
        'site_name': app.settings.get('site_name'),
        'colors': app.settings.get('colors'),
        'images': app.settings.get('images'),
        'ga': app.settings.get('ga'),
        'message': 'Erro ao gerar imagem',
        'message_type': 'danger',
    }
    return render_template('index.html', **context)

if __name__ == "__main__":
    app.run()

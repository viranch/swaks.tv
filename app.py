import urllib,json
from flask import Flask, render_template, request

from resources.lib.indexers import movies
from resources.lib.indexers import tvshows
from resources.lib.indexers import episodes
from resources.lib.sources import sources

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', movie_genres=movies.movies().genres(), tvshow_genres=tvshows.tvshows().genres())

@app.route('/movies/')
def movies_navigator():
    args = request.args
    m = movies.movies()
    url = args.get('url')
    if 'genre' in args:
        url = m.genre_link % args['genre']

    data = m.get(url)
    for movie in data:
        meta = dict((k,v) for k, v in movie.iteritems() if not v == '0')
        meta.update({'mediatype': 'movie'})
        meta.update({'trailer': '%s (%s)' % (movie['title'], movie['year'])})
        if not 'duration' in movie: meta.update({'duration': '120'})
        elif movie['duration'] == '0': meta.update({'duration': '120'})
        try: meta.update({'duration': str(int(meta['duration']) * 60)})
        except: pass
        try: meta.update({'genre': meta['genre']})
        except: pass

        movie['play_qs'] = urllib.urlencode({
            'title': movie['title'],
            'year': movie['year'],
            'imdb': movie['imdb'],
            'meta': json.dumps(meta),
            't': m.systime
        })
        movie['_swaks_label'] = '%s (%s)' % (movie['title'], movie['year'])

    return render_template('list.html', items=data)

@app.route('/tvshows/')
def tvshows_navigator():
    args = request.args
    data = []
    if 'genre' in args or 'url' in args:
        t = tvshows.tvshows()
        url = args.get('url')
        if 'genre' in args:
            url = t.genre_link % args['genre']

        data = t.get(url, False)
        for show in data:
            show['href_qs'] = urllib.urlencode({
                'tvshowtitle': show['originaltitle'],
                'year': show['year'],
                'imdb': show['imdb'],
                'tvdb': show['tvdb']
            })
            show['_swaks_label'] = show['title']
    elif 'tvshowtitle' in args:
        if 'season' in args:
            title, year, imdb, tvdb, season = args['tvshowtitle'], args['year'], args['imdb'], args['tvdb'], args['season']
            e = episodes.episodes()
            data = e.get(title, year, imdb, tvdb, season)
            for item in data:
                meta = dict((k,v) for k, v in item.iteritems() if not v == '0')
                meta.update({'mediatype': 'episode'})
                meta.update({'trailer': item['tvshowtitle']})
                if not 'duration' in item: meta.update({'duration': '60'})
                elif item['duration'] == '0': meta.update({'duration': '60'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                try: meta.update({'genre': meta['genre']})
                except: pass
                try: meta.update({'title': item['label']})
                except: pass

                item['play_qs'] = urllib.urlencode({
                    'title': item['title'],
                    'year': item['year'],
                    'imdb': item['imdb'],
                    'tvdb': item['tvdb'],
                    'season': item['season'],
                    'episode': item['episode'],
                    'tvshowtitle': item['tvshowtitle'],
                    'premiered': item['premiered'],
                    'meta': json.dumps(meta),
                    't': e.systime
                })
                item['_swaks_label'] = item.get('label', item['title'])
                item['_swaks_label'] = '%sx%02d . %s' % (item['season'], int(item['episode']), item['_swaks_label'])
        else:
            title, year, imdb, tvdb = args['tvshowtitle'], args['year'], args['imdb'], args['tvdb']
            data = episodes.seasons().get(title, year, imdb, tvdb, False)
            for item in data:
                item['href_qs'] = urllib.urlencode({
                    'tvshowtitle': item['tvshowtitle'],
                    'year': item['year'],
                    'imdb': item['imdb'],
                    'tvdb': item['tvdb'],
                    'season': item['season']
                })
                item['_swaks_label'] = 'Season %s' % item['season']

    return render_template('list.html', items=data)

@app.route('/movies/play/')
@app.route('/tvshows/play/')
def play():
    # args = dict((k,v) for k, v in request.args.iteritems())
    args = request.args
    # print sources().play()
    return 'Hi'
    # return render_template('play.html')

app.run()
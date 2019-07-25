import json
import random
import string

import httplib2
import requests
from flask import Flask, render_template, request, redirect,\
    jsonify, url_for, flash, session as login_session, make_response
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from crud_functions import category_listing, item_listing,\
    category_create, get_category, category_update, category_delete,\
    category_item_listing, item_create, get_item, item_save, item_delete
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json').read())['web']['client_id']


@app.route('/')
def show_categories():
    categories = category_listing()
    last_items = item_listing()[:9]
    return render_template('category.html',
                           categories=categories, items=last_items,
                           username=login_session.get('username', None),
                           user_picture=login_session.get('picture', None))


@app.route('/category/new/', methods=['GET', 'POST'])
def add_category():
    if not login_session.get('username'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        is_published = request.form.get('is_published', False)
        if not is_published:
            is_published = True
        category = category_create(name=request.form['name'],
                                   is_published=is_published)
        flash('New Category %s Successfully Created' % category.name)
        return redirect(url_for('show_categories'))
    else:
        return render_template('category_form.html')


@app.route('/category/<string:category_name>/edit/', methods=['GET', 'POST'])
def category_edit(category_name):
    if not login_session.get('username'):
        return redirect(url_for('login'))
    category = get_category(name=category_name)

    if request.method == 'POST':
        is_published = request.form.get('is_published', False)
        if not is_published:
            is_published = True
        category_update(category.id, request.form['name'],
                        is_published=is_published)
        flash('Category Successfully Edited %s' % category.name)
        return redirect(url_for('show_categories'))
    else:
        return render_template('category_form.html', category=category)


@app.route('/category/<string:category_name>/delete/', methods=['GET', 'POST'])
def delete_category(category_name):
    if not login_session.get('username'):
        return redirect(url_for('login'))
    category = get_category(name=category_name)
    if request.method == 'POST':
        category_delete(id=category.id)
        flash('%s Successfully Deleted' % category.name)
        return redirect(url_for('show_categories'))
    else:
        return render_template('category_delete.html', category=category)


@app.route('/category/<string:category_name>/')
@app.route('/category/<string:category_name>/items/')
def show_category_items(category_name):
    category = get_category(category_name)
    items = category_item_listing(category_id=category.id)
    return render_template('category.html', category=category, items=items)


@app.route('/category/JSON')
def category_json():
    categories = category_listing()
    categories_json = [c.serialize for c in categories]
    for cat in categories_json:
        if category_item_listing(category_id=cat['id']).count() > 0:  # noqa
            cat['items'] = [i.serialize for i in category_item_listing(category_id=cat['id'])]  # noqa
    return jsonify(categories_json)


@app.route('/item/new/', methods=['GET', 'POST'])
def add_item():
    if not login_session.get('username'):
        return redirect(url_for('login'))
    categories = category_listing()
    if request.method == 'POST':
        item = item_create(category_id=request.form['category_id'],
                           name=request.form['name'],
                           description=request.form['description'])
        flash('New %s Item Successfully Created' % item.name)
        return redirect(url_for('show_categories'))
    else:
        return render_template('item_form.html', categories=categories)


@app.route('/item/<string:item_name>/edit', methods=['GET', 'POST'])
def edit_item(item_name):
    if not login_session.get('username'):
        return redirect(url_for('login'))
    categories = category_listing()
    item = get_item(item_name)
    if request.method == 'POST':
        if request.form.get('name', None):
            item.name = request.form['name']
        if request.form.get('description', None):
            item.description = request.form['description']
        if request.form.get('category_id', None):
            item.category_id = request.form['category_id']
        item_save(item)
        flash('New %s Item Successfully Updated' % (item.name))
        return redirect(url_for('show_categories'))
    else:
        return render_template('item_form.html',
                               categories=categories, item=item)


@app.route('/item/<string:item_name>/', methods=['GET'])
def item_details(item_name):
    return render_template('item_details.html', item=get_item(item_name))


@app.route('/item/<string:item_name>/delete', methods=['GET', 'POST'])
def delete_item(item_name):
    if not login_session.get('username'):
        return redirect(url_for('login'))
    item = get_item(name=item_name)
    if request.method == 'POST':
        item_delete(id=item.id)
        flash('%s Successfully Deleted' % item.name)
        return redirect(url_for('show_categories'))
    else:
        return render_template('item_delete.html', item=item)


@app.route('/login')
def login():
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (  # noqa
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    url = 'https://graph.facebook.com/v2.8/me?fields=id%2Cname%2Cemail%2Cpicture&access_token=' + access_token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['access_token'] = access_token
    login_session['picture'] = data["picture"]["data"]["url"]

    flash("Now logged in as %s" % login_session['username'], 'success')
    return login_session['username']

# disconnect FB login
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # noqa
    h = httplib2.Http()
    h.request(url, 'DELETE')[1]
    return "you have been logged out"


# CONNECT - Google login get token
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data.decode('utf-8')

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed - authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_gplus_id = login_session.get('gplus_id')
    if gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    login_session['access_token'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    flash("you are now logged in as %s" % login_session['username'], 'success')
    return login_session['username']


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # only disconnect a connected user
    credentials = json.loads(login_session.get('access_token'))
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    # execute HTTP GET request to revoke current token
    print credentials['access_token']
    access_token = credentials['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # token given is invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/logout')
def logout():
    if 'username' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        elif login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
            del login_session['access_token']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']

        flash("You have been successfully logged out!")
        return redirect(url_for('show_categories'))
    else:
        flash("You were not logged in!")
        return redirect(url_for('show_categories'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

from . import client

def _idisint(id):
    if not isinstance(id, int):
        raise TypeError('the id must be int, not {!r}'.format(id.__class__.__name__))

def _get(client, path, id):
    _idisint(id)
    return client.get(path % id)

def basic(client, id):
    """ Gets basic data about an staff
    
    :param client: an instance of a :class:`Client <Client>`
    :param id: the id to get
    :return: the json answer of the API
    :rtype: str
    """
    return _get(client, 'staff/%d', id)

def page(client, id):
    """ Gets all data about an staff to display a page with all related data
    
    :param client: an instance of a :class:`Client <Client>`
    :param id: the id to get
    :return: the json answer of the API
    :rtype: str
    """
    return _get(client, 'staff/%d/page', id)

def favourite(client, id):
    """ Toggles the favourite status of an staff

    :param client: an instance of a :class:`Client <Client>`
    :param id: the id
    :return: "Favourite Added" || "Favourite Removed"
    :rtype: str
    """
    _idisint(id)
    client.hasLogin()
    return client.post('staff/favourite', data={ 'id' : id })

def search(client, query):
    """ Searches an staff by its name
    
    :param client: an instance of a :class:`Client <Client>`
    :param query: string to search for
    :return: json string
    :rtype: str
    """
    return client.get('staff/search/%s' % query)

from oslo_config import cfg
import keystoneauth1.identity.v3
import keystoneauth1.session
import requests
import yaml

__all__ = ['get_documents']

_DECKHAND_PREFIX = 'deckhand+'


def get_documents(design_ref):
    if design_ref.startswith(_DECKHAND_PREFIX):
        response = _get_from_deckhand(design_ref)
    else:
        response = _get_from_basic_web(design_ref)

    response.raise_for_status()

    return list(yaml.safe_load_all(response.text))


def _get_from_basic_web(design_ref):
    return requests.get(design_ref)


def _get_from_deckhand(design_ref):
    auth = keystoneauth1.identity.v3.Password(**cfg.CONF.keystone_authtoken)
    session = keystoneauth1.session.Session(auth=auth)

    return session.get(design_ref[len(_DECKHAND_PREFIX):])

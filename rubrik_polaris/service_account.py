import json
import re
from pathlib import Path
from typing import Optional, Tuple, Dict, Union

from requests import post

from .config import get_conf_val


class BaseUrl:
    """Represents the base URL of a Rubrik instance.

    Typically, for an account `my-account`, the base url is:
    https://my-account.my.rubrik.com/api

    """

    def __init__(self, baseurl: str):
        self.baseurl = baseurl

    @classmethod
    def from_domain(cls, domain: str, root_domain: str = 'my.rubrik.com'):
        return BaseUrl(f'https://{domain}.{root_domain}/api')

    @classmethod
    def from_access_token_uri(cls, access_token_uri: str):
        return BaseUrl(re.sub(r'/client_token', '', access_token_uri))

    def __str__(self) -> str:
        return self.baseurl

    def access_token_uri(self) -> str:
        return f'{self.baseurl}/client_token'


class ServiceAccount:
    """A Rubrik service account."""

    def __init__(
            self,
            name: str,
            client_id: str,
            client_secret: str,
            access_token_uri: str):
        """A Rubrik service account.

        :param name: service account name (as entered in the UI).
               Example value:
               'my service account'
        :param client_id: service account client id.
               Example value:
               'client|rjSOLdenk7gtFWSnSiSgX4G1SprdkF6I'
        :param client_secret: service account client secret
               Example value:
               'qzY2TtYxPB0WYvqviWtHvK2w5P3wvQ39YXTPpIAEZCxLkSkfDCE0IV4DTWu3_o2S'
        :param access_token_uri: access token URI
               Example value:
               'https://my-account.my.rubrik.com/api/client_token'
        """
        self.name: str = name
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.access_token_uri: str = access_token_uri
        self.baseurl: BaseUrl = BaseUrl.from_access_token_uri(access_token_uri)

    @classmethod
    def from_json(cls, d: Dict[str, str]) -> 'ServiceAccount':
        """Make a ServiceAccount object from a JSON-like dict."""
        return ServiceAccount(
            name=d['name'],
            client_id=d['client_id'],
            client_secret=d['client_secret'],
            access_token_uri=d['access_token_uri']
        )

    @classmethod
    def from_json_file(cls, path: Union[str, Path]) -> 'ServiceAccount':
        """Make a ServiceAccount object from a JSON file."""
        with Path(path).expanduser().open() as f:
            return ServiceAccount.from_json(json.load(f))

    @classmethod
    def from_env(cls,
                 name: str,
                 client_id_override: Optional[str] = None,
                 client_secret_override: Optional[str] = None,
                 domain_override: Optional[str] = None,
                 root_domain_override: Optional[str] = None,
                 ) -> 'ServiceAccount':
        """Make a ServiceAccount object from environment variables and
           argument overrides.

           see: get_conf_val for info on environment variables.
        """
        baseurl = BaseUrl.from_domain(
            get_conf_val('domain', domain_override),
            get_conf_val('root_domain', root_domain_override,
                         'my.rubrik.com')
        )
        return ServiceAccount(
            name=name,
            client_id=get_conf_val('client_id', client_id_override),
            client_secret=get_conf_val('client_secret', client_secret_override),
            access_token_uri=baseurl.access_token_uri()
        )

    def get_token(self) -> str:
        """Retrieve a client access token using a service account.

        :return: client access token.
        """

        r = post(
            url=self.access_token_uri,
            json=dict(
                client_id=self.client_id,
                client_secret=self.client_secret,
                name=self.name
            ),
            headers={
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json, text/plain'
            }
        )
        r.raise_for_status()  # raise only if 4xx or 5xx error.
        session: Dict[str] = r.json()
        assert session['client_id'] == self.client_id
        return session['access_token']

    def get_appliance_token(self, appliance_uuid: str) \
            -> Tuple[str, str, str]:
        """Create a session on a given appliance with a service account,
        retrieve client access token for it.

        Notes:
        - this function does not use username & password credentials, but a
          service account instead. The appliance session can be created here
          without any active Rubrik session.
        - the service account must have sufficient permissions to access the
          appliance.
        - the appliance must be registered with the current Rubrik instance.
        - see list_cdm_clusters to retrieve your cluster ID.

        :param appliance_uuid: Appliance or cluster UUID.
               Example value:
               '40505837-9772-4a91-a18a-db6108c66b59'
        :return: tuple of 3 strings: session id, token and expiration date.

        Response example: (client_id, client_token, expiration) with:
            client_id = '009e7254-3e1b-4bef-a06a-6a0dc63cb6fe'
            client_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmNjFk'\
                    'N2RkNS1mN2M4LTQ3MDEtYWFiOS00ZGJmZDkxN2IwMmNfY2xpZW50fHJqU09M'\
                    'ZGVuazdndEZXU25TaVNnWDRHMVNwcmRrRjZJIiwiaXNNZmFSZW1lbWJlclRv'\
                    'a2VuIjpmYWxzZSwiaXNzIjoiZjYxZDdkZDUtZjdjOC00NzAxLWFhYjktNGRi'\
                    'ZmQ5MTdiMDJjIiwiaWF0IjoxNjM2MDY4OTUxLCJqdGkiOiIwMDllNzI1NC0z'\
                    'ZTFiLTRiZWYtYTA2YS02YTBkYzYzY2I2ZmUifQ.jTVcmpfF9jh1u4O69Yp2M'\
                    'GmcXOP8cxTO2TwKfXEP13U'
            expiration = '2021-11-05T23:35:51Z'
        """
        r = post(
            url=f'{self.baseurl}/cdm_client_token',
            json=dict(
                client_id=self.client_id,
                client_secret=self.client_secret,
                cluster_uuid=appliance_uuid,
            ),
        )
        r.raise_for_status()  # raise only if 4xx or 5xx error.
        session: Dict[str] = r.json()['session']
        return session['id'], session['token'], session['expiration']

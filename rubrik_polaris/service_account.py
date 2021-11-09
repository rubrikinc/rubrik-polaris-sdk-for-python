import json
import re
from typing import Optional, Tuple, Dict
from requests import post
from .config import get_conf_val


class BaseUrl:
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

class ServiceAccount:
    def __init__(
            self,
            client_id: str,
            client_secret: str,
            baseurl: BaseUrl,
            **kwargs):
        """A Polaris service account.

        :param client_id: Polaris service account client id.
               Example value:
               'client|rjSOLdenk7gtFWSnSiSgX4G1SprdkF6I'
        :param client_secret: Polaris service account client secret
               Example value:
               'qzY2TtYxPB0WYvqviWtHvK2w5P3wvQ39YXTPpIAEZCxLkSkfDCE0IV4DTWu3_o2S'
        :param domain: Polaris domain. If not given here, must be given as
               environment variable 'rubrik_polaris_domain'.
               Example value:
               'my-company'
        :param kwargs: uncommon options:
               - kwargs['root_domain'] to change Polaris root domain.
                 Default: 'my.rubrik.com'

        """
        self.client_id: str = get_conf_val('client_id', client_id)
        self.client_secret: str = get_conf_val('client_secret', client_secret)
        self.baseurl: BaseUrl = baseurl
        self._access_token_uri: Optional[str] = kwargs.get(
            'access_token_uri', f'https://{self.baseurl}/client_token')

    @classmethod
    def from_json(cls, d: Dict[str]) -> 'ServiceAccount':
        return ServiceAccount(
            client_id=d['client_id'],
            client_secret=d['client_secret'],
            baseurl=BaseUrl.from_access_token_uri(d['access_token_uri']),
            access_token_uri=d['access_token_uri'],
        )

    @classmethod
    def from_json_file(cls, path) -> 'ServiceAccount':
        with open(path) as f:
            return ServiceAccount.from_json(json.load(f))

    @classmethod
    def from_env(cls,
                 client_id_override: Optional[str] = None,
                 client_secret_override: Optional[str] = None,
                 domain_override: Optional[str] = None,
                 root_domain_override: Optional[str] = None,
                 ) -> 'ServiceAccount':
        return ServiceAccount(
            client_id=get_conf_val('client_id', client_id_override),
            client_secret=get_conf_val('client_secret', client_secret_override),
            baseurl=BaseUrl.from_domain(
                get_conf_val('domain', domain_override),
                get_conf_val('root_domain', root_domain_override,
                             'my.rubrik.com')
            )
        )

    def get_client_token(self) -> str:
        """Retrieve a client access token using a service account.

        :return: client access token.
        """

        r = post(
            url=self._access_token_uri,
            data=dict(
                client_id=self.client_id,
                client_secret=self.client_secret,
            ),
        )
        r.raise_for_status()  # raise only if 4xx or 5xx error.
        session: Dict[str] = r.json()
        assert session['client_id'] == self.client_id
        return session['access_token']

    def get_cluster_client_token(self, cluster_uuid: str) \
            -> Tuple[str, str, str]:
        """Create a CDM session on a given cluster with a Polaris service account,
        retrieve client access token for it.

        Notes:
        - this function does not use username & password credentials, but a
          service account instead. The CDM session can be created here without
          any active Polaris session.
        - your service account must have sufficient permissions to access the
          CDM cluster.
        - the cluster must be registered with the current Polaris instance.
        - see list_cdm_clusters to retrieve your cluster ID.

        :param cluster_uuid: Cluster ID.
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
            url=f'https://{self.baseurl}/cdm_client_token',
            data=dict(
                client_id=self.client_id,
                client_secret=self.client_secret,
                cluster_uuid=cluster_uuid,
            ),
        )
        r.raise_for_status()  # raise only if 4xx or 5xx error.
        session: Dict[str] = r.json()['session']
        return session['id'], session['token'], session['expiration']

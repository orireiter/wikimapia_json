from time import sleep
import datetime

import requests
from stem import Signal
from stem.control import Controller


class TorRequests():
    '''
        This class is used to attach the requests module to a tor server, 
        and change ip with proxy, every given amount of requests.
        If only the proxy is needed without changing ip, 
        you should switch every -1 requests.

        Attributes
        ----------
        tor_host: str
            Hostname of a tor server.
        tor_management_port: int
            Self-explanatory.
        tor_management_password: str
            Self-explanatory.
        tor_port: int
            Tor port to acquire proxy services from.
        switch_ip_every: int (defaults to -1)
            Acquire a new ip address every given amount or requests sent.
            If assigned with -1, the ip won't change.

        Methods
        -------
        get_tor_session:
            Returns a session which can be used to send requests.
            This session is already associated with the tor services
            specified upon initialization.
        renew_connection:
            Tell tor to switch ip.
        await_new_ip:
            Executes renew connection until it verifies a new ip was set.
        get:
            Gets the given url, and returns the response.
            It will switch IP every amount or requests spcified upon
            initializing the object.
    '''

    def __init__(self,
                 tor_host: str,
                 tor_management_port: int,
                 tor_management_password: str,
                 tor_port: int,
                 switch_ip_every: int = -1):

        self.tor_host = tor_host
        self.tor_management_port = tor_management_port
        self.tor_management_password = tor_management_password
        self.tor_port = tor_port
        self.switch_ip_every = switch_ip_every

        # Creating a session and using it to check current ip.
        # This is necessary to compare it to a new ip later on.
        session = self.get_tor_session()
        self.previous_ip = session.get("http://httpbin.org/ip").text

        self.request_counter = 0

    def get_tor_session(self):
        '''
            Returns a session which can be used for http requests.\n
            This session is associated with tor proxy.
        '''
        session = requests.session()
        session.proxies = {'http':  f'socks5://{self.tor_host}:{self.tor_port}',
                           'https': f'socks5://{self.tor_host}:{self.tor_port}'}

        return session

    def renew_connection(self):
        '''
            Signal tor to assign a new ip address.
        '''
        with Controller.from_port(address=self.tor_host, port=self.tor_management_port) as controller:
            controller.authenticate(password=self.tor_management_password)
            controller.signal(Signal.NEWNYM)

    def await_new_ip(self):
        '''
            This function tries to acquire a new ip, and is looped until it succeeds.
        '''
        while True:
            session = self.get_tor_session()
            self.renew_connection()

            new_ip = session.get("http://httpbin.org/ip").text

            if self.previous_ip != new_ip:
                print(
                    f'{datetime.datetime.now()} -> INFO: Changed IP from {self.previous_ip} to {new_ip}')
                self.previous_ip = new_ip
                break
            else:
                print(
                    f'{datetime.datetime.now()} -> WARNING: IP not available for change yet, retrying...')
                sleep(1)

    def get(self, url):
        '''
            This function performs a get request with a session, while appending
            to the counter, and changes ip when the counter reaches the limit.
            It returns the response of the request.
        '''
        if self.request_counter >= self.switch_ip_every and self.switch_ip_every != -1:
            self.await_new_ip()
            self.request_counter = 0

        session = self.get_tor_session()
        response = session.get(str(url))

        self.request_counter += 1
        return response

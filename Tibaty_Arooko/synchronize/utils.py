import requests


class Request(object):
    def __init__(self, domain, url, method):
        self.domain_name = domain
        self.url = url
        self.method = method
        self.uri_map = {
            'register_user': 'offline_register',
            'update_user': 'offline_update',
            'update_wallet': 'update_wallet',
            'update_schedule': 'offline_schedule',
            'update_transaction': 'update_transaction',
            'create_transaction': 'create_transaction'
        }

    def request(self, data):
        response = eval("""requests."""+self.method+"""(eval("'http://'+self.domain_name+'/'\
                        +self.uri_map[self.url]+'/'+data['username']+'/'") if data['id']\
                        else eval("'http://'+self.domain_name+'/'+self.uri_map[self.url]+'/'"))""")

        return response

    def data_request(self, data):
        response = eval("""requests."""+self.method+"""(eval("'http://'+self.domain_name+'/'\
                        +self.uri_map[self.url]+'/'+data['username']+'/'") if data['id']\
                        else eval("'http://'+self.domain_name+'/'+self.uri_map[self.url]+'/'"), data)""")

        return response


class Response:
    def __init__(self, more_data: dict = {}):
        self.data = {
            'result': '1/1 template configurations successfully applied',
            'mgmtResponse': {
                'cliTemplateCommandJobResult': [
                    {'jobName': 'test_name'}
                ]
            },
            'queryResponse': {
                'entity': [
                    {'devicesDTO': {
                        'ipAddress': '172.30.100.61',
                        '@id':'1111'
                    }},
                    {'devicesDTO': {
                        'ipAddress': '172.30.100.62',
                        '@id': '2222'
                    }},
                    {'configVersionsDTO': {
                        'fileInfos':
                            {
                                'fileInfo': [{
                                    'fileId': 'filename'
                                }]
                            }
                    }
                    }
                ]
            },

        }
        self.data.update(more_data)
        self.content = str(self.data)
        self.ok = True

    def json(self):
        return self.data

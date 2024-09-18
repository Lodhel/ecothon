from backend.app.routes.utils import make_data_by_response


class MainRouterMIXIN:

    @classmethod
    def make_response_by_ok(cls):
        data: dict = {'ok': 'success'}
        result = cls.get_data(data)
        return result

    @classmethod
    def make_response_by_error(cls):
        data: dict = {'error': 'AuthError'}
        result = cls.get_data(data)
        return result

    @staticmethod
    @make_data_by_response
    def get_data(data: dict | list):
        return data

from starlette.responses import JSONResponse


def make_data_by_response(func):
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        if isinstance(data, JSONResponse):
            return data

        if isinstance(data, dict) and data.get('error'):
            response = {'data': data, 'success': False, 'code': 400}
        else:
            response = {'data': data, 'success': True, 'code': 200}

        return JSONResponse(content=response, status_code=response['code'])

    return wrapper

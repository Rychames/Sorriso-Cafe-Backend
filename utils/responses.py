from rest_framework.response import Response as DRFResponse
from drf_yasg import openapi

def successStatus(status):
    if status < 400:
        return True
    return False

def ResponseData(
        status: int,
        data = None,
        error = None,
        message = None,
        success = False,
    ):
    response_data = {}
    
    if data is None and error is None:
        raise Exception("Data ou Error devem ser usados.")
    
    if data and error:
        raise Exception("Escolha entre Data e Error")
    
    if message is not None:
        response_data = {'message': message,}

    if data: 
        success = True
        response_data['data'] = data
    
    if error: 
        success = False
        response_data['error'] = error 

    response = {
        'success': success,
        'status': status,
        **response_data,
    }
    
    return response

def StrResponse(
    status: int,
    data = None,
    error = None,
    message = None,
    success = False,
):    
    response = ResponseData(
            status,
            data,
            error,
            message,
            success,
        )
    
    request_body = None
    
    if successStatus(response['status']):
        request_body = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Success', example=response["success"]),
                    'status': openapi.Schema(type=openapi.TYPE_INTEGER, description='Status Code', example=response["status"]),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Message', example=response.get("message", "Operação concluída!")),
                    'data': openapi.Schema(type=openapi.TYPE_STRING, description='Data', example=response.get("data", "Data xxx.")),
                }
            )
    else:
        request_body = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Success', example=response["success"]),
                    'status': openapi.Schema(type=openapi.TYPE_INTEGER, description='Status Code', example=response["status"]),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Message', example=response.get("message", "Operação não  concluída!")),
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error', example=response.get("error", "Error xxx.")),
                }
            )
    return request_body
    
def Response(
    status: int,
    data = None,
    error = None,
    message = None,
    success = False,
):    
    response = ResponseData(
            status,
            data,
            error,
            message,
            success,
        )
    return DRFResponse(response, status=status)


def ApiResponse(response):
    status = response.status_code    
    success = successStatus(status)
    if success:
        print("data", response.data)
        if response.data is None:
            response.data = {}
        return Response(status=status, data=response.data)
    else:
        return Response(status=status, error=response.data)
        
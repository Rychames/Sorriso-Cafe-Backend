from rest_framework import viewsets
from utils.responses import ApiResponse


class ModelViewSet(viewsets.ModelViewSet): 
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)           
        return ApiResponse(response)
        #return self.finalize_response(request, response)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return ApiResponse(response)
        #return self.finalize_response(request, response)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return ApiResponse(response)
        #return self.finalize_response(request, response)

    def update(self, request, *args, **kwargs):
        #request.data.pop('role', None)

        response = super().update(request, *args, **kwargs)
        
        return ApiResponse(response)
        #return self.finalize_response(request, response)

    #def partial_update(self, request, *args, **kwargs):
        #response = super().partial_update(request, *args, **kwargs)
        #return ApiResponse(response)
        #return self.finalize_response(request, response)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return ApiResponse(response)
        #return Response(status=status.HTTP_204_NO_CONTENT)
        

'''
'''
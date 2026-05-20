from django.shortcuts import render
from rest_framework import generics,permissions, viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from pprint import pprint
from django.shortcuts import get_object_or_404
from pprint import pprint
# Create your views here.
from .models import Department, Employee  
from django.db import transaction
from .serializers import EmployeeSerializer, EmployeesSerializer, DepartmentSerializer,Department1Serializer,Employee1Serializer, DepartmentTreeSerializer,DepartmentUpdateTreeSerializer, DeleteDepartmentSerializer
# Create your views here.

class DepartmentCreate(generics.ListCreateAPIView):
    serializer_class = DepartmentSerializer
    #permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (permissions.AllowAny,)
    
    def post(self,request):
        try:
            serializer = DepartmentSerializer(data=request.data, context={'request': request} )
            if serializer.is_valid():
                serializer.save()
                return Response({"department":serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Department.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class EmployeeCreate(APIView):
    serializer_class = EmployeesSerializer
    permission_classes = (permissions.AllowAny,)
    
    def post(self,request,pk):
        serializer = EmployeesSerializer(
            data=request.data,    
            context={
                'request': request,        
                'department_id': pk        
            }
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"employee":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DepartmentsCreate(APIView):
    serializer_class = Department1Serializer
    permission_classes = (permissions.AllowAny,)

    def get(self,request,id):
        serializer = DepartmentTreeSerializer(
            data=request.data, 
            context={'request': request, 'id':id},
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"dapartment":serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request,id): 
        try:   
            serializer = DepartmentUpdateTreeSerializer(
                data=request.data, 
                context={'request': request, 'id':id},
            )
            if serializer.is_valid():
               serializer.save()
               return Response({"update_department":serializer.data}, status=status.HTTP_200_OK)
            else:
               return Response(status=status.HTTP_409_CONFLICT)
        except Department.DoesNotExist:
            return Response({"error": "Департамент не найден"}, status=status.HTTP_404_NOT_FOUND)  
    
    def delete(self,request,id): 
        try:   
            serializer = DeleteDepartmentSerializer(
                data=request.data, 
                context={'request': request, 'id':id},
            )
            if serializer.is_valid():
               serializer.save()
               return Response(status=status.HTTP_204_NO_CONTENT)
            else:
               return Response({"error": serializer.errors},status=status.HTTP_404_NOT_FOUND)
        except Department.DoesNotExist:
            return Response({"error": "Департамент не найден"}, status=status.HTTP_404_NOT_FOUND)  


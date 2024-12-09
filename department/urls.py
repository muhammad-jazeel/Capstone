from django.urls import path
from .views import *

urlpatterns = [
    path('', departments_view, name='departments'),  
    path('add_department/', add_department_view, name='add_department'),  
    path('edit_department/<int:department_id>/', edit_department_view, name='edit_department'),  
    path('delete_department/<int:department_id>/', delete_department_view, name='delete_department'), 
    path('departments/toggle_department_status/<int:department_id>', toggle_department_status, name= 'toggle_department_status'),
]


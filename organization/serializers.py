from django.db import transaction
from rest_framework import serializers  
from .models import Department, Employee  
from django.contrib.auth.models import User  
from datetime import datetime
from django.forms.models import model_to_dict
from django.db import transaction
from pprint import pprint
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.http import Http404
import logging
from rest_framework.generics import get_object_or_404
logger=logging.getLogger(__name__)
from rest_framework.exceptions import APIException
class Department1Serializer(serializers.ModelSerializer):  
    """Сериализатор для комментария"""

    class Meta:  
        model = Department  
        fields = '__all__' 
    
class Employee1Serializer(serializers.ModelSerializer):  
    """Сериализатор для модели Manufacturer"""  

    class Meta:  
        model = Employee  
        fields = '__all__'
class ValidationError404(APIException):
    status_code = status.HTTP_404_NOT_FOUND
  
class EmployeesSerializer(serializers.ModelSerializer):  
    """Сериализатор для сотрудника"""  
    
    def create(self, validated_data):
        # Используем timezone.now() для поддержки часовых поясов Django
        validated_data['created_at'] = timezone.now()
    
        # Извлекаем id департамента из параметров URL (например, если в urls.py указано <int:pk> или <int:department_id>)
        department_id = self.context.get('department_id')

        if not department_id:
            raise serializers.ValidationError({
                "department": "Не удалось определить ID департамента из URL."
            })

        try:
            # Проверяем, существует ли департамент
            dept = Department.objects.get(id=department_id)
        
            # Создаем сотрудника и связываем его с департаментом
            employee = Employee.objects.create(**validated_data, department=dept)
            return employee

        except Department.DoesNotExist:
            # Используем стандартное исключение с кодом 404
            raise serializers.ValidationError(
                 {"department_id": "Департамент с таким ID не существует."},
                 code=404
            )
        except (ValueError, TypeError):
            raise serializers.ValidationError({
                "department_id": "Некорректный формат ID департамента в URL."
            })
    
    def update(self, instance, validated_data):
         # Получаем нового родителя из validated_data (обычно DRF передает объект модели в 'parent')
         new_parent = validated_data.get('parent', instance.parent)
         new_name = validated_data.get('name', instance.name)

         # Защита от зацикливания: департамент не должен быть родителем самого себя
         if new_parent and new_parent.id == instance.id:
             raise serializers.ValidationError({
                 "parent": "Департамент не может быть родителем самого себя."
            })

         # Обновляем поля корректно
         instance.parent = new_parent
         instance.name = new_name
         instance.save()
         return instance
    
    class Meta:  
        model = Employee  
        fields = ('id', 'department_id', 'full_name', 'position','hired_at_field','created_at')

    def validate_full_name(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError("Поле не может быть пустым.")
            
        # 3. Проверяем длину строки
        if not (1 <= len(cleaned_value) <= 200):
            raise serializers.ValidationError("Длина текста должна быть от 1 до 200 символов.")
        return cleaned_value
    
    def validate_position(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError("Поле не может быть пустым.")
            
        # 3. Проверяем длину строки
        if not (1 <= len(cleaned_value) <= 200):
            raise serializers.ValidationError("Длина текста должна быть от 1 до 200 символов.")
        return cleaned_value  

class EmployeeSerializer(serializers.ModelSerializer):  
    """Сериализатор для комментария"""  

    def create(self, validated_data):
        # Устанавливаем корректное время создания с учетом таймзоны
        validated_data['created_at'] = timezone.now()
    
        # 1. Безопасно получаем ID департамента из URL через kwargs контроллера
        view = self.context.get('view')
        object_id = view.kwargs.get('pk') if view else None

        # Запасной вариант (только если роутер не передал kwargs)
        if not object_id:
            try:
                path_segments = [i for i in str(self.context['request'].path).split('/') if i]
                object_id = int(path_segments[1])
            except (IndexError, ValueError, KeyError):
                # Если ID вообще не удалось спарсить, выбрасываем 404
                raise Http404("ID подразделения не указан или некорректен.")

        # 2. Ищем департамент. Если его нет — Django автоматически вернет ответ 404 Not Found
        dept = get_object_or_404(Department, id=object_id)
    
        # 3. Если департамент успешно найден, создаем сотрудника
        employee = Employee.objects.create(**validated_data, department=dept)
        return employee

    def update(self, instance, validated_data):
        # Проверяем, пришел ли новый ID департамента для переназначения
        if 'reassign_to_department_id' in validated_data:
            reassign_id = validated_data.get('reassign_to_department_id')
        
            # Ищем новый департамент. Если его нет в базе — автоматически вернется 404 Not Found
            new_department = get_object_or_404(Department, id=reassign_id)
        
            # Присваиваем именно найденный объект модели
            instance.department = new_department

        # Обновляем остальные стандартные поля сотрудника (например, имя, фамилию), если они пришли
        for attr, value in validated_data.items():
            if attr != 'reassign_to_department_id':
                setattr(instance, attr, value)
            
        instance.save()
        return instance
  
    class Meta:  
        model = Employee  
        fields = ('id', 'department_id', 'full_name', 'position','hired_at_field','created_at')  
    
    def validate_full_name(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError("Поле не может быть пустым.")
            
        # 3. Проверяем длину строки
        if not (1 <= len(cleaned_value) <= 200):
            raise serializers.ValidationError("Длина текста должна быть от 1 до 200 символов.")

        return cleaned_value
    
    def validate_position(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError("Поле не может быть пустым.")
            
        # 3. Проверяем длину строки
        if not (1 <= len(cleaned_value) <= 200):
            raise serializers.ValidationError("Длина текста должна быть от 1 до 200 символов.")

        return cleaned_value

class DepartmentSerializer(serializers.ModelSerializer):  
    """Сериализатор для комментария"""  
    class Meta:  
        model = Department  
        fields = ('id','name','parent','created_at') 
        #extra_kwargs = {'parent': {'required': False}}
    
    def validate_name(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError("Поле не может быть пустым.")
            
        # 3. Проверяем длину строки
        if not (1 <= len(cleaned_value) <= 200):
            raise serializers.ValidationError("Длина текста должна быть от 1 до 200 символов.")

        return cleaned_value
    
    def create(self, validated_data):
        # Используем timezone.now() вместо datetime.now() для поддержки часовых поясов Django
        validated_data['created_at'] = timezone.now()
    
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError({"request": "Контекст запроса отсутствует."})
        
        # Безопасно получаем данные из запроса
        parent_id = request.data.get('parent')
        name = request.data.get('name')
    
        if not name:
            raise serializers.ValidationError({"name": "Поле 'name' обязательно для заполнения."})

        # Если parent_id не передан, создаем корневой департамент
        if not parent_id:
            return Department.objects.create(**validated_data)

        try:
            # Проверяем существование родительского департамента
            dept = Department.objects.get(id=parent_id)
        
            # Проверяем, есть ли уже у этого родителя дочерний элемент с таким же именем
            child_exists = Department.objects.filter(parent=dept, name=name).exists()
        
            if child_exists:
                raise serializers.ValidationError({
                    "parent": "Запись отменена: дочерний элемент с таким именем уже существует у этого родителя."
                })
            
            # Создаем департамент, явно связывая его с родителем (если этого нет в validated_data)
            validated_data['parent'] = dept
            return Department.objects.create(**validated_data)

        except Department.DoesNotExist:
            raise serializers.ValidationError({"parent": "Указанный родительский департамент не найден."})

    def update(self, instance, validated_data):
        # Извлекаем новые значения (если их нет в запросе, оставляем старые)
        new_parent = validated_data.get('parent', instance.parent)
        new_name = validated_data.get('name', instance.name)

        # Проверка на базовое зацикливание иерархии
        if new_parent and new_parent.id == instance.id:
            raise serializers.ValidationError({
                "parent": "Департамент не может быть родительским для самого себя."
            })

        # Применяем изменения к объекту
        instance.parent = new_parent
        instance.name = new_name
        instance.updated_at = timezone.now() 
        instance.save()
        return instance

    def validate_parent(self, value):
        # instance — это департамент, который мы СЕЙЧАС обновляем
        if self.instance and value:
            
            # РЕКУРСИВНАЯ ФУНКЦИЯ: идет вверх по дереву новых родителей
            def check_cycle(current_parent):
                if current_parent == self.instance:
                    raise serializers.ValidationError("Цикл! Нельзя перенести департамент внутрь его собственного поддепартамента.")
                if current_parent.parent:
                    check_cycle(current_parent.parent) # Рекурсивный шаг вверх  

class DepartmentTreeSerializer(serializers.ModelSerializer):
    
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    class Meta:
        model = Department
        fields = '__all__'  

    def create(self, validated_data):
    # ... логика поиска ID ...
        view = self.context.get('id')
        root_department = get_object_or_404(Department, id=view)
        
        return root_department

    def to_representation(self, instance):
        # 1. Получаем стандартные данные текущего объекта
        data = super().to_representation(instance)
        
        # 2. Достаем значение depth из тела POST-запроса
        request = self.context.get('request')
        max_depth = 0  # значение по умолчанию (выводить только текущий уровень)
        
        if request and request.data:
            # Пытаемся безопасно достать параметр 'max_depth' из JSON-тела POST-запроса
            try:
                max_depth = int(request.data.get('depth', 0))
                if max_depth < 1 or max_depth > 5:
                    raise serializers.ValidationError({
                        "max_depth": f"Глубина поиска должна быть от 1 до 5 включительно. Вы передали: {max_depth}."
                    })

            except (ValueError, TypeError):
                max_depth = 0

        # 3. Получаем текущий уровень глубины из контекста (чтобы контролировать шаги рекурсии)
        current_depth = self.context.get('current_depth', 0)
        if current_depth == 0:
            # Находим всех сотрудников, привязанных к данному корневому департаменту
            root_employees = Employee.objects.filter(department=instance)
            # Сериализуем список сотрудников
            data['initial_department_employees'] = Employee1Serializer(root_employees, many=True).data
        # ====================================================================

        # 4. РЕКУРСИЯ: Если мы еще не достигли лимита max_depth, подтягиваем детей
        if current_depth < max_depth:
            # Находим прямых детей для текущего департамента
            children = Department.objects.filter(parent=instance)
            
            # Создаем новый контекст для следующего шага рекурсии, увеличивая счетчик глубины
            new_context = self.context.copy()
            new_context['current_depth'] = current_depth + 1
            
            # Запускаем этот же сериализатор рекурсивно для списка детей
            child_serializer = self.__class__(children, many=True, context=new_context)
            data['children'] = child_serializer.data
        else:
            # Если глубина исчерпана, возвращаем пустой список или вообще не выводим ключ 'children'
            data['children'] = []

        return data
class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Обнаружен конфликт в структуре данных.'
    default_code = 'conflict'

class DepartmentUpdateTreeSerializer(serializers.ModelSerializer):
    
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    
    class Meta:
        model = Department
        fields = '__all__'  
    
    def create(self, validated_data):
        # 1. Получаем ID текущего департамента
        root_id = self.context.get('id') or self.context.get('root_id')
        root_department = get_object_or_404(Department, id=root_id)
        
        # 2. Получаем ID нового родителя из тела запроса
        request = self.context.get('request')
        parent_id = request.data.get('parent') if request else None
        
        if not parent_id:
            raise serializers.ValidationError({"parent": "Поле parent обязательно для проверки."})

        new_parent = get_object_or_404(Department, id=parent_id)

        if int(parent_id) == root_department.id:
            raise ConflictException({"department": "Ваш родитель не подходит: нельзя назначить департамент родителем самого себя."})

        # Множество для сохранения всех ID, которые мы встретим по пути наверх
        visited_ids = {root_department.id}
        
        # Начинаем движение вверх от нового родителя
        current_dept = new_parent
        
        while current_dept is not None:
            # Если ID текущего департамента уже встречался в нашей цепочке — это цикл!
            if current_dept.id in visited_ids:
                raise ConflictException({
                    "department": "Ваш родитель не подходит: данное перемещение создает бесконечный цикл в иерархии."
                })
            
            # Запоминаем текущий ID как пройденный
            visited_ids.add(current_dept.id)
            
            # Переходим к следующему родителю выше по дереву.
            # Используем parent_id, чтобы Django не делал лишних "тяжелых" запросов объектов
            if current_dept.parent_id:
                # Берем id напрямую, а объект запрашиваем точечно
                current_dept = Department.objects.filter(id=current_dept.parent_id).first()
            else:
                current_dept = None
        # ====================================================================

        # Если цикл не обнаружен, обновляем родителя в базе данных
        root_department.parent = new_parent
        root_department.save()

        return root_department

    def to_representation(self, instance):
        return super().to_representation(instance)

class DeleteDepartmentSerializer(serializers.ModelSerializer):
    
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Department
        fields = '__all__'  
    
    def create(self, validated_data):
        request = self.context.get('request')
        mode = request.query_params.get('mode')
        id = self.context.get('id')
        try:
            department = Department.objects.get(id=id)

            # Обертываем логику в транзакцию, чтобы база данных не сломалась при ошибке
            with transaction.atomic():
                if mode == 'cascade':
                    department.delete()

                elif mode == 'reassign':
                    reassign_to_id = request.query_params.get('reassign_to_department_id')
                    if not reassign_to_id:
                        raise serializers.ValidationError({"error": "Параметр reassign_to_department_id обязателен"})

                    try:
                        reassign_department = Department.objects.get(id=reassign_to_id)
                    except Department.DoesNotExist:
                        raise serializers.ValidationError(
                            {"error": "Департамент для переназначения не найден"}
                        ) 
                            
                    # Переназначаем сотрудников и удаляем старый департамент
                    Employee.objects.filter(department=department).update(department=reassign_department)
                    department.delete()
        
                else:
                    return serializers.ValidationError(
                        {"error": "Неверный или отсутствующий режим (mode)"} 
                    )

        except Department.DoesNotExist:
            raise serializers.ValidationError(
                {"error": "Департамент для удаления не найден"}
            ) 
        return department
 
    def to_representation(self, instance):
        return super().to_representation(instance)

from django import forms 
from django.contrib.auth import authenticate
from.models import User,Session, Position,Course,SemesterQuestionPattern,SemesterQuestionSet,SemesterSubQuestion,SemesterSubQuestionMark

class LoginForm(forms.Form):
    email = forms.EmailField(
        label ="Email",
        widget = forms.EmailInput(
            attrs = {
                "class":"form-control",
                "placeholder":"Enter email",
            }
        ) 
    )
    
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs ={
                "class":"form-control",
                "placeholder":"Enter your password",
            }
        )
        
    )
    def clean(self):
        cleaned_data = super().clean()
        
        email = cleaned_data.get('email')
        password=cleaned_data.get('password')
         
        if email and password:
            user=authenticate(
                username=email,
                password=password
            )
            if user is None:
                raise forms.ValidationError(
                    "Invalid email or password"
                )
            if not user.is_active:
                raise forms.ValidationError(
                    "this account is in active."
                )
            self.user = user
        return cleaned_data
    
class TeacherCreateForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class":"form-control",
                "placeholder":"Enter Password",
            }
                
            
        )
    )
    class Meta:
        model = User
        fields =[
            "username","first_name","last_name","email","date_of_birth","address","password"
        ]
    
        widgets ={
            "username":forms.Textarea(
                 attrs={
                     "class":"form-contron",
                     "placeholder":"Enter username"
                 }
             ),
            "first_name":forms.TextInput(
                attrs={
                    "class":"form-contron",
                    "placeholder":"Enter first name"
                    
                }
            ),
            "last_name":forms.TextInput(
                attrs={
                    "class":"form-contron",
                    "placeholder":"Enter last name"
                }
            ),
            "email":forms.EmailInput(
                attrs={
                                        "class":"form-contron",
                    "placeholder":"Enter your email"
                }
            ),
            "gender":forms.Select(
                attrs={
                    "class":"form-select",
                }
            ),
            "date_of_birth":forms.DateInput(
                attrs={
                    "class":"form-contron",
                    "type":"data",
                }
            ),
            "address":forms.Textarea(
                attrs={
                                        "class":"form-contron",
                    "placeholder":"Enter your address",
                    "rows":3
                }
            ),   
             
         }
        
        def save(self,commit=True):
            user = super().save(commit=False)
            user.role ="teacher"
            user.set_password(
                self.cleaned_data["password"]
            )
            if commit:
                user.save()
                
            return user
        
class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                  "class": "form-control",
                "placeholder": "Enter password",
            }
        )
    )
    
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm password",
            }
        )
    )
    
    class Meta :
         model = User
         fields = [
             "username","first_name","last_name","email","gender","date_of_birth","address","role","password","session","position"
             
         ]
         widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter username",
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter first name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter last name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter email",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter address",
                    "rows": 3,
                }
            ),

            "role": forms.Select(
                attrs={
                    "class": "form-select",
                    "id":"id_role",
                }
            ),
             "session": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_session",
                }
            ),
             "position": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_position",
                }
            ),
        }
    def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.fields["role"].choices = [
            ("student", "Student"),
            ("teacher", "Teacher"),
        ]
            self.fields["session"].queryset = Session.objects.all()

            self.fields["position"].queryset = Position.objects.all()

            self.fields["session"].empty_label = "Select Session"

            self.fields["position"].empty_label = "Select Position"
            
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        role = cleaned_data.get("role")
        session = cleaned_data.get("session")
        position = cleaned_data.get("position")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )
        
        if role == "student":
            if not session:
                self.add_error(
                    "session",
                    "Please select your session."
                )
            cleaned_data["position"]=None
            
        elif role == "teacher":
            if not position:
                self.add_error(
                    "position",
                    "Please select your Positon."
                )
            cleaned_data["session"]=None
        elif role == "admin":
            cleaned_data["session"] = None
            cleaned_data["position"] = None

        return cleaned_data
    
    def save(self, commit=True):
    
        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password"]
        )

        if commit:
            user.save()

        return user
    
    
class StudentProfileForm(forms.ModelForm):
    
    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "address",
            "profile_image",
            "roll",
            "face_image",
        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "roll": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your roll number",
                }
            ),

            "face_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }
        
class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields=[
            "year",
            "is_graduated",
        ]
        
   
        widgets = {

            "year": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: 2020-2021",
                }
            ),

            "is_graduated": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        } 
        
        
    
class CourseForm(forms.ModelForm):
    
    class Meta:
        model = Course

        fields = [
            "course_code",
            "course_name",
            "year",
            "semester",
            "credit",
            "session",
            "teacher",
        ]

        widgets = {

            "course_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: ICE-1001",
                }
            ),

            "course_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: C Programming",
                }
            ),

            "year": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "semester": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "credit": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: 3.0",
                    "step": "0.1",
                }
            ),

            "session": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "teacher": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["teacher"].queryset = User.objects.filter(
            role="teacher",
            is_active=True
        ).order_by(
            "first_name",
            "last_name"
        )

        self.fields["teacher"].label_from_instance = (
            lambda teacher: (
                f"{teacher.get_full_name() or teacher.username}"
                f" - {teacher.position}"
            )
        )
     
     
class SemesterQuestionPatternForm(forms.ModelForm):
    
    class Meta:
        model = SemesterQuestionPattern

        fields = [
            "course",
            "total_marks",
        ]

        widgets = {
            "course": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "total_marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter total semester marks",
                    "step": "0.01",
                    "min": "1",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["course"].queryset = Course.objects.filter(
            semester_question_pattern__isnull=True
        ).order_by(
            "session",
            "year",
            "semester",
            "course_code"
        )

        self.fields["course"].label_from_instance = (
            lambda course: (
                f"{course.course_code} - "
                f"{course.course_name} "
                f"({course.session.year})"
            )
        )

    def clean_course(self):
        course = self.cleaned_data["course"]

        if hasattr(course, "semester_question_pattern"):
            raise forms.ValidationError(
                "This course already has a semester question pattern."
            )

        return course


class SemesterQuestionSetForm(forms.ModelForm):

    class Meta:
        model = SemesterQuestionSet

        fields = [
            "set_name",
            "total_marks",
            "order",
        ]

        widgets = {
            "set_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: A, B, C"
                }
            ),

            "total_marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter set marks",
                    "step": "0.01",
                    "min": "0"
                }
            ),

            "order": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1"
                }
            ),
        }


class SemesterSubQuestionForm(forms.ModelForm):

    class Meta:
        model = SemesterSubQuestion

        fields = [
            "question_label",
            "marks",
            "order",
        ]

        widgets = {
            "question_label": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: A1, A2, A3"
                }
            ),

            "marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter question marks",
                    "step": "0.01",
                    "min": "0"
                }
            ),

            "order": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1"
                }
            ),
        }


class SemesterSubQuestionMarkForm(forms.ModelForm):

    class Meta:
        model = SemesterSubQuestionMark

        fields = [
            "obtained_marks",
        ]

        widgets = {
            "obtained_marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }
    
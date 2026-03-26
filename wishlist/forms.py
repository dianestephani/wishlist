from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Activity, Event, Wishlist, WishlistItem

User = get_user_model()


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone_number"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "Phone number"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Description (optional)"}),
        }


class WishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ["title", "product_url", "price", "category", "brand", "store", "image", "notes"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Item name"}),
            "product_url": forms.URLInput(attrs={"placeholder": "https://..."}),
            "price": forms.NumberInput(attrs={"placeholder": "0.00", "step": "0.01"}),
            "category": forms.TextInput(attrs={"placeholder": "e.g. Gaming, Beauty"}),
            "brand": forms.TextInput(attrs={"placeholder": "e.g. Nintendo, OUAI"}),
            "store": forms.TextInput(attrs={"placeholder": "e.g. Best Buy, Ulta"}),
            "notes": forms.Textarea(attrs={"rows": 2, "placeholder": "Notes (optional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name != "title":
                self.fields[field_name].required = False
        self.fields["title"].required = True


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "date", "start_time", "end_time", "address", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "address": forms.TextInput(attrs={"placeholder": "123 Main St, City, State"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Notes (optional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["date"].required = True
        self.fields["start_time"].required = True
        self.fields["end_time"].required = True
        self.fields["address"].required = True
        self.fields["notes"].required = False

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and end_time <= start_time:
            self.add_error("end_time", "End time must be after start time.")
        return cleaned_data


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["title", "location", "notes"]
        widgets = {
            "location": forms.TextInput(attrs={"placeholder": "City, State"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Notes (optional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = True
        self.fields["location"].required = True
        self.fields["notes"].required = False


class PurchaseForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label=(
            "I confirm that I have purchased this item. If I have not purchased it "
            "and I click Confirm Purchase anyway, I understand that I am responsible for "
            "contacting Diane and telling her personally that I lied about getting "
            "her a birthday present."
        ),
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Leave a message (optional)"}),
        label="Message",
    )


class UndoPurchaseForm(forms.Form):
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Explain yourself (optional)"}),
        label="Message",
    )

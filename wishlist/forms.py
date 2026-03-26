from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

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


class PurchaseForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label=(
            "I confirm that I have purchased this item. If I have not purchased it "
            "and I click Purchased anyway, I understand that I am responsible for "
            "contacting Diane and telling her personally that I lied about getting "
            "her a birthday present."
        ),
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Leave a message (optional)"}),
        label="Message",
    )

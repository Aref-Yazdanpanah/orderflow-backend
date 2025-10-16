from django import forms
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import OTP

User = get_user_model()


try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


# ---------------------------
# Forms for the custom User
# ---------------------------
class UserCreationForm(forms.ModelForm):
    """
    Creation form with two password entries.
    """

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Password confirmation"), widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "is_active")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_("Passwords don't match."))
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use the model manager's password handling via set_password
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Simple change form; password changes should be done via the "change password" form.
    """

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


# ---------------------------
# Admins
# ---------------------------
@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    """
    Admin for custom User where `username` is a local mobile number (e.g., 09121234567).
    """

    form = UserChangeForm
    add_form = UserCreationForm
    ordering = ["-date_joined"]

    # What shows on the change page
    fieldsets = (
        (None, {"fields": ("id", "username", "first_name", "last_name", "password")}),
        (_("Role"), {"fields": ("role",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # What shows on the add page
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_active",
                ),
            },
        ),
    )

    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    ]
    search_fields = ["id", "username", "first_name", "last_name"]
    list_filter = ["role", "is_active", "is_staff", "is_superuser"]
    readonly_fields = ["id", "date_joined", "last_login"]


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """
    OTPs are mostly immutable; we keep them view/delete-only to preserve auditability.
    """

    list_display = (
        "id",
        "password",
        "destination",
        "is_used",
        "is_expired",
        "created_at",
    )
    ordering = ["-created_at"]
    search_fields = ["id", "destination", "password"]
    list_filter = ["is_used", "created_at"]
    readonly_fields = (
        "id",
        "password",
        "destination",
        "is_used",
        "extra",
        "created_at",
    )

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        # Keeping OTPs immutable in admin; toggle to True if you want to allow flipping is_used.
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        # Allow deletes if you explicitly want to purge old OTPs from the admin.
        return True

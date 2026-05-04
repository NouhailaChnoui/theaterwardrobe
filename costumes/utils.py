def is_admin(user):
    """Vérifie si l'utilisateur est admin (staff ou groupe Régisseur)."""
    return user.is_authenticated and (user.is_staff or user.groups.filter(name='Régisseur').exists())

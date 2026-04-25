from django.shortcuts import redirect


class OrganizationMiddleware:
    """
    Attaches the current organization to the request object.
    
    After this middleware runs, views can access `request.organization`
    instead of manually fetching from session every time.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from apps.accounts.models import Organization
        
        request.organization = None
        org_id = request.session.get('org_id')
        
        if org_id:
            try:
                request.organization = Organization.objects.get(id=org_id, is_active=True)
            except Organization.DoesNotExist:
                # Invalid session — clean it up
                request.session.pop('org_id', None)

        return self.get_response(request)

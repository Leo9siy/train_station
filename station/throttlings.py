from rest_framework.throttling import SimpleRateThrottle


class AdminRateThrottle(SimpleRateThrottle):
    scope = 'admin'

    def get_cache_key(self, request, view):
        if (request.user and request.user.is_authenticated
                and request.user.is_staff
                and not request.user.is_superuser):
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

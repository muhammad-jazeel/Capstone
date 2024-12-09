import random
from service.models import Service

def get_random_recommendations(limit=5):
    """
    Fetch random services from random vendors.
    :param limit: Number of services to fetch.
    :return: QuerySet of randomly selected services.
    """
    services = Service.objects.filter(status='active').select_related('user__vendor')
    if services.exists():
        service_ids = services.values_list('id', flat=True)
        random_ids = random.sample(list(service_ids), min(len(service_ids), limit))
        return Service.objects.filter(id__in=random_ids)
    return []

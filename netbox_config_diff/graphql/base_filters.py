from netbox.settings import VERSION

if VERSION.startswith("4.4"):
    from core.graphql.filter_mixins import ChangeLogFilterMixin as ChangeLoggedModelFilter
    from netbox.graphql.filter_mixins import NetBoxModelFilterMixin as NetBoxModelFilter
    from netbox.graphql.filter_mixins import PrimaryModelFilterMixin as PrimaryModelFilter
elif VERSION.startswith("4.5"):
    from netbox.graphql.filters import (
        ChangeLoggedModelFilter,
        NetBoxModelFilter,
        PrimaryModelFilter,
    )


class ChangeLoggedGraphQLFilter(ChangeLoggedModelFilter):
    pass


class NetBoxGraphQLFilter(NetBoxModelFilter):
    pass


class PrimaryNetBoxGraphQLFilter(PrimaryModelFilter):
    pass

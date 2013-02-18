from sqlalchemy import and_, desc
from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer

from clld.web import datatables
from clld.web.datatables.base import (
    Col, filter_number, LinkCol, DetailsRowLinkCol, LinkToMapCol,
)
from clld.db.models import common
from clld.web.util.helpers import linked_contributors, link
from clld.web.util.htmllib import HTML
from clld.db.meta import DBSession

from wals3.models import WalsLanguage, Genus, Family, Chapter, Feature, Area


class FeatureIdCol(LinkCol):
    def get_attrs(self, item):
        return {'label': item.id}

    def order(self):
        return Feature.contribution_pk, Feature.ordinal_qualifier


class FeatureIdCol2(FeatureIdCol):
    def get_attrs(self, item):
        return {'label': item.parameter.id}

    def get_obj(self, item):
        return item.parameter


class AreaCol(Col):
    #def __init__(self, *args, **kw):
    #    super(AreaCol, self).__init__(*args, **kw)
    #    self.choices = [a.name for a in DBSession.query(Area).order_by(Area.id)]

    def format(self, item):
        return item.parameter.chapter.area.name

    def order(self):
        return Area.name

    def search(self, qs):
        return Area.name.contains(qs)


class RefCol(Col):
    def format(self, item):
        res = ''
        for i, ref in enumerate(item.references):
            if i > 0:
                res += ', '
            res += link(self.dt.req, ref.source)
            if ref.description:
                res += ' (%s)' % ref.description
        return HTML.small(res)


class Datapoints(datatables.Values):
    def base_query(self, query):
        query = super(Datapoints, self).base_query(query)
        query = query.options(joinedload_all(common.Value.references, common.ValueReference.source))
        if self.language:
            query = query.join(Feature, Feature.pk == common.Value.parameter_pk)\
                .join(Chapter, Area)\
                .options(joinedload_all(common.Value.parameter, Feature.chapter))
        return query

    #
    # TODO: add columns:
    # - parameter id (if not self.parameter)
    # - feature area (if not self.parameter)
    # - references
    #
    def col_defs(self):
        cols = list(reversed(super(Datapoints, self).col_defs()))
        if not self.parameter:
            cols = [FeatureIdCol2(self, 'fid', sClass='right', bSearchable=False)]\
                + cols\
                + [AreaCol(self, 'area', bSearchable=False)]
        return cols + [
            RefCol(self, 'references', bSearchable=False, bSortable=False),
            Col(self, 'version'),
            ]

    def get_options(self):
        opts = super(Datapoints, self).get_options()
        if self.language:
            # if the table is restricted to the values for one language, the number of
            # features is an upper bound for the number of values; thus, we do not
            # paginate.
            opts['bLengthChange'] = False
            opts['bPaginate'] = False
        return opts


class ContributorsCol(Col):
    def format(self, item):
        return linked_contributors(self.dt.req, item.chapter)


class RepresentationCol(Col):
    def search(self, qs):
        return filter_number(cast(common.Parameter_data.value, Integer), qs, type_=int)

    def order(self):
        return cast(common.Parameter_data.value, Integer)

    def format(self, item):
        return item.datadict()['representation']


class Features(datatables.Parameters):
    def base_query(self, query):
        return query.join(Chapter)\
            .join(common.Parameter_data, and_(
                common.Parameter_data.object_pk == common.Parameter.pk,
                common.Parameter_data.key == 'representation'
            ))\
            .options(joinedload(Feature.chapter), joinedload(common.Parameter.data))

    def col_defs(self):
        return [
            DetailsRowLinkCol(self),
            FeatureIdCol(self, 'id', sClass='right'),
            LinkCol(self, 'name'),
            ContributorsCol(self, 'Authors', bSearchable=False, bSortable=False),
            RepresentationCol(self, 'Languages', sClass='right'),
        ]


class GenusCol(Col):
    def order(self):
        return Genus.name

    def search(self, qs):
        return Genus.name.contains(qs)

    def format(self, item):
        return item.genus.name


class FamilyCol(Col):
    def order(self):
        return Family.name

    def search(self, qs):
        return Family.name.contains(qs)

    def format(self, item):
        return link(self.dt.req, item.genus.family)


class Languages(datatables.Languages):
    def base_query(self, query):
        return query.join(Genus).join(Family).options(joinedload_all(WalsLanguage.genus, Genus.family))

    def col_defs(self):
        cols = datatables.Languages.col_defs(self)
        return cols[:2] + [
            GenusCol(self, 'genus'),
            FamilyCol(self, 'family'),
            LinkToMapCol(self),
        ]

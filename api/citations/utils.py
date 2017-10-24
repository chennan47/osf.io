import os
import re
import logging
from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import Citation, CitationItem
from citeproc import formatter
from citeproc.source.json import CiteProcJSON

from osf.models import PreprintService
from website.settings import CITATION_STYLES_PATH, BASE_PATH, CUSTOM_CITATIONS


logger = logging.getLogger(__file__)


def clean_up_common_errors(cit):
    cit = re.sub(r"\.+", '.', cit)
    cit = re.sub(r" +", ' ', cit)
    return cit

def display_absolute_url(node):
    url = node.absolute_url
    if url is not None:
        return re.sub(r'https?:', '', url).strip('/')


def preprint_csl(preprint, node):
    csl = node.csl

    csl['id'] = preprint._id
    csl['publisher'] = preprint.provider.name
    csl['URL'] = display_absolute_url(preprint)

    if csl.get('DOI'):
        csl.pop('DOI')

    doi = preprint.article_doi
    if doi:
        csl['DOI'] = doi

    return csl

def render_citation(node, style='apa'):
    """Given a node, return a citation"""
    csl = None
    if isinstance(node, PreprintService):
        csl = preprint_csl(node, node.node)
        data = [csl, ]
    else:
        data = [node.csl, ]

    logger.info('-----------------')
    logger.info('data')
    logger.info(data)
    logger.info('-----------------')

    bib_source = CiteProcJSON(data)
    logger.info('-----------------')
    logger.info('bib_source')
    logger.info(bib_source)
    logger.info('-----------------')

    custom = CUSTOM_CITATIONS.get(style, False)

    path = os.path.join(BASE_PATH, 'static', custom) if custom else os.path.join(CITATION_STYLES_PATH, style)
    logger.info('-----------------')
    logger.info('path')
    logger.info(path)
    logger.info('-----------------')

    bib_style = CitationStylesStyle(path, validate=False)
    logger.info('-----------------')
    logger.info('bib_style')
    logger.info(bib_style)
    logger.info('-----------------')

    bibliography = CitationStylesBibliography(bib_style, bib_source, formatter.plain)
    logger.info('-----------------')
    logger.info('bibliography')
    logger.info(bibliography)
    logger.info('-----------------')

    citation = Citation([CitationItem(node._id)])
    logger.info('-----------------')
    logger.info('citation')
    logger.info(citation)
    logger.info('-----------------')

    bibliography.register(citation)

    bib = bibliography.bibliography()
    logger.info('-----------------')
    logger.info('bib')
    logger.info(bib)
    logger.info('-----------------')

    cit = unicode(bib[0] if len(bib) else '')
    logger.info('-----------------')
    logger.info('cit')
    logger.info(cit)
    logger.info('-----------------')

    title = csl['title'] if csl else node.csl['title']

    if cit.count(title) == 1:
        i = cit.index(title)
        prefix = clean_up_common_errors(cit[0:i])
        suffix = clean_up_common_errors(cit[i + len(title):])
        cit = prefix + title + suffix
    elif cit.count(title) == 0:
        cit = clean_up_common_errors(cit)

    return cit

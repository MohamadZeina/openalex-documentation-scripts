import csv
import glob
import gzip
import json
import os

from contextlib import ExitStack

from tqdm.auto import tqdm

# SNAPSHOT_DIR = 'openalex-snapshot'
# CSV_DIR = 'csv-files'

SNAPSHOT_DIR = '/media/mo/4TB_SSD/mo_data/datasets/openalex-snapshot-feb-2024'
CSV_DIR = '/media/mo/4TB_SSD/mo_data/datasets/csv-files-feb-2024-test-new-cols'

FILES_PER_ENTITY = int(os.environ.get('OPENALEX_DEMO_FILES_PER_ENTITY', '0'))

csv_files = {
    'authors': {
        'authors': {
            'name': os.path.join(CSV_DIR, 'authors.csv.gz'),
            'columns': [
                'id', 'orcid', 'display_name', 'display_name_alternatives', 'works_count', 'cited_by_count',
                'last_known_institution', 'works_api_url', 'updated_date',
                # Mo added
                '2yr_mean_citedness', 'h_index', 'i10_index', 'oa_percent', 
                '2yr_works_count', '2yr_cited_by_count', '2yr_i10_index', '2yr_h_index' 
            ]
        },
        'ids': {
            'name': os.path.join(CSV_DIR, 'authors_ids.csv.gz'),
            'columns': [
                'author_id', 'openalex', 'orcid', 'scopus', 'twitter', 'wikipedia', 'mag'
            ]
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, 'authors_counts_by_year.csv.gz'),
            'columns': [
                'author_id', 'year', 'works_count', 'cited_by_count', 'oa_works_count'
            ]
        }
    },
    'concepts': {
        'concepts': {
            'name': os.path.join(CSV_DIR, 'concepts.csv.gz'),
            'columns': [
                'id', 'wikidata', 'display_name', 'level', 'description', 'works_count', 'cited_by_count', 'image_url',
                'image_thumbnail_url', 'works_api_url', 'updated_date'
            ]
        },
        'ancestors': {
            'name': os.path.join(CSV_DIR, 'concepts_ancestors.csv.gz'),
            'columns': ['concept_id', 'ancestor_id']
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, 'concepts_counts_by_year.csv.gz'),
            'columns': ['concept_id', 'year', 'works_count', 'cited_by_count', 'oa_works_count']
        },
        'ids': {
            'name': os.path.join(CSV_DIR, 'concepts_ids.csv.gz'),
            'columns': ['concept_id', 'openalex', 'wikidata', 'wikipedia', 'umls_aui', 'umls_cui', 'mag']
        },
        'related_concepts': {
            'name': os.path.join(CSV_DIR, 'concepts_related_concepts.csv.gz'),
            'columns': ['concept_id', 'related_concept_id', 'score']
        }
    },
    'topics': {
        'topics': {
            'name': os.path.join(CSV_DIR, 'topics.csv.gz'),
            'columns': [
                'id', 'display_name', 'subfield', 'field', 'domain', 'description', 'keywords', 
                'works_count', 'cited_by_count',
            ]
        },
        # 'ancestors': {
        #     'name': os.path.join(CSV_DIR, 'concepts_ancestors.csv.gz'),
        #     'columns': ['concept_id', 'ancestor_id']
        # # },
        # 'counts_by_year': {
        #     'name': os.path.join(CSV_DIR, 'concepts_counts_by_year.csv.gz'),
        #     'columns': ['concept_id', 'year', 'works_count', 'cited_by_count', 'oa_works_count']
        # },
        # 'ids': {
        #     'name': os.path.join(CSV_DIR, 'concepts_ids.csv.gz'),
        #     'columns': ['concept_id', 'openalex', 'wikidata', 'wikipedia', 'umls_aui', 'umls_cui', 'mag']
        # },
        # 'related_concepts': {
        #     'name': os.path.join(CSV_DIR, 'concepts_related_concepts.csv.gz'),
        #     'columns': ['concept_id', 'related_concept_id', 'score']
        # }
    },
    'subfields': {
        'subfields': {
            'name': os.path.join(CSV_DIR, 'subfields.csv.gz'),
            'columns': [
                'id', 'display_name', 'field', 'domain', 'description',
                'works_count', 'cited_by_count',
            ]
        },
    },
    'fields': {
        'fields': {
            'name': os.path.join(CSV_DIR, 'fields.csv.gz'),
            'columns': [
                'id', 'display_name', 'domain', 'description',
                'works_count', 'cited_by_count',
            ]
        },
    },
    'domains': {
        'domains': {
            'name': os.path.join(CSV_DIR, 'domains.csv.gz'),
            'columns': [
                'id', 'display_name', 'description',
                'works_count', 'cited_by_count',
            ]
        },
    },
    'institutions': {
        'institutions': {
            'name': os.path.join(CSV_DIR, 'institutions.csv.gz'),
            'columns': [
                'id', 'ror', 'display_name', 'country_code', 'type', 'homepage_url', 'image_url', 'image_thumbnail_url',
                'display_name_acronyms', 'display_name_alternatives', 'works_count', 'cited_by_count', 'works_api_url',
                'updated_date'
            ]
        },
        'ids': {
            'name': os.path.join(CSV_DIR, 'institutions_ids.csv.gz'),
            'columns': [
                'institution_id', 'openalex', 'ror', 'grid', 'wikipedia', 'wikidata', 'mag'
            ]
        },
        'geo': {
            'name': os.path.join(CSV_DIR, 'institutions_geo.csv.gz'),
            'columns': [
                'institution_id', 'city', 'geonames_city_id', 'region', 'country_code', 'country', 'latitude',
                'longitude'
            ]
        },
        'associated_institutions': {
            'name': os.path.join(CSV_DIR, 'institutions_associated_institutions.csv.gz'),
            'columns': [
                'institution_id', 'associated_institution_id', 'relationship'
            ]
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, 'institutions_counts_by_year.csv.gz'),
            'columns': [
                'institution_id', 'year', 'works_count', 'cited_by_count', 'oa_works_count'
            ]
        }
    },
    'publishers': {
        'publishers': {
            'name': os.path.join(CSV_DIR, 'publishers.csv.gz'),
            'columns': [
                'id', 'display_name', 'alternate_titles', 'country_codes', 'hierarchy_level', 'parent_publisher',
                'works_count', 'cited_by_count', 'sources_api_url', 'updated_date'
            ]
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, 'publishers_counts_by_year.csv.gz'),
            'columns': ['publisher_id', 'year', 'works_count', 'cited_by_count', 'oa_works_count']
        },
        'ids': {
            'name': os.path.join(CSV_DIR, 'publishers_ids.csv.gz'),
            'columns': ['publisher_id', 'openalex', 'ror', 'wikidata']
        },
    },
    'sources': {
        'sources': {
            'name': os.path.join(CSV_DIR, 'sources.csv.gz'),
            'columns': [
                'id', 'issn_l', 'issn', 'display_name', 'publisher', 'works_count', 'cited_by_count', 'is_oa',
                'is_in_doaj', 'homepage_url', 'works_api_url', 'updated_date'
            ]
        },
        'ids': {
            'name': os.path.join(CSV_DIR, 'sources_ids.csv.gz'),
            'columns': ['source_id', 'openalex', 'issn_l', 'issn', 'mag', 'wikidata', 'fatcat']
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, 'sources_counts_by_year.csv.gz'),
            'columns': ['source_id', 'year', 'works_count', 'cited_by_count', 'oa_works_count']
        },
    },
    'works': {
        'works': {
            'name': os.path.join(CSV_DIR, 'works.csv.gz'),
            'columns': [
                'id', 'doi', 'title', 'display_name', 'publication_year', 'publication_date', 'type', 'cited_by_count',
                'is_retracted', 'is_paratext', 'cited_by_api_url', 'abstract_inverted_index','language',
                #'counts_by_year' # Mo added
                '2yr_cited_by_count', 'authors_count', 
                'locations_count', 'referenced_works_count', # 'grants', 'apc_list', 'apc_paid'
            ]
        },
        'primary_locations': {
            'name': os.path.join(CSV_DIR, 'works_primary_locations.csv.gz'),
            'columns': [
                'work_id', 'source_id', 'landing_page_url', 'pdf_url', 'is_oa', 'version', 'license'
            ]
        },
        'locations': {
            'name': os.path.join(CSV_DIR, 'works_locations.csv.gz'),
            'columns': [
                'work_id', 'source_id', 'landing_page_url', 'pdf_url', 'is_oa', 'version', 'license'
            ]
        },
        'best_oa_locations': {
            'name': os.path.join(CSV_DIR, 'works_best_oa_locations.csv.gz'),
            'columns': [
                'work_id', 'source_id', 'landing_page_url', 'pdf_url', 'is_oa', 'version', 'license'
            ]
        },
        'authorships': {
            'name': os.path.join(CSV_DIR, 'works_authorships.csv.gz'),
            'columns': [
                'work_id', 'author_position', 'author_id', 'institution_id', 'raw_affiliation_string'
            ]
        },
        'biblio': {
            'name': os.path.join(CSV_DIR, 'works_biblio.csv.gz'),
            'columns': [
                'work_id', 'volume', 'issue', 'first_page', 'last_page'
            ]
        },
        'concepts': {
            'name': os.path.join(CSV_DIR, 'works_concepts.csv.gz'),
            'columns': [
                'work_id', 'concept_id', 'score'
            ]
        },
        'topics': {
            'name': os.path.join(CSV_DIR, 'works_topics.csv.gz'),
            'columns': [
                'work_id', 'topic_id', 'display_name', 'score', 'subfield', 'field', 'domain'
            ]
        },
        'ids': {
            'name': os.path.join(CSV_DIR, 'works_ids.csv.gz'),
            'columns': [
                'work_id', 'openalex', 'doi', 'mag', 'pmid', 'pmcid'
            ]
        },
        'mesh': {
            'name': os.path.join(CSV_DIR, 'works_mesh.csv.gz'),
            'columns': [
                'work_id', 'descriptor_ui', 'descriptor_name', 'qualifier_ui', 'qualifier_name', 'is_major_topic'
            ]
        },
        'open_access': {
            'name': os.path.join(CSV_DIR, 'works_open_access.csv.gz'),
            'columns': [
                'work_id', 'is_oa', 'oa_status', 'oa_url', 'any_repository_has_fulltext',
                # Mo added
                'apc_list_value_usd', 'apc_paid_value_usd'
            ]
        },
        'referenced_works': {
            'name': os.path.join(CSV_DIR, 'works_referenced_works.csv.gz'),
            'columns': [
                'work_id', 'referenced_work_id'
            ]
        },
        'related_works': {
            'name': os.path.join(CSV_DIR, 'works_related_works.csv.gz'),
            'columns': [
                'work_id', 'related_work_id'
            ]
        },
        'counts_by_year': {
            'name': os.path.join(CSV_DIR, 'works_counts_by_year.csv.gz'),
            'columns': [
                'work_id', 'year', 'cited_by_count'
            ]
        },
        'sustainable_development_goals': {
            'name': os.path.join(CSV_DIR, 'works_sustainable_development_goals.csv.gz'),
            'columns': [
                'work_id', 'id', 'score' # 'display_name' redundant
            ]
        },
        'grants': {
            'name': os.path.join(CSV_DIR, 'works_grants.csv.gz'),
            'columns': [
                'work_id', 'funder', 'award_id' # 'funder_display_name' redundant
            ]
        },
    },
}


def flatten_authors():
    file_spec = csv_files['authors']

    with gzip.open(file_spec['authors']['name'], 'wt', encoding='utf-8') as authors_csv, \
            gzip.open(file_spec['ids']['name'], 'wt', encoding='utf-8') as ids_csv, \
            gzip.open(file_spec['counts_by_year']['name'], 'wt', encoding='utf-8') as counts_by_year_csv:

        authors_writer = csv.DictWriter(
            authors_csv, fieldnames=file_spec['authors']['columns'], extrasaction='ignore'
        )
        authors_writer.writeheader()

        ids_writer = csv.DictWriter(ids_csv, fieldnames=file_spec['ids']['columns'])
        ids_writer.writeheader()

        counts_by_year_writer = csv.DictWriter(counts_by_year_csv, fieldnames=file_spec['counts_by_year']['columns'])
        counts_by_year_writer.writeheader()

        files_done = 0
        for jsonl_file_name in tqdm(glob.glob(os.path.join(SNAPSHOT_DIR, 'data', 'authors', '*', '*.gz'))):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as authors_jsonl:
                for author_json in authors_jsonl:
                    if not author_json.strip():
                        continue

                    author = json.loads(author_json)

                    if not (author_id := author.get('id')):
                        continue

                    for summary_col in ['2yr_mean_citedness', 'h_index', 'i10_index', 'oa_percent', '2yr_works_count', '2yr_cited_by_count', '2yr_i10_index', '2yr_h_index' ]:
                        author[summary_col] = author.get('summary_stats', {}).get(summary_col)

                    # authors
                    author['display_name_alternatives'] = json.dumps(author.get('display_name_alternatives'), ensure_ascii=False)
                    author['last_known_institution'] = (author.get('last_known_institution') or {}).get('id')
                    authors_writer.writerow(author)

                    # ids
                    if author_ids := author.get('ids'):
                        author_ids['author_id'] = author_id
                        ids_writer.writerow(author_ids)

                    # counts_by_year
                    if counts_by_year := author.get('counts_by_year'):
                        for count_by_year in counts_by_year:
                            count_by_year['author_id'] = author_id
                            counts_by_year_writer.writerow(count_by_year)
            files_done += 1
            if FILES_PER_ENTITY and files_done >= FILES_PER_ENTITY:
                break

def flatten_concepts():
    with gzip.open(csv_files['concepts']['concepts']['name'], 'wt', encoding='utf-8') as concepts_csv, \
            gzip.open(csv_files['concepts']['ancestors']['name'], 'wt', encoding='utf-8') as ancestors_csv, \
            gzip.open(csv_files['concepts']['counts_by_year']['name'], 'wt', encoding='utf-8') as counts_by_year_csv, \
            gzip.open(csv_files['concepts']['ids']['name'], 'wt', encoding='utf-8') as ids_csv, \
            gzip.open(csv_files['concepts']['related_concepts']['name'], 'wt', encoding='utf-8') as related_concepts_csv:

        concepts_writer = csv.DictWriter(
            concepts_csv, fieldnames=csv_files['concepts']['concepts']['columns'], extrasaction='ignore'
        )
        concepts_writer.writeheader()

        ancestors_writer = csv.DictWriter(ancestors_csv, fieldnames=csv_files['concepts']['ancestors']['columns'])
        ancestors_writer.writeheader()

        counts_by_year_writer = csv.DictWriter(counts_by_year_csv, fieldnames=csv_files['concepts']['counts_by_year']['columns'])
        counts_by_year_writer.writeheader()

        ids_writer = csv.DictWriter(ids_csv, fieldnames=csv_files['concepts']['ids']['columns'])
        ids_writer.writeheader()

        related_concepts_writer = csv.DictWriter(related_concepts_csv, fieldnames=csv_files['concepts']['related_concepts']['columns'])
        related_concepts_writer.writeheader()

        seen_concept_ids = set()

        files_done = 0
        for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', 'concepts', '*', '*.gz')):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as concepts_jsonl:
                for concept_json in concepts_jsonl:
                    if not concept_json.strip():
                        continue

                    concept = json.loads(concept_json)

                    if not (concept_id := concept.get('id')) or concept_id in seen_concept_ids:
                        continue

                    seen_concept_ids.add(concept_id)

                    concepts_writer.writerow(concept)

                    if concept_ids := concept.get('ids'):
                        concept_ids['concept_id'] = concept_id
                        concept_ids['umls_aui'] = json.dumps(concept_ids.get('umls_aui'), ensure_ascii=False)
                        concept_ids['umls_cui'] = json.dumps(concept_ids.get('umls_cui'), ensure_ascii=False)
                        ids_writer.writerow(concept_ids)

                    if ancestors := concept.get('ancestors'):
                        for ancestor in ancestors:
                            if ancestor_id := ancestor.get('id'):
                                ancestors_writer.writerow({
                                    'concept_id': concept_id,
                                    'ancestor_id': ancestor_id
                                })

                    if counts_by_year := concept.get('counts_by_year'):
                        for count_by_year in counts_by_year:
                            count_by_year['concept_id'] = concept_id
                            counts_by_year_writer.writerow(count_by_year)

                    if related_concepts := concept.get('related_concepts'):
                        for related_concept in related_concepts:
                            if related_concept_id := related_concept.get('id'):
                                related_concepts_writer.writerow({
                                    'concept_id': concept_id,
                                    'related_concept_id': related_concept_id,
                                    'score': related_concept.get('score')
                                })

            files_done += 1
            if FILES_PER_ENTITY and files_done >= FILES_PER_ENTITY:
                break

def flatten_topics():
    with gzip.open(csv_files['topics']['topics']['name'], 'wt', encoding='utf-8') as topics_csv:

        topics_writer = csv.DictWriter(
            topics_csv, fieldnames=csv_files['topics']['topics']['columns'], extrasaction='ignore'
        )
        topics_writer.writeheader()

        seen_topic_ids = set()

        files_done = 0
        for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', 'topics', '*', '*.gz')):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as topics_jsonl:
                for topic_json in topics_jsonl:
                    if not topic_json.strip():
                        continue

                    topic = json.loads(topic_json)
                    
                    topic['subfield'] = topic['subfield']['id']
                    topic['field'] = topic['field']['id']
                    topic['domain'] = topic['domain']['id']

                    if not (topic_id := topic.get('id')) or topic_id in seen_topic_ids:
                        continue

                    seen_topic_ids.add(topic_id)

                    # keywords
                    if (keywords := topic.get('keywords')) is not None:
                        topic['keywords'] = json.dumps(keywords, ensure_ascii=False)

                    topics_writer.writerow(topic)

            files_done += 1
            if FILES_PER_ENTITY and files_done >= FILES_PER_ENTITY:
                break

def flatten_subfields():
    with gzip.open(csv_files['subfields']['subfields']['name'], 'wt', encoding='utf-8') as subfields_csv:
            
        subfields_writer = csv.DictWriter(
            subfields_csv, fieldnames=csv_files['subfields']['subfields']['columns'], extrasaction='ignore'
        )
        subfields_writer.writeheader()

        seen_subfield_ids = set()

        files_done = 0
        for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', 'subfields', '*', '*.gz')):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as subfields_jsonl:
                for subfield_json in subfields_jsonl:
                    if not subfield_json.strip():
                        continue

                    subfield = json.loads(subfield_json)
                    
                    subfield['field'] = subfield['field']['id']
                    subfield['domain'] = subfield['domain']['id']

                    if not (subfield_id := subfield.get('id')) or subfield_id in seen_subfield_ids:
                        continue

                    seen_subfield_ids.add(subfield_id)

                    subfields_writer.writerow(subfield)

            files_done += 1
            if FILES_PER_ENTITY and files_done >= FILES_PER_ENTITY:
                break

def flatten_fields():
    with gzip.open(csv_files['fields']['fields']['name'], 'wt', encoding='utf-8') as fields_csv:
            
        fields_writer = csv.DictWriter(
            fields_csv, fieldnames=csv_files['fields']['fields']['columns'], extrasaction='ignore'
        )
        fields_writer.writeheader()

        seen_field_ids = set()

        files_done = 0
        for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', 'fields', '*', '*.gz')):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as fields_jsonl:
                for field_json in fields_jsonl:
                    if not field_json.strip():
                        continue

                    field = json.loads(field_json)
                    
                    field['domain'] = field['domain']['id']

                    if not (field_id := field.get('id')) or field_id in seen_field_ids:
                        continue

                    seen_field_ids.add(field_id)

                    fields_writer.writerow(field)

            files_done += 1
            if FILES_PER_ENTITY and files_done >= FILES_PER_ENTITY:
                break

def flatten_domains():
    with gzip.open(csv_files['domains']['domains']['name'], 'wt', encoding='utf-8') as domains_csv:
            
        domains_writer = csv.DictWriter(
            domains_csv, fieldnames=csv_files['domains']['domains']['columns'], extrasaction='ignore'
        )
        domains_writer.writeheader()

        seen_domain_ids = set()

        files_done = 0
        for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', 'domains', '*', '*.gz')):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as domains_jsonl:
                for domain_json in domains_jsonl:
                    if not domain_json.strip():
                        continue

                    domain = json.loads(domain_json)
                    
                    if not (domain_id := domain.get('id')) or domain_id in seen_domain_ids:
                        continue

                    seen_domain_ids.add(domain_id)

                    domains_writer.writerow(domain)

            files_done += 1
            if FILES_PER_ENTITY and files_done >= FILES_PER_ENTITY:
                break

def flatten_institutions():
    file_spec = csv_files['institutions']

    with gzip.open(file_spec['institutions']['name'], 'wt', encoding='utf-8') as institutions_csv, \
            gzip.open(file_spec['ids']['name'], 'wt', encoding='utf-8') as ids_csv, \
            gzip.open(file_spec['geo']['name'], 'wt', encoding='utf-8') as geo_csv, \
            gzip.open(file_spec['associated_institutions']['name'], 'wt', encoding='utf-8') as associated_institutions_csv, \
            gzip.open(file_spec['counts_by_year']['name'], 'wt', encoding='utf-8') as counts_by_year_csv:

        institutions_writer = csv.DictWriter(
            institutions_csv, fieldnames=file_spec['institutions']['columns'], extrasaction='ignore'
        )
        institutions_writer.writeheader()

        ids_writer = csv.DictWriter(ids_csv, fieldnames=file_spec['ids']['columns'])
        ids_writer.writeheader()

        geo_writer = csv.DictWriter(geo_csv, fieldnames=file_spec['geo']['columns'])
        geo_writer.writeheader()

        associated_institutions_writer = csv.DictWriter(
            associated_institutions_csv, fieldnames=file_spec['associated_institutions']['columns']
        )
        associated_institutions_writer.writeheader()

        counts_by_year_writer = csv.DictWriter(counts_by_year_csv, fieldnames=file_spec['counts_by_year']['columns'])
        counts_by_year_writer.writeheader()

        seen_institution_ids = set()

        files_done = 0
        for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', 'institutions', '*', '*.gz')):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as institutions_jsonl:
                for institution_json in institutions_jsonl:
                    if not institution_json.strip():
                        continue

                    institution = json.loads(institution_json)

                    if not (institution_id := institution.get('id')) or institution_id in seen_institution_ids:
                        continue

                    seen_institution_ids.add(institution_id)

                    # institutions
                    institution['display_name_acronyms'] = json.dumps(institution.get('display_name_acronyms'), ensure_ascii=False)
                    institution['display_name_alternatives'] = json.dumps(institution.get('display_name_alternatives'), ensure_ascii=False)
                    institutions_writer.writerow(institution)

                    # ids
                    if institution_ids := institution.get('ids'):
                        institution_ids['institution_id'] = institution_id
                        ids_writer.writerow(institution_ids)

                    # geo
                    if institution_geo := institution.get('geo'):
                        institution_geo['institution_id'] = institution_id
                        geo_writer.writerow(institution_geo)

                    # associated_institutions
                    if associated_institutions := institution.get(
                        'associated_institutions', institution.get('associated_insitutions')  # typo in api
                    ):
                        for associated_institution in associated_institutions:
                            if associated_institution_id := associated_institution.get('id'):
                                associated_institutions_writer.writerow({
                                    'institution_id': institution_id,
                                    'associated_institution_id': associated_institution_id,
                                    'relationship': associated_institution.get('relationship')
                                })

                    # counts_by_year
                    if counts_by_year := institution.get('counts_by_year'):
                        for count_by_year in counts_by_year:
                            count_by_year['institution_id'] = institution_id
                            counts_by_year_writer.writerow(count_by_year)

            files_done += 1
            if FILES_PER_ENTITY and files_done >= FILES_PER_ENTITY:
                break

def flatten_publishers():
    with gzip.open(csv_files['publishers']['publishers']['name'], 'wt', encoding='utf-8') as publishers_csv, \
            gzip.open(csv_files['publishers']['counts_by_year']['name'], 'wt', encoding='utf-8') as counts_by_year_csv, \
            gzip.open(csv_files['publishers']['ids']['name'], 'wt', encoding='utf-8') as ids_csv:

        publishers_writer = csv.DictWriter(
            publishers_csv, fieldnames=csv_files['publishers']['publishers']['columns'], extrasaction='ignore'
        )
        publishers_writer.writeheader()

        counts_by_year_writer = csv.DictWriter(counts_by_year_csv, fieldnames=csv_files['publishers']['counts_by_year']['columns'])
        counts_by_year_writer.writeheader()

        ids_writer = csv.DictWriter(ids_csv, fieldnames=csv_files['publishers']['ids']['columns'])
        ids_writer.writeheader()

        seen_publisher_ids = set()

        files_done = 0
        for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', 'publishers', '*', '*.gz')):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as concepts_jsonl:
                for publisher_json in concepts_jsonl:
                    if not publisher_json.strip():
                        continue

                    publisher = json.loads(publisher_json)

                    if not (publisher_id := publisher.get('id')) or publisher_id in seen_publisher_ids:
                        continue

                    seen_publisher_ids.add(publisher_id)

                    # publishers
                    publisher['alternate_titles'] = json.dumps(publisher.get('alternate_titles'), ensure_ascii=False)
                    publisher['country_codes'] = json.dumps(publisher.get('country_codes'), ensure_ascii=False)
                    publishers_writer.writerow(publisher)

                    if publisher_ids := publisher.get('ids'):
                        publisher_ids['publisher_id'] = publisher_id
                        ids_writer.writerow(publisher_ids)

                    if counts_by_year := publisher.get('counts_by_year'):
                        for count_by_year in counts_by_year:
                            count_by_year['publisher_id'] = publisher_id
                            counts_by_year_writer.writerow(count_by_year)

            files_done += 1
            if FILES_PER_ENTITY and files_done >= FILES_PER_ENTITY:
                break

def flatten_sources():
    with gzip.open(csv_files['sources']['sources']['name'], 'wt', encoding='utf-8') as sources_csv, \
            gzip.open(csv_files['sources']['ids']['name'], 'wt', encoding='utf-8') as ids_csv, \
            gzip.open(csv_files['sources']['counts_by_year']['name'], 'wt', encoding='utf-8') as counts_by_year_csv:

        sources_writer = csv.DictWriter(
            sources_csv, fieldnames=csv_files['sources']['sources']['columns'], extrasaction='ignore'
        )
        sources_writer.writeheader()

        ids_writer = csv.DictWriter(ids_csv, fieldnames=csv_files['sources']['ids']['columns'])
        ids_writer.writeheader()

        counts_by_year_writer = csv.DictWriter(counts_by_year_csv, fieldnames=csv_files['sources']['counts_by_year']['columns'])
        counts_by_year_writer.writeheader()

        seen_source_ids = set()

        files_done = 0
        for jsonl_file_name in glob.glob(os.path.join(SNAPSHOT_DIR, 'data', 'sources', '*', '*.gz')):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as sources_jsonl:
                for source_json in sources_jsonl:
                    if not source_json.strip():
                        continue

                    source = json.loads(source_json)

                    if not (source_id := source.get('id')) or source_id in seen_source_ids:
                        continue

                    seen_source_ids.add(source_id)

                    source['issn'] = json.dumps(source.get('issn'))
                    sources_writer.writerow(source)

                    if source_ids := source.get('ids'):
                        source_ids['source_id'] = source_id
                        source_ids['issn'] = json.dumps(source_ids.get('issn'))
                        ids_writer.writerow(source_ids)

                    if counts_by_year := source.get('counts_by_year'):
                        for count_by_year in counts_by_year:
                            count_by_year['source_id'] = source_id
                            counts_by_year_writer.writerow(count_by_year)

            files_done += 1
            if FILES_PER_ENTITY and files_done >= FILES_PER_ENTITY:
                break

def flatten_works():
    file_spec = csv_files['works']

    with ExitStack() as stack:
        works_csv = stack.enter_context(gzip.open(file_spec['works']['name'], 'wt', encoding='utf-8'))
        primary_locations_csv = stack.enter_context(gzip.open(file_spec['primary_locations']['name'], 'wt', encoding='utf-8'))
        locations = stack.enter_context(gzip.open(file_spec['locations']['name'], 'wt', encoding='utf-8'))
        best_oa_locations = stack.enter_context(gzip.open(file_spec['best_oa_locations']['name'], 'wt', encoding='utf-8'))
        authorships_csv = stack.enter_context(gzip.open(file_spec['authorships']['name'], 'wt', encoding='utf-8'))
        biblio_csv = stack.enter_context(gzip.open(file_spec['biblio']['name'], 'wt', encoding='utf-8'))
        concepts_csv = stack.enter_context(gzip.open(file_spec['concepts']['name'], 'wt', encoding='utf-8'))
        topics_csv = stack.enter_context(gzip.open(file_spec['topics']['name'], 'wt', encoding='utf-8'))
        ids_csv = stack.enter_context(gzip.open(file_spec['ids']['name'], 'wt', encoding='utf-8'))
        mesh_csv = stack.enter_context(gzip.open(file_spec['mesh']['name'], 'wt', encoding='utf-8'))
        open_access_csv = stack.enter_context(gzip.open(file_spec['open_access']['name'], 'wt', encoding='utf-8'))
        referenced_works_csv = stack.enter_context(gzip.open(file_spec['referenced_works']['name'], 'wt', encoding='utf-8'))
        related_works_csv = stack.enter_context(gzip.open(file_spec['related_works']['name'], 'wt', encoding='utf-8'))
        counts_by_year_csv = stack.enter_context(gzip.open(file_spec['counts_by_year']['name'], 'wt', encoding='utf-8'))
        sustainable_development_goals_csv = stack.enter_context(gzip.open(file_spec['sustainable_development_goals']['name'], 'wt', encoding='utf-8'))
        grants_csv = stack.enter_context(gzip.open(file_spec['grants']['name'], 'wt', encoding='utf-8'))

        works_writer = init_dict_writer(works_csv, file_spec['works'], extrasaction='ignore') #opened gzip csv file, column names, ignore extra columns
        primary_locations_writer = init_dict_writer(primary_locations_csv, file_spec['primary_locations'])
        locations_writer = init_dict_writer(locations, file_spec['locations'])
        best_oa_locations_writer = init_dict_writer(best_oa_locations, file_spec['best_oa_locations'])
        authorships_writer = init_dict_writer(authorships_csv, file_spec['authorships'])
        biblio_writer = init_dict_writer(biblio_csv, file_spec['biblio'])
        concepts_writer = init_dict_writer(concepts_csv, file_spec['concepts'])
        topics_writer = init_dict_writer(topics_csv, file_spec['topics'])
        ids_writer = init_dict_writer(ids_csv, file_spec['ids'], extrasaction='ignore')
        mesh_writer = init_dict_writer(mesh_csv, file_spec['mesh'])
        open_access_writer = init_dict_writer(open_access_csv, file_spec['open_access'])
        referenced_works_writer = init_dict_writer(referenced_works_csv, file_spec['referenced_works'])
        related_works_writer = init_dict_writer(related_works_csv, file_spec['related_works'])
        counts_by_year_writer = init_dict_writer(counts_by_year_csv, file_spec['counts_by_year'])
        sustainable_development_goal_writer = init_dict_writer(sustainable_development_goals_csv, file_spec['sustainable_development_goals'], extrasaction='ignore')
        grants_writer = init_dict_writer(grants_csv, file_spec['grants'], extrasaction='ignore')

        files_done = 0
        for jsonl_file_name in tqdm(glob.glob(os.path.join(SNAPSHOT_DIR, 'data', 'works', '*', '*.gz'))):
            print(jsonl_file_name)
            with gzip.open(jsonl_file_name, 'r') as works_jsonl:
                for work_json in works_jsonl:
                    if not work_json.strip():
                        continue

                    work = json.loads(work_json)

                    if not (work_id := work.get('id')):
                        continue

                    # works
                    if (abstract := work.get('abstract_inverted_index')) is not None:
                        work['abstract_inverted_index'] = json.dumps(abstract, ensure_ascii=False)

                    work['2yr_cited_by_count'] = work.get('summary_stats', {}).get('2yr_cited_by_count')
                    
                    # if (counts_by_year := work.get('counts_by_year')) is not None:
                    #     work['counts_by_year'] = json.dumps(counts_by_year, ensure_ascii=False)

                    works_writer.writerow(work)

                    # primary_locations
                    if primary_location := (work.get('primary_location') or {}):
                        if primary_location.get('source') and primary_location.get('source').get('id'):
                            primary_locations_writer.writerow({
                                'work_id': work_id,
                                'source_id': primary_location['source']['id'],
                                'landing_page_url': primary_location.get('landing_page_url'),
                                'pdf_url': primary_location.get('pdf_url'),
                                'is_oa': primary_location.get('is_oa'),
                                'version': primary_location.get('version'),
                                'license': primary_location.get('license'),
                            })

                    # locations
                    if locations := work.get('locations'):
                        for location in locations:
                            if location.get('source') and location.get('source').get('id'):
                                locations_writer.writerow({
                                    'work_id': work_id,
                                    'source_id': location['source']['id'],
                                    'landing_page_url': location.get('landing_page_url'),
                                    'pdf_url': location.get('pdf_url'),
                                    'is_oa': location.get('is_oa'),
                                    'version': location.get('version'),
                                    'license': location.get('license'),
                                })

                    # best_oa_locations
                    if best_oa_location := (work.get('best_oa_location') or {}):
                        if best_oa_location.get('source') and best_oa_location.get('source').get('id'):
                            best_oa_locations_writer.writerow({
                                'work_id': work_id,
                                'source_id': best_oa_location['source']['id'],
                                'landing_page_url': best_oa_location.get('landing_page_url'),
                                'pdf_url': best_oa_location.get('pdf_url'),
                                'is_oa': best_oa_location.get('is_oa'),
                                'version': best_oa_location.get('version'),
                                'license': best_oa_location.get('license'),
                            })

                    # authorships
                    if authorships := work.get('authorships'):
                        for authorship in authorships:
                            if author_id := authorship.get('author', {}).get('id'):
                                institutions = authorship.get('institutions')
                                institution_ids = [i.get('id') for i in institutions]
                                institution_ids = [i for i in institution_ids if i]
                                institution_ids = institution_ids or [None]

                                for institution_id in institution_ids:
                                    authorships_writer.writerow({
                                        'work_id': work_id,
                                        'author_position': authorship.get('author_position'),
                                        'author_id': author_id,
                                        'institution_id': institution_id,
                                        'raw_affiliation_string': authorship.get('raw_affiliation_string'),
                                    })

                    # biblio
                    if biblio := work.get('biblio'):
                        biblio['work_id'] = work_id
                        biblio_writer.writerow(biblio)

                    # concepts
                    for concept in work.get('concepts'):
                        if concept_id := concept.get('id'):
                            concepts_writer.writerow({
                                'work_id': work_id,
                                'concept_id': concept_id,
                                'score': concept.get('score'),
                            })
                    
                    # topics
                    if topics := work.get('topics'):
                        for topic in topics:
                            if topic_id := topic.get('id'):
                                topics_writer.writerow({
                                    'work_id': work_id,
                                    'topic_id': topic_id,
                                    # 'display_name': topic.get('display_name'), # Should be in topics.csv
                                    'score': topic.get('score'),
                                    # 'subfield': topic.get('subfield'),
                                    # 'field': topic.get('field'),
                                    # 'domain': topic.get('domain')
                                })

                    # ids
                    if ids := work.get('ids'):
                        ids['work_id'] = work_id
                        ids_writer.writerow(ids)

                    # mesh
                    for mesh in work.get('mesh'):
                        mesh['work_id'] = work_id
                        mesh_writer.writerow(mesh)

                    # open_access
                    if open_access := work.get('open_access'):
                        open_access['work_id'] = work_id
                        # apc list and paid should strictly go into their own tables, but this'll be easier to work with
                        if apc_list := work.get('apc_list'):
                            open_access['apc_list_value_usd'] = apc_list.get('value_usd')
                        if apc_paid := work.get('apc_paid'):
                            open_access['apc_paid_value_usd'] = apc_paid.get('value_usd')
                        open_access_writer.writerow(open_access)

                    # referenced_works
                    for referenced_work in work.get('referenced_works'):
                        if referenced_work:
                            referenced_works_writer.writerow({
                                'work_id': work_id,
                                'referenced_work_id': referenced_work
                            })

                    # related_works
                    for related_work in work.get('related_works'):
                        if related_work:
                            related_works_writer.writerow({
                                'work_id': work_id,
                                'related_work_id': related_work
                            })

                    # counts_by_year
                    if counts_by_year := work.get('counts_by_year'):
                        for count_by_year in counts_by_year:
                            count_by_year['work_id'] = work_id
                            counts_by_year_writer.writerow(count_by_year)

                    # sustainable_development_goals
                    if sustainable_development_goals := work.get('sustainable_development_goals'):
                        for sustainable_development_goal in sustainable_development_goals:
                            sustainable_development_goal['work_id'] = work_id
                            sustainable_development_goal_writer.writerow(sustainable_development_goal)

                    # grants
                    if grants := work.get('grants'):
                        for grant in grants:
                            grant['work_id'] = work_id
                            grants_writer.writerow(grant)

            files_done += 1
            if FILES_PER_ENTITY and files_done >= FILES_PER_ENTITY:
                break

def init_dict_writer(csv_file, file_spec, **kwargs):
    writer = csv.DictWriter(
        csv_file, fieldnames=file_spec['columns'], **kwargs
    )
    writer.writeheader()
    return writer

if __name__ == '__main__':
    print(f'Starting flattening. {FILES_PER_ENTITY = } (0 means all files)')
    flatten_authors()
    flatten_concepts()
    flatten_topics()
    flatten_subfields()
    flatten_fields()
    flatten_domains()
    flatten_institutions()
    flatten_publishers()
    flatten_sources()
    flatten_works()

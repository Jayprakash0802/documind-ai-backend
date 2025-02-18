from elasticsearch import Elasticsearch
from config import Config
from datetime import datetime,timezone
import traceback

# Initialize Elasticsearch connection
es = Elasticsearch( [Config.ELASTICSEARCH_URL])

# Enable Request Caching for Optimized Queries
def check_index_exists(index_name):
    """Check if the index exists"""
    return es.indices.exists(index=index_name)

def enable_cache():
    """Enable request cache for the 'documents' index"""
    if not check_index_exists("documents"):
        print("Index not found")
        return None
    try:
        response = es.indices.put_settings(
            index="documents",
            body={"index.requests.cache.enable": True}
        )
        print("Request caching enabled:", response)
    except Exception as e:
        print("Error enabling request caching:", str(e))


# Index Document in Elasticsearch
def index_document(document_id: str, user_id: str, title: str, extracted_text: str, summary: str):
    """
    Indexes a document into the 'documents' index in Elasticsearch.

    :param document_id: Unique document ID
    :param user_id: ID of the user who uploaded the document
    :param title: Title of the document
    :param extracted_text: Full extracted text of the document
    :param summary: Summarized text of the document
    """
    index_name = "documents"

    # Check if index exists, if not, create it with proper mappings
    if not es.indices.exists(index=index_name):
        print(f"Index '{index_name}' does not exist. Creating index with proper mapping...")

        index_settings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "edge_ngram_analyzer": {
                            "type": "custom",
                            "tokenizer": "edge_ngram_tokenizer",
                            "filter": ["lowercase"]
                        }
                    },
                    "tokenizer": {
                        "edge_ngram_tokenizer": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 10,
                            "token_chars": ["letter", "digit"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "user_id": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "edge_ngram_analyzer"},
                    "content": {"type": "text", "analyzer": "edge_ngram_analyzer"},
                    "summary": {"type": "text", "analyzer": "edge_ngram_analyzer"},
                    "title_suggest": {"type": "completion"},  # Autocomplete field
                    "timestamp": {"type": "date"}
                }
            }
        }

        es.indices.create(index=index_name, body=index_settings)

    # Prepare document body
    utc_time = datetime.now(timezone.utc).isoformat()
    doc_body = {
        "user_id": user_id,
        "document_id":document_id,
        "unique_id":f"{user_id}_{document_id}",
        "title": title,
        "title_suggest": {"input": title},  # Autocomplete field
        "content": extracted_text,
        "summary": summary,
        "timestamp": utc_time  # Proper timestamp format
    }
    try:
        response = es.index(index=index_name, id=f"{user_id}_{document_id}", body=doc_body)
        print(f"Document {document_id} indexed successfully:", response)
    except Exception as e:
        print("Error indexing document:", str(e))

def search_documents(query: str, filters: dict = None):
    """Enhanced search with proper fuzzy matching and filter handling."""
    if not query or len(query) < 2:  # Ignore very short/random queries
        return {"documents": [], "suggestions": []}

    search_query = {
        "query": {
            "bool": {
                "must": [  # Ensure it actually matches meaningful content
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title", "content", "summary"],
                            "fuzziness": "AUTO",
                            "operator": "and"  # Requires stronger match
                        }
                    }
                ],
                "should": [  # Optional conditions to expand results if no strict match
                    {
                        "query_string": {
                            "query": f"*{query}*",  # Wildcard search for partial terms
                            "fields": ["title", "content", "summary"],
                            "default_operator": "AND"
                        }
                    }
                ],
                "minimum_should_match": 1,
                "filter": []
            }
        },
        "size": 10,
        "sort": [
            {"_score": "desc"}  # Prioritize most relevant matches
        ],
        "suggest": {
            "doc-suggest": {
                "prefix": query.lower(),
                "completion": {"field": "title_suggest"}
            }
        }
    }

    # Add filters if provided (e.g., date range, user_id)
    if filters:
        for key, value in filters.items():
            if isinstance(value, dict):  # Date range filter
                search_query["query"]["bool"]["filter"].append({"range": {key: value}})
            else:  # Exact match filter
                search_query["query"]["bool"]["filter"].append({"term": {key: value}})

    try:
        result = es.search(index="documents", body=search_query)

        # Extract suggestions safely
        suggestions = []
        if result.get("suggest", {}).get("doc-suggest"):
            suggestions = [
                option["text"]
                for option in result["suggest"]["doc-suggest"][0].get("options", [])
            ]

        # Extract valid documents with a score threshold (avoid garbage results)
        documents = [
            hit["_source"]
            for hit in result["hits"]["hits"]
            if hit["_score"] > 1.5  # Ignore extremely weak matches
        ]

        return {"documents": documents, "suggestions": suggestions}

    except Exception as e:
        print(f"Error searching documents: {str(e)}")
        return {"documents": [], "suggestions": []}

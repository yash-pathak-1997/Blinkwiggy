from flask import Blueprint, request, jsonify
from elasticsearch import Elasticsearch

analytics_bp = Blueprint('analytics', __name__)
es = Elasticsearch("http://host.docker.internal:9200")


@analytics_bp.route('/spent-between/<username>')
def spent_between(username):
    index_name = f"{username}_data"  # Dynamic index name based on username
    start_date = request.args.get('start_date')  # Expect format: "YYYY-MM-DD"
    end_date = request.args.get('end_date')  # Expect format: "YYYY-MM-DD"

    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "Date": {
                                "gte": start_date,
                                "lte": end_date
                            }
                        }
                    }
                ]
            }
        },
        "aggs": {
            "total_spent": {
                "sum": {
                    "field": "price"
                }
            }
        }
    }
    response = es.search(index=index_name, body=query)
    total_spent = response["aggregations"]["total_spent"]["value"]

    return jsonify({"username": username, "total_spent": total_spent})


@analytics_bp.route('/category-spending/<username>/<category>')
def category_spending(username, category):
    index_name = f"{username}_data"  # Dynamic index name based on username
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "category.keyword": category
                        }
                    }
                ]
            }
        },
        "aggs": {
            "total_spent": {
                "sum": {
                    "field": "price"
                }
            }
        }
    }
    response = es.search(index=index_name, body=query)
    total_spent = response["aggregations"]["total_spent"]["value"]

    return jsonify({"category": category, "total_spent": total_spent})


@analytics_bp.route('/monthly-trend/<username>')
def monthly_trend(username):
    index_name = f"{username}_data"  # Dynamic index name based on username
    query = {
        "aggs": {
            "monthly_spending": {
                "date_histogram": {
                    "field": "Date",
                    "calendar_interval": "month",
                    "format": "yyyy-MM"
                },
                "aggs": {
                    "total_spent": {
                        "sum": {
                            "field": "price"
                        }
                    }
                }
            }
        }
    }
    response = es.search(index=index_name, body=query)
    trends = [{
        "month": bucket["key_as_string"],
        "total_spent": bucket["total_spent"]["value"]
    } for bucket in response["aggregations"]["monthly_spending"]["buckets"]]

    return jsonify(trends)


@analytics_bp.route('/top-costliest-items/<username>')
def top_costliest_items(username):
    index_name = f"{username}_data"  # Dynamic index name based on username
    query = {
        "size": 5,
        "sort": [
            {
                "price": {
                    "order": "desc"
                }
            }
        ]
    }
    response = es.search(index=index_name, body=query)
    items = [{
        "name": hit["_source"]["name"],
        "price": hit["_source"]["price"],
        "category": hit["_source"]["category"],
        "order_id": hit["_source"]["Order ID"],
        "total_amount": hit["_source"]["Total Amount"]
    } for hit in response["hits"]["hits"]]

    return jsonify(items)


@analytics_bp.route('/autocomplete-items/<username>')
def search_item(username, item_name):
    index_name = f"{username}_data"  # Dynamic index name based on username

    # Constructing the search query to search by item name (fuzzy match for flexibility)
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "name": {
                                "query": item_name,
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                ]
            }
        },
        "size": 10
    }

    # Performing the search query
    response = es.search(index=index_name, body=query)

    # Parsing and formatting the response to return only relevant fields
    items = [{
        "name": hit["_source"]["name"],
        "quantity": hit["_source"]["quantity"],
        "price": hit["_source"]["price"],
        "category": hit["_source"]["category"],
        "order_id": hit["_source"]["Order ID"],
        "total_amount": hit["_source"]["Total Amount"],
        "date": hit["_source"]["Date"]
    } for hit in response["hits"]["hits"]]

    # Return the list of matching items as a JSON response
    return jsonify(items)

import os
from typing import List

import weaviate
from weaviate.util import generate_uuid5

client = weaviate.Client(
    embedded_options=weaviate.EmbeddedOptions(),
    additional_headers={
        "X-OpenAI-Api-Key": os.environ["OPENAI_APIKEY"]
    }
)

DEFAULT_COLLECTION_CONFIG = {
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "generative-openai": {}
    }
}


def build_collection_config(collection_name: str) -> dict:
    collection_config = DEFAULT_COLLECTION_CONFIG.copy()
    collection_config['class'] = collection_name
    return collection_config


def create_collection(collection_name: str) -> bool:
    if client.schema.exists(collection_name):
        print(f"Collection '{collection_name}' already exists")
        return True
    else:
        collection_config = build_collection_config(collection_name)
        client.schema.create(collection_config)
        print(f"Added collection: '{collection_name}'")
        return True


def add_object(collection_name, data_object):
    client.data_object.create(
        data_object=data_object,
        class_name=collection_name,
        uuid=generate_uuid5(data_object)
    )


def add_objects(collection_name, data_objects):
    client.batch.configure(batch_size=100)
    with client.batch as batch:
        for data_object in data_objects:
            batch.add_data_object(
                data_object=data_object,
                class_name=collection_name,
                uuid=generate_uuid5(data_object)
            )


def get_all_property_names(collection_name) -> List[str]:
    """
    Get property names from the Weaviate collection
    :return:
    """
    class_schema = client.schema.get(collection_name)
    return [p["name"] for p in class_schema["properties"]]


def get(collection_name, source_path):
    if not client.schema.exists(collection_name):
        return None
    else:
        wv_filter = {
            "path": ["source_path"],
            "operator": "Equal",
            "valueText": source_path
        }
        count_response = client.query.aggregate(collection_name).with_meta_count().do()
        count = count_response["data"]["Aggregate"][collection_name][0]["meta"]["count"]
        print(count)
        if count == 0:
            return None
        else:
            property_names = get_all_property_names(collection_name)
            response = (
                client.query.get(collection_name, property_names)
                .with_where(wv_filter)
                .do()
            )
            objects = response["data"]["Get"][collection_name]
            print(objects)
            if len(objects) > 0:
                raise AssertionError("There should be just one object matching this criteria but there are multiple!")
            else:
                return objects[0]

import weaviate
from weaviate.classes.init import Auth
import weaviate.classes as wvc
from aisolution.settings import WEAVIATE_PASSWORD, WEAVIATE_HOST

# Initialize Weaviate client
weaviate_client = weaviate.connect_to_weaviate_cloud(cluster_url=WEAVIATE_HOST, auth_credentials=Auth.api_key(WEAVIATE_PASSWORD))

# Define Weaviate schema if not created already
def create_schema():
    try:
        properties = [
            wvc.config.Property(name="textChunk", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="chunkRank", data_type=wvc.config.DataType.INT),
            wvc.config.Property(name="documentUUID", data_type=wvc.config.DataType.UUID),
        ]
        res = weaviate_client.collections.create(
            name="Document_db",
            properties=properties
        )
    except Exception as e:
        print(e)
create_schema()
weaviate_client.close()

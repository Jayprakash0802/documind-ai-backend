@echo off
python -m black .
python -m isort .
python -m pytest

docker run -d --name es01 --net elastic -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.17.1

docker run -d --name kib01 --net elastic -p 5601:5601  -e "ELASTICSEARCH_HOSTS=http://es01:9200" -e "xpack.security.enabled=false"  docker.elastic.co/kibana/kibana:8.17.1
include api.env
export

build:
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

status:
	docker-compose ps

load_data:
	curl -XPUT http://127.0.0.1:9200/${ES_INDEX_NAME} -H 'Content-Type: application/json' -d @index.json
	docker-compose exec api python etl.py

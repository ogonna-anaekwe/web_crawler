.PHONY: start
start:
	docker compose up --build --remove-orphans

.PHONY: run
run:
	@$(call docker_exec, 'python app/main.py')

.PHONY: stop
stop:
	@$(call docker_exec, 'rm -rf /web_crawler/*.json')
	docker compose down --rmi all

.PHONY: test
test:
	@$(call docker_exec, 'python -m unittest -v')	

.PHONY: clean
clean:
	rm -rf `find . -type d -name __pycache__`

define docker_exec
	# Executes the given command/argument in the container's terminal

	echo "Running $(1) in the container's terminal"	
	docker exec `docker ps --format '{{.Names}}' | grep web_crawler` bash -c  $(1)
endef
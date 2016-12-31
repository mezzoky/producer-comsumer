Update
# Task
- setup docker for rabbitmq, python, and go
- make queue
- publish subscribe
- listen on queue
- dispatch and receive task
- deliver task to queue and catch task from queue and return back task to queue
- python client: pika
- twisted adapter for pika

# Task 2
- convert the demo producer-consumer server into golang

# Task 3
- http for UI to illustrate the queue status

# Refactor
- change Tpl print to use builtin logging
- merge ConsumerDirectExchange and ConsumerTopicExchange into one base class

# GUI - web
- producer N register, update, delete the data to web server (maybe flask or tornado)
- worker N register, update, delete the data to web server
- web server send the full data on connect via websocket
- web server publish the chunk of small data about producers or workers updates to websocket port

## data
- data:
    - task id (int)
    - producer name (str)
    - queue name (str)
    - exchange type (map[str]str)
    - delivery mode (str)
- data structure:
    - producer collection list
        - producer docker container name or container hash hostname
        - register a producer:
            {
                hosname: 3487e34,
                name: producer_1,
                task_dispatched: [],
            }
        - update a producer: {
            method: dispatched_a_new_task,
            task: {
                producer: producer_1,
                id: 1,
                delivery_mode: persistent,
                exchange_type: {
                    exchange: fanout
                }
        }
        - push into producer collection list's task_dispatched list
        - delete a producer: {
            producer: producer_1,
        }
    - consumer collection list
        - register: {
            hostname: 23987d4,
            name: worker_1,
            tasks_taken: [],
        }
        - take task: {
            method: take_task,
            worker: worker_1,
            task_id: 1,
        }
        - completed task: {
            method: completed_task,
            worker: worker_1,
            task_id: 1,
        }
        - delete: {
            worker: worker_1
        }
    - task collection list

function Host(props) {
    const {name, tasks} = props

    return (
        <div className={"host"}>
            <div>hostname: {name}</div>
            <div>tasks: {tasks.join(' : ')}</div>
        </div>
    )
}

function Producer(props) {
    const { hosts } = props
    const containers = Object.keys(hosts).map(hostname => {
        return (
            <Host key={hostname} name={hostname} tasks={hosts[hostname]}/>
        )
    })
    return (
        <div>
            <h1>Producer</h1>
            {containers}
        </div>
    )
}

function Consumer(props) {
    const { hosts } = props
    const containers = Object.keys(hosts).map(hostname => {
        return (
            <Host key={hostname} name={hostname} tasks={hosts[hostname]}/>
        )
    })
    return (
        <div>
            <h1>Consumer</h1>
            {containers}
        </div>
    )
}

function Tasks(props) {
    const {tasks} = props
    const containers = Object.keys(tasks).map(id => {
        const {
            ack,
            body,
            hostname,
            module,
            queue,
            routing_key,
            status,
            exchange,
        } = tasks[id]
        console.log(tasks[id])
        return (
            <div key={id} className="task">
                <div>id: {id}</div>
                <div>ack: {ack ? 'true' : 'false'}</div>
                <div>body: {body}</div>
                <div>queue: {queue}</div>
                <div>routing_key: {routing_key}</div>
                <div>status: {status}</div>
                <div>exchange: {exchange}</div>
                <div>module: {module}</div>
            </div>
        )
    })
    return (
        <div>
            <h1>Tasks</h1>
            {containers}
        </div>
    )
}

class App extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            producerHosts: {},
            consumerHosts: {},
            tasks: {},
        }
        this.events = {
            delivering_task: this.deliveringTask.bind(this),
            delivered_task: this.deliveredTask.bind(this),
            taking_task: this.takingTask.bind(this),
            completed_task: this.completedTask.bind(this),
            initialize: this.initialize.bind(this),
        }
    }
    componentDidMount() {
        this.ws = new WebSocket('ws://localhost:8888/ws')
        this.ws.onopen = (e) => {console.log('ws open')}
        this.ws.onclose = (e) => {console.log('ws closed')}
        this.ws.onmessage = (e) => {
            const data = JSON.parse(e.data)
            const callback = this.events[data.method]
            callback(data.data)
        }
    }
    initialize(data) {
        this.setState({
            consumerHosts: data.consumer_hosts,
            producerHosts: data.producer_hosts,
            tasks: data.tasks,
        })
    }
    deliveringTask(data) {
        console.log('delivering', data.hostname)
        let {tasks, producerHosts} = this.state

        tasks[data.id] = data
        if (producerHosts.hasOwnProperty(data.hostname)) {
            if (producerHosts[data.hostname].indexOf(data.id) === -1) {
                producerHosts[data.hostname].push(data.id)
            }
        } else {
            producerHosts[data.hostname] = [data.id]
        }

        this.setState({
            tasks,
            producerHosts,
        })
    }
    deliveredTask(data) {
        console.log('delivered', data.hostname)
        let {tasks, producerHosts} = this.state

        tasks[data.id] = data
        if (producerHosts.hasOwnProperty(data.hostname)) {
            if (producerHosts[data.hostname].indexOf(data.id) === -1) {
                producerHosts[data.hostname].push(data.id)
            }
        } else {
            producerHosts[data.hostname] = [data.id]
        }

        this.setState({
            tasks,
            producerHosts,
        })
    }
    takingTask(data) {
        console.log('taking', data.hostname)
        let {tasks, consumerHosts} = this.state

        tasks[data.id] = data
        if (consumerHosts.hasOwnProperty(data.hostname)) {
            if (consumerHosts[data.hostname].indexOf(data.id) === -1) {
                consumerHosts[data.hostname].push(data.id)
            }
        } else {
            consumerHosts[data.hostname] = [data.id]
        }

        this.setState({
            tasks,
            consumerHosts,
        })
    }
    completedTask(data) {
        console.log('completed', data.hostname)
        let {tasks, consumerHosts} = this.state

        tasks[data.id] = data
        if (consumerHosts.hasOwnProperty(data.hostname)) {
            if (consumerHosts[data.hostname].indexOf(data.id) === -1) {
                consumerHosts[data.hostname].push(data.id)
            }
        } else {
            consumerHosts[data.hostname] = [data.id]
        }

        this.setState({
            tasks,
            consumerHosts,
        })
    }
    render() {
        return (
            <div>
                <Producer hosts={this.state.producerHosts}/>
                <Consumer hosts={this.state.consumerHosts}/>
                <Tasks tasks={this.state.tasks}/>
            </div>
        )
    }
}


ReactDOM.render(
  <App/>,
  document.getElementById('app')
);

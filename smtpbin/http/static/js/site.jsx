class InboxNav extends React.Component {
  render() {
    return (
        <aside>
          <h3>Inboxes</h3>
          {this.props.inboxes.map(inbox =>
              <a
                  style={{
                    backgroundColor: inbox == this.props.inbox ? "#dadada": null
                  }}
                  onClick={ e => this.props.onClick(inbox) }
                  key={inbox.name}>
                {inbox.name}
              </a>
          )}
        </aside>
    );
  }
}

class MessageList extends React.Component {
  render() {
    return (
        <nav class="list">
          {this.props.messages.map(message =>
              <a class="message"
                  style={{
                    backgroundColor: message == this.props.message ? "#dadada": null
                  }}
                 onClick={ e => this.props.onClick(message) }
                 key={message.id}>
                Message 1
              </a>
          )}
        </nav>
    );
  }
}

class MessageBody extends React.Component {
  constructor() {
    super();

    this.state = {body: null}
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.inbox && nextProps.message) {
      fetch('/api/inbox/' + nextProps.inbox.name + '/messages/' + nextProps.message.id)
          .then(r => {
            r.json().then(d => {
              this.setState({body: d.body})
            })
          })
    } else {
      this.setState({body: null});
    }
  }

  render() {
    if (this.state.body) {
      return (
          <section class="body">
              <pre>
                {this.state.body}
              </pre>
          </section>
      )
    } else {
      return (
          <section class="body">
            Select an email
          </section>
      );
    }
  }
}

class Messages extends React.Component {
  constructor() {
    super();

    this.state = {
      messages: [],
      selectedMessage: null,
    }
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.inbox) {
      fetch('/api/inbox/' + nextProps.inbox.name + '/messages')
          .then(r =>
              r.json().then(d =>
                  this.setState({messages: d})
              )
          )
    }
  }

  handleMessageSelect(message) {
    this.setState({selectedMessage: message})
  }

  render() {
    return (
        <article class="messages">
          <MessageList inbox={this.props.inbox}
                       messages={this.state.messages}
                       message={this.state.selectedMessage}
                       onClick={e => this.handleMessageSelect(e)}/>
          <MessageBody inbox={this.props.inbox}
                       message={this.state.selectedMessage}/>
        </article>
    );
  }
}

class App extends React.Component {
  constructor() {
    super();

    this.state = {
      inboxes: [],
      selectedInbox: null,
    };
  }

  componentWillMount() {
    fetch('/api/inbox')
        .then(r => {
          r.json().then(d => {
            this.setState({inboxes: d})
          })
        })
  }

  handleInboxSelect(inbox) {
    this.setState({selectedInbox: inbox});
  }

  render() {
    return (
        <main>
          <InboxNav inbox={this.state.selectedInbox}
                    inboxes={this.state.inboxes}
                    onClick={e => this.handleInboxSelect(e)}/>
          <Messages inbox={this.state.selectedInbox}/>
        </main>
    );
  }
}

ReactDOM.render(
    <App/>,
    document.getElementById("app")
)
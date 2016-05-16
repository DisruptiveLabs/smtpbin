class InboxNav extends React.Component {
  render() {
    return (
        <aside>
          <h3>Inboxes</h3>
          {this.props.inboxes.map(inbox =>
              <a
                  style={{
                    backgroundColor: inbox.name == this.props.selectedInbox ? "#dadada": null
                  }}
                  onClick={ e => this.props.onClick(inbox) }
                  key={inbox.name}>
                {inbox.name} ({inbox.unread} unread)
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
                    backgroundColor: message.id == this.props.selectedMessage ? "#dadada": null
                  }}
                 onClick={ e => this.props.onClick(message) }
                 key={message.id}>
                <div class="from">{message.fromaddr}</div>
                <div class="to">{message.toaddr}</div>
                <div class="subject">{message.subject}</div>
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
    if (nextProps.selectedInbox && nextProps.message) {
      if (nextProps.message !== this.props.message) {
        fetch('/api/inbox/' + nextProps.selectedInbox + '/messages/' + nextProps.message.id)
            .then(r => {
              r.json().then(d => {
                this.setState({body: d.body})
              })
            });
        this.setState({body: null});
      }
    } else {
      this.setState({body: null});
    }
  }

  renderMIME(mime_message) {
    var {headers, body} = mime_message;

    switch (headers['content-type'].split(";")[0].trim()) {
      case 'multipart/mixed':
      case 'multipart/alternative':
      case 'multipart/related':
        return (<div>

          {body.map(b => this.renderMIME(b))}
        </div>);

      case 'text/html':
        return (<div dangerouslySetInnerHTML={{__html: body}}/>);
      case 'text/plain':
        return (<pre>{body}</pre>);
      default:
        if (body instanceof String) {
          return (<pre>{body}</pre>);
        } else {
          return (<pre>{JSON.stringify(body)}</pre>);
        }

    }
  }

  renderBody() {
    if (this.state.body) {
      var message = parseMIME(this.state.body);

      return (
          <div>
            {this.renderMIME(message)}
          </div>
      );
    }
  }

  render() {
    if (this.props.message) {
      return (
          <section class="body">
            From: {this.props.message.fromaddr}<br/>
            To: {this.props.message.toaddr}<br/>
            Received: {this.props.message.received}<br/>
            {this.renderBody()}
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
    if (nextProps.selectedInbox && nextProps.selectedInbox !== this.props.selectedInbox) {
      fetch('/api/inbox/' + nextProps.selectedInbox + '/messages')
          .then(r =>
              r.json().then(d =>
                  this.setState({messages: d})
              )
          )
    }
  }

  handleMessageSelect(message) {
    this.setState({selectedMessage: message.id})
  }

  render() {
    return (
        <article class="messages">
          <MessageList messages={this.state.messages}
                       selectedMessage={this.state.selectedMessage}
                       onClick={e => this.handleMessageSelect(e)}/>
          <MessageBody selectedInbox={this.props.selectedInbox}
                       message={this.state.messages.find(m => m.id == this.state.selectedMessage)}/>
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

    this.ws = this.createWebSocket()
  }

  createWebSocket() {
    var ws = new WebSocket("ws://" + document.location.hostname + ":" + window.WEBSOCKET_PORT);

    ws.onerror = e => this.socketError(e);
    ws.onmessage = e => this.onMessage(e);

    return ws
  }

  socketError(e) {
    console.error(e)

    setTimeout(() => this.ws = this.createWebSocket(), 1000);
  }

  onMessage(e) {
    var msg = JSON.parse(e.data);
    var type = msg.type;
    var value = msg.data;

    switch (type) {
      case 'message':
        var inboxes = JSON.parse(JSON.stringify(this.state.inboxes));

        for (var i = 0; i < inboxes.length; i++) {
          var inbox = inboxes[i];
          if (inbox.id === value.inbox) {
            inbox.unread++;
            inbox.count++;
            console.log(inbox)
          }
        }

        this.setState({inboxes});

        if (this.state.selectedInbox == this.state.inboxes.filter(i => i.id == value.inbox)[0].name) {
          var messages = this.messages.state.messages;
          messages.unshift(value);
          this.messages.setState({messages});
        }

        break;
      case 'inbox':
        break;
      default:
        console.log("Unhandled websocket message: ", e);
    }
  }

  handleInboxSelect(inbox) {
    this.setState({selectedInbox: inbox.name});
  }

  render() {
    return (
        <main>
          <InboxNav selectedInbox={this.state.selectedInbox}
                    inboxes={this.state.inboxes}
                    onClick={e => this.handleInboxSelect(e)}/>
          <Messages selectedInbox={this.state.selectedInbox}
                    ref={c => this.messages = c}/>
        </main>
    );
  }
}

ReactDOM.render(
    <App/>,
    document.getElementById("app")
);
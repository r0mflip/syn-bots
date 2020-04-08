import {html, render, Component} from '/static/js/third_party/htm-preact.js';

const Results = ({hndle, results}) => {
  if (hndle && results) {
    const isbot = results.isbot ? 'bot' : 'notbot';
    return html`
      <div class="results">
        <!-- <p class="isbot isbot--${results.isbot ? 'bot' : 'notbot'}">${results.isbot ? 'bot!' : 'clean!'}</p> -->
        ${
          results.isbot
            ? html`<p class="isbit--text ${isbot}">The account <b>@${hndle}</b> seems to exhibit bot like behavior.</p>` : ''}
        ${
          !results.isbot
            ? html`<p class="isbot--text ${isbot}">Great! The account <b>@${hndle}</b> looks clean of suspicious bot behavior.</p>` : ''}
      </div>
    `;
  }

  return html``;
}

class App extends Component {
  state = {hndle: '', results: {}}

  constructor(...args) {
    super(...args);
    this.onValueChange = this.onValueChange.bind(this);
  }

  async getPrediction() {
    const {hndle} = this.state;

    if (!hndle) {
      return;
    }

    const results = await (await fetch(`/predict/${hndle}`)).json();
    // console.log(results);
    this.setState({hndle, results});
  }

  onValueChange(e) {
    this.setState({hndle: e.target.value, results: []});
  }

  render({}, {hndle, results}) {
    return html`
      <div class="main__container">
        <h1>SYN</h1>
        <p>Bot activity predition using Machine Learning for Twitter</p>

        <label>
          <span>Twitter handle</span>
          <input type="text" value=${hndle} onChange=${this.onValueChange} />
        </label>

        <button onClick=${_ => this.getPrediction()}>Check</button>

        <${Results} hndle=${hndle} results=${results} />
      </div>
    `;
  }
}

const init = _ => {
  render(html`
    <${App} />
  `, document.querySelector('main'));
};

window.addEventListener('load', init, {once: true});

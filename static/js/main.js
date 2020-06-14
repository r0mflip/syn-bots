import {html, render, Component} from '/static/js/third_party/htm-preact.js';

/**
 * Results class
 *
 * @param {Object} {hndle, results}
 */
const Results = ({hndle, results = {}}) => {
  if (!results) {
    return html``;
  }

  results.user.hndle = results.user.hndle.startsWith('@') ? results.user.hndle.slice(1) : results.user.hndle;

  if (results.error) {
    return html`<p><b>Error:</b> ${results.code == 50 ? `User ${results.hndle} not found.` : results.reason}</p>`;
  }

  const preds = results.predictions;
  const user = results.user;

  if (!preds) {
    return html``;
  }

  const isbotlike = preds.rfc[1] == 1;

  return html`
    <div class="results">
      <div class="results__user">
        <img src=${user.profile_image_url.replace('_normal.', '_400x400.')} />
        <p>${user.name}</p>
        <p>@${user.hndle}${user.verified ? ' ✔️' : ''}${user.self_bot ? ' - bot' : ''}</p>
      </div>
      <!-- <p class="results__status bot--${isbotlike}">
      ${
        isbotlike
          ? html`<b>@${hndle}</b> seems to exhibit bot like behavior`
          : html`<b>@${hndle}</b> looks clean of bot like behavior`
      }
      </p> -->

      <div class="results__progress">
        <p>Bot meter: ${preds.proba}%</p>
        <div>
          <span style="width: ${preds.proba}%"></span>
        </div>
      </div>

      <details>
        <summary>More info</summary>
        <table>
          <tr><th>Model</th><th>Original</th><th>Scaled</th></tr>
          <tr><td>SVC</td><td>${preds['svc'][0]}</td><td>${preds['svc'][1]}</td></tr>
          <tr><td>Gaussian NB</td><td>${preds['gnb'][0]}</td><td>${preds['gnb'][1]}</td></tr>
          <tr><td>Decission Tree</td><td>${preds['dtc'][0]}</td><td>${preds['dtc'][1]}</td></tr>
          <tr><td>Random Forest</td><td>${preds['rfc'][0]}</td><td>${preds['rfc'][1]}</td></tr>
        </table>
        <p>Get more account info on <a href="https://foller.me/?name=${results.user.hndle}" target="_blank">foller.me/${results.user.hndle}</a></p>
      </details>
    </div>
  `;
}


/**
 * Main app component
 *
 * @class App
 * @extends {Component}
 */
class App extends Component {
  constructor(...args) {
    super(...args);
    this.onValueChange = this.onValueChange.bind(this);
  }

  async getPrediction() {
    const {hndle} = this.state;

    if (!hndle) {
      return;
    }

    this.setState({hndle, results: undefined});

    try {
      const results = await (await fetch(`/predict/${hndle}`)).json();
      console.log(results);
      this.setState({hndle, results});
    } catch (e) {
      console.error(e);
      this.setState({hndle, results: {error: true, reason: 'Server error or handle not found'}});
    }
  }

  onValueChange(e) {
    const state = this.state;
    const hndle = e.target.value;

    this.setState({hndle: hndle, results: state.results});
  }

  render({}, {hndle, results}) {
    return html`
      <div class="main__container">
        <h1>SYN</h1>
        <p>Bot activity predition using Machine Learning for Twitter</p>

        <label>
          <span>Twitter handle</span>
          <input type="text" value=${hndle} onChange=${this.onValueChange} pattern="[a-zA-Z0-9_]+" />
        </label>

        <button onClick=${_ => this.getPrediction()}>Check</button>

        ${results ? html`<${Results} hndle=${hndle} results=${results} />` : ''}
      </div>
    `;
  }
}


/**
 * Setup function
 */
const init = _ => {
  render(html`
    <${App} />
  `, document.querySelector('main'));
};

window.addEventListener('load', init, {once: true});

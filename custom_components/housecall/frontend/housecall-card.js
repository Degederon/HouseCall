/* HouseCall card — glass-style feed + composer for Home Assistant. */
(() => {
  const VERSION = "0.1.1";

  const PRIO = {
    info: { label: "Info", color: "#5EE6FF", tint: "rgba(94,230,255,0.14)", glow: "rgba(94,230,255,0.45)" },
    normal: { label: "Normal", color: "#FFB547", tint: "rgba(255,181,71,0.14)", glow: "rgba(255,181,71,0.45)" },
    critical: { label: "Critical", color: "#FF6B6B", tint: "rgba(255,107,107,0.16)", glow: "rgba(255,107,107,0.5)" },
  };

  const STATUS = {
    sent: "",
    held: "Waiting for quiet hours to end",
    waiting: "Waiting for someone to answer",
    acknowledged: "Handled",
    unanswered: "Nobody answered",
  };

  const VIA = { phone: "Phones", board: "Board", speaker: "Speaker" };

  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const fmtTime = (iso) => {
    try {
      const d = new Date(iso);
      const today = new Date();
      const t = d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
      if (d.toDateString() === today.toDateString()) return t;
      return d.toLocaleDateString([], { month: "short", day: "numeric" }) + ", " + t;
    } catch (e) {
      return "";
    }
  };

  const fmtClock = (hhmm) => {
    const [h, m] = String(hhmm || "0:0").split(":").map(Number);
    const ap = h >= 12 ? "PM" : "AM";
    const h12 = h % 12 || 12;
    return m ? `${h12}:${String(m).padStart(2, "0")} ${ap}` : `${h12} ${ap}`;
  };

  const ICON = {
    bell: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>',
    moon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
    send: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>',
    check: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
  };

  const CSS = `
    :host { display:block; --hc-text:#EEF2FF; --hc-muted:#A9B4D0; }
    ha-card { display:block; }
    * { box-sizing:border-box; }
    svg { width:100%; height:100%; fill:none; stroke:currentColor; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }
    .card {
      container-type:inline-size; position:relative; overflow:hidden;
      border-radius:var(--ha-card-border-radius, 24px); padding:20px; color:var(--hc-text);
      font-family: Inter, var(--ha-card-header-font-family, system-ui), sans-serif;
      background-color: rgba(8,12,26,0.72);
      background-image:
        radial-gradient(520px 360px at 8% 0%, rgba(94,230,255,0.18), transparent 70%),
        radial-gradient(520px 380px at 100% 10%, rgba(167,120,255,0.20), transparent 70%);
      border:1px solid rgba(255,255,255,0.13);
      backdrop-filter: blur(22px); -webkit-backdrop-filter: blur(22px);
      box-shadow: 0 20px 60px rgba(0,0,0,0.30);
    }
    header { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px; margin-bottom:16px; }
    .brand { display:flex; align-items:center; gap:12px; }
    .logo { width:42px; height:42px; border-radius:14px; display:flex; align-items:center; justify-content:center; color:#7FE3FF;
      background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.16); box-shadow:0 0 26px rgba(94,230,255,0.25); }
    .logo span { width:22px; height:22px; display:block; }
    h2 { margin:0; font-size:20px; font-weight:700; letter-spacing:-0.01em; }
    .sub { font-size:12px; color:var(--hc-muted); }
    .pills { display:flex; flex-wrap:wrap; gap:8px; }
    .pill { display:inline-flex; align-items:center; gap:7px; padding:7px 12px; border-radius:999px; font-size:12px;
      background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.14); }
    .pill .i { width:13px; height:13px; color:#C9B2FF; display:block; }
    .pill.alert { color:#FF8A8A; background:rgba(255,107,107,0.14); border-color:rgba(255,107,107,0.45); font-weight:700; }
    .people { display:flex; flex-wrap:wrap; gap:14px; margin-bottom:16px; }
    .person { display:flex; align-items:center; gap:9px; font-size:13px; }
    .av { position:relative; width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center;
      font-weight:700; color:#0A0F1F; }
    .av i { position:absolute; right:-1px; bottom:-1px; width:11px; height:11px; border-radius:50%; border:2px solid #11162A; }
    .person small { display:block; color:var(--hc-muted); font-size:11px; }
    .grid { display:grid; grid-template-columns: 1fr; gap:16px; }
    @container (min-width: 720px) { .grid { grid-template-columns: minmax(0,1fr) 320px; } }
    .panel { padding:16px; border-radius:20px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.11); }
    .label { font-size:11px; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; color:var(--hc-muted); margin:0 0 10px; }
    .feed { display:flex; flex-direction:column; gap:9px; max-height: var(--hc-feed-height, 420px); overflow-y:auto; padding-right:2px; }
    .item { display:flex; gap:12px; padding:12px 14px; border-radius:15px; background:rgba(255,255,255,0.045); border:1px solid rgba(255,255,255,0.08); }
    .item.waiting { border-color:rgba(255,107,107,0.55); box-shadow:0 0 24px rgba(255,107,107,0.18); }
    .dot { flex:none; width:10px; height:10px; border-radius:50%; margin-top:6px; }
    .body { flex:1; min-width:0; }
    .top { display:flex; justify-content:space-between; gap:10px; align-items:baseline; }
    .msg { font-weight:600; font-size:14px; line-height:1.35; word-break:break-word; }
    .time { flex:none; font-size:11px; color:var(--hc-muted); }
    .meta { display:flex; flex-wrap:wrap; gap:8px; margin-top:6px; align-items:center; font-size:12px; color:var(--hc-muted); }
    .chip { padding:2px 9px; border-radius:999px; font-weight:700; font-size:11px; }
    .ok { display:inline-flex; align-items:center; gap:4px; color:#7CF0B5; font-weight:600; }
    .ok span { width:12px; height:12px; display:block; }
    .warn { color:#FFB0B0; font-weight:600; }
    .ack { margin-top:10px; min-height:40px; padding:0 16px; border-radius:12px; border:none; cursor:pointer;
      font:700 13px Inter, system-ui, sans-serif; color:#1A0508; background:#FF6B6B; box-shadow:0 8px 22px rgba(255,107,107,0.4); }
    .empty { padding:26px 10px; text-align:center; color:var(--hc-muted); font-size:13px; }
    .composer { display:flex; flex-direction:column; gap:14px; }
    input.text { width:100%; height:46px; padding:0 14px; border-radius:13px; border:1px solid rgba(255,255,255,0.18);
      background:rgba(8,12,26,0.6); color:var(--hc-text); font:500 14px Inter, system-ui, sans-serif; outline:none; }
    input.text:focus { border-color:#7FE3FF; box-shadow:0 0 0 3px rgba(127,227,255,0.2); }
    input.text::placeholder { color:#8792AE; }
    .chips { display:flex; flex-wrap:wrap; gap:7px; }
    .who { min-height:40px; padding:0 14px; border-radius:999px; cursor:pointer; font:600 13px Inter, system-ui, sans-serif;
      color:var(--hc-text); background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.18); }
    .who[aria-pressed="true"] { color:#08101F; background:#EEF2FF; border-color:#EEF2FF; }
    .seg { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:5px; padding:4px; border-radius:15px;
      background:rgba(8,12,26,0.5); border:1px solid rgba(255,255,255,0.10); }
    .seg button { min-height:40px; border-radius:11px; border:1px solid transparent; cursor:pointer; background:transparent;
      font:700 13px Inter, system-ui, sans-serif; }
    .route { padding:12px 14px; border-radius:14px; border:1px dashed rgba(255,255,255,0.2); background:rgba(8,12,26,0.4);
      font-size:13px; line-height:1.45; }
    .send { min-height:50px; border-radius:15px; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:9px;
      font:700 15px Inter, system-ui, sans-serif; color:#08101F; transition:transform .1s ease; }
    .send:active { transform:scale(0.98); }
    .send span { width:17px; height:17px; display:block; }
    .send[disabled] { opacity:.6; cursor:default; }
    .toast { font-size:12px; color:#7CF0B5; min-height:16px; }
    .err { padding:16px; color:#FFB0B0; }
    button:focus-visible { outline:2px solid #7FE3FF; outline-offset:2px; }
  `;

  const AVATARS = [
    "linear-gradient(135deg,#7FE3FF,#B49BFF)",
    "linear-gradient(135deg,#FFD08A,#FF8E8E)",
    "linear-gradient(135deg,#9BF5C9,#7FE3FF)",
    "linear-gradient(135deg,#C9B2FF,#FF9ED8)",
    "linear-gradient(135deg,#FFE38A,#9BF5C9)",
  ];

  class HouseCallCard extends HTMLElement {
    static getStubConfig() {
      return { entity: "sensor.housecall" };
    }

    setConfig(config) {
      this._config = {
        entity: "sensor.housecall",
        title: "HouseCall",
        show_composer: true,
        max_items: 20,
        ...(config || {}),
      };
      this._who = this._who || new Set(["everyone"]);
      this._prio = this._prio || "normal";
      this._built = false;
      this._lastState = null;
      if (this._hass) this._render();
    }

    set hass(hass) {
      this._hass = hass;
      const st = hass.states[this._config.entity];
      if (!this._built) this._build();
      if (st !== this._lastState) {
        this._lastState = st;
        this._update(st);
      }
    }

    getCardSize() {
      return 8;
    }

    getGridOptions() {
      return { columns: 12, min_columns: 6, rows: "auto" };
    }

    _render() {
      this._built = false;
      this._lastState = null;
      this.hass = this._hass;
    }

    _build() {
      if (!this.shadowRoot) this.attachShadow({ mode: "open" });
      const c = this._config;
      this.shadowRoot.innerHTML = `
        <style>${CSS}</style>
        <ha-card class="card">
          <header>
            <div class="brand">
              <div class="logo"><span>${ICON.bell}</span></div>
              <div><h2>${esc(c.title)}</h2><div class="sub">Every alert in the house, in one place</div></div>
            </div>
            <div class="pills" id="pills"></div>
          </header>
          <div class="people" id="people"></div>
          <div class="grid">
            <section class="panel">
              <p class="label">Messages</p>
              <div class="feed" id="feed"></div>
            </section>
            ${c.show_composer ? `
            <section class="panel composer">
              <div>
                <label class="label" for="msg">Message</label>
                <input id="msg" class="text" type="text" placeholder="Dinner's ready!" autocomplete="off">
              </div>
              <div><p class="label">Who</p><div class="chips" id="who"></div></div>
              <div><p class="label">How urgent</p><div class="seg" id="prio"></div></div>
              <div class="route" id="route"></div>
              <button class="send" id="send" type="button"><span>${ICON.send}</span>Send now</button>
              <div class="toast" id="toast" role="status"></div>
            </section>` : ""}
          </div>
        </ha-card>`;
      this._built = true;
      const $ = (id) => this.shadowRoot.getElementById(id);
      this.$ = $;
      if (c.show_composer) {
        $("send").addEventListener("click", () => this._send());
        $("msg").addEventListener("keydown", (e) => {
          if (e.key === "Enter") this._send();
        });
        this._renderPrio();
      }
      this.shadowRoot.addEventListener("click", (e) => {
        const ack = e.target.closest("[data-ack]");
        if (ack) this._ack(ack.dataset.ack);
        const who = e.target.closest("[data-who]");
        if (who) this._toggleWho(who.dataset.who);
        const p = e.target.closest("[data-prio]");
        if (p) {
          this._prio = p.dataset.prio;
          this._renderPrio();
        }
      });
    }

    _people() {
      const st = this._lastState;
      return (st && st.attributes.people) || [];
    }

    _update(st) {
      const $ = this.$;
      if (!st) {
        $("feed").innerHTML = `<div class="err">Can't find <b>${esc(this._config.entity)}</b>. Is HouseCall set up?</div>`;
        return;
      }
      const a = st.attributes;
      const hist = (a.history || []).slice(0, this._config.max_items);
      const waiting = Number(st.state) || 0;
      const q = a.quiet_hours || {};
      const today = new Date().toDateString();
      const sentToday = (a.history || []).filter((h) => new Date(h.time).toDateString() === today).length;

      $("pills").innerHTML = `
        ${waiting ? `<span class="pill alert">${waiting} waiting for an answer</span>` : ""}
        <span class="pill"><span><b>${sentToday}</b> today</span></span>
        <span class="pill"><span class="i">${ICON.moon}</span>${q.active ? "Quiet hours on" : `Quiet ${fmtClock(q.start)} – ${fmtClock(q.end)}`}</span>`;

      $("people").innerHTML = (a.people || [])
        .map(
          (p, i) => `
          <div class="person">
            <div class="av" style="background:${AVATARS[i % AVATARS.length]}">${esc((p.name || "?").charAt(0).toUpperCase())}
              <i style="background:${p.home ? "#7CF0B5" : "#8792AE"}"></i></div>
            <div>${esc(p.name)}<small>${p.home ? "Home" : "Away"} · ${p.phones} phone${p.phones === 1 ? "" : "s"}</small></div>
          </div>`
        )
        .join("");

      $("feed").innerHTML = hist.length
        ? hist.map((h) => this._itemHtml(h)).join("")
        : `<div class="empty">No messages yet. Send one to try it out.</div>`;

      if (this._config.show_composer) {
        this._renderWho();
        this._renderRoute();
      }
    }

    _itemHtml(h) {
      const p = PRIO[h.priority] || PRIO.normal;
      const via = (h.via || []).map((v) => VIA[v] || v).join(", ");
      let status = "";
      if (h.status === "acknowledged") {
        status = `<span class="ok"><span>${ICON.check}</span>Handled by ${esc(h.acked_by || "someone")}</span>`;
      } else if (h.status === "held" || h.status === "unanswered") {
        status = `<span class="warn">${STATUS[h.status]}</span>`;
      } else if (h.status === "waiting") {
        status = `<span class="warn">${STATUS.waiting}${h.repeats ? ` · repeated ${h.repeats}×` : ""}</span>`;
      }
      return `
        <article class="item ${h.status === "waiting" ? "waiting" : ""}">
          <span class="dot" style="background:${p.color};box-shadow:0 0 12px ${p.color}"></span>
          <div class="body">
            <div class="top"><div class="msg">${esc(h.title ? h.title + ": " : "")}${esc(h.message)}</div>
              <div class="time">${fmtTime(h.time)}</div></div>
            <div class="meta">
              <span class="chip" style="color:${p.color};background:${p.tint}">${p.label}</span>
              <span>To ${esc(h.to_label)}${via ? " · " + esc(via) : ""}</span>
              ${status}
            </div>
            ${h.status === "waiting" ? `<button class="ack" type="button" data-ack="${esc(h.id)}">I'm on it</button>` : ""}
          </div>
        </article>`;
    }

    _renderWho() {
      const people = this._people();
      const chips = [{ id: "everyone", name: "Everyone" }, ...people];
      this.$("who").innerHTML = chips
        .map(
          (c) =>
            `<button class="who" type="button" data-who="${esc(c.id)}" aria-pressed="${this._who.has(c.id)}">${esc(c.name)}</button>`
        )
        .join("");
    }

    _toggleWho(id) {
      if (id === "everyone") {
        this._who = new Set(["everyone"]);
      } else {
        this._who.delete("everyone");
        this._who.has(id) ? this._who.delete(id) : this._who.add(id);
        if (!this._who.size) this._who.add("everyone");
      }
      this._renderWho();
      this._renderRoute();
    }

    _renderPrio() {
      this.$("prio").innerHTML = Object.entries(PRIO)
        .map(([k, p]) => {
          const on = this._prio === k;
          return `<button type="button" data-prio="${k}" aria-pressed="${on}" style="color:${on ? "#08101F" : p.color};background:${
            on ? p.color : "transparent"
          };box-shadow:${on ? "0 0 20px " + p.glow : "none"}">${p.label}</button>`;
        })
        .join("");
      const p = PRIO[this._prio];
      const send = this.$("send");
      send.style.background = p.color;
      send.style.boxShadow = `0 10px 28px ${p.glow}`;
      this._renderRoute();
    }

    _whoLabel() {
      if (this._who.has("everyone")) return "everyone";
      const names = this._people().filter((p) => this._who.has(p.id)).map((p) => p.name);
      return names.join(", ") || "everyone";
    }

    _renderRoute() {
      const st = this._lastState;
      const a = (st && st.attributes) || {};
      const quiet = a.quiet_hours && a.quiet_hours.active;
      const speaker = a.outputs && a.outputs.speaker;
      const who = this._whoLabel();
      const text = {
        info: "Shows here on the board only. Nobody's phone will buzz.",
        normal: quiet
          ? `Quiet hours are on, so it shows here now and goes to ${esc(who)}'s phone in the morning.`
          : `Phone notification for ${esc(who)}, and it shows here.`,
        critical: `<b>Loud</b> on ${esc(who)}'s phone, even in quiet hours${speaker ? ", read aloud on the speakers" : ""}. Repeats until someone taps "I'm on it".`,
      }[this._prio];
      this.$("route").innerHTML = `<p class="label" style="margin-bottom:4px">Where it will go</p>${text}`;
    }

    async _send() {
      const input = this.$("msg");
      const message = input.value.trim();
      if (!message) {
        input.focus();
        return;
      }
      const btn = this.$("send");
      btn.disabled = true;
      const data = { message, priority: this._prio };
      if (!this._who.has("everyone")) data.to = [...this._who];
      try {
        await this._hass.callService("housecall", "send", data);
        input.value = "";
        this._toast("Sent");
      } catch (e) {
        this._toast("Couldn't send: " + (e.message || e), true);
      } finally {
        btn.disabled = false;
      }
    }

    async _ack(id) {
      const me = this._hass.user && this._hass.user.name;
      try {
        await this._hass.callService("housecall", "acknowledge", me ? { id, by: me } : { id });
      } catch (e) {
        this._toast("Couldn't update: " + (e.message || e), true);
      }
    }

    _toast(text, bad) {
      const t = this.$("toast");
      if (!t) return;
      t.style.color = bad ? "#FFB0B0" : "#7CF0B5";
      t.textContent = text;
      clearTimeout(this._tt);
      this._tt = setTimeout(() => (t.textContent = ""), 3000);
    }
  }

  if (!customElements.get("housecall-card")) {
    customElements.define("housecall-card", HouseCallCard);
    window.customCards = window.customCards || [];
    window.customCards.push({
      type: "housecall-card",
      name: "HouseCall",
      description: "Glass-style message feed and composer for HouseCall.",
      preview: true,
    });
    console.info(`%c HOUSECALL-CARD %c ${VERSION} `, "background:#5EE6FF;color:#08101F;font-weight:700", "");
  }
})();

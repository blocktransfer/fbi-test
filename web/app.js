"use strict";

const byId = (id) => document.getElementById(id);
const storageKey = "bt-fbi-test-admin";
let token = "";
let gatewayReady = false;
let sending = false;

function loadToken() {
  if (location.hash.startsWith("#token=")) {
    token = decodeURIComponent(location.hash.slice(7));
    try { sessionStorage.setItem(storageKey, token); } catch (_) {}
    history.replaceState(null, "", location.pathname);
  } else {
    try { token = sessionStorage.getItem(storageKey) || ""; } catch (_) {}
  }
  byId("auth-notice").hidden = Boolean(token);
  byId("use-notice").hidden = !token;
}

async function api(path, method = "GET", payload) {
  if (!token) throw Error("Open the admin URL printed in your terminal.");
  const options = { method, credentials: "omit", cache: "no-store", headers: { "X-Admin-Token": token } };
  if (payload !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(payload);
  }
  let response;
  try { response = await fetch(path, options); }
  catch (_) { throw Error("Cannot reach local admin server."); }
  let result;
  try { result = await response.json(); }
  catch (_) { throw Error("Unexpected server response."); }
  if (!response.ok) throw Error(result.error || "Request failed.");
  return result;
}

function sendButtonState() {
  byId("send").disabled = sending || !gatewayReady || !token || !byId("confirmed").checked || !byId("authorization").value.trim();
  byId("send").textContent = sending ? "Sending once…" : "Send synthetic gateway test ↗";
}

function feedback(id, message, status) {
  const node = byId(id);
  node.textContent = message;
  node.className = "feedback" + (id === "send-feedback" ? " center" : "") + (status ? " " + status : "");
}

function showStatus(s) {
  gatewayReady = Boolean(s.gateway_configured);
  byId("gateway-metric").textContent = gatewayReady ? "Configured" : "Not configured";
  byId("gateway-caption").textContent = gatewayReady ? "Agency test gateway only" : "No approved gateway settings";
  byId("attempts-metric").textContent = String(s.attempts);
  byId("receipts-metric").textContent = String(s.accepted_http);
  byId("gateway-pill").textContent = gatewayReady ? "TEST READY" : "NOT SET UP";
  byId("gateway-pill").className = "pill " + (gatewayReady ? "ok" : "warn");
  byId("config-dot").className = "dot " + (gatewayReady ? "" : "grey");
  byId("gateway-host").textContent = gatewayReady ? "Configured test host: " + s.gateway_host : "No approved gateway configured.";
  if (!sending) feedback("send-feedback", gatewayReady ? "HTTP response is not FBI acceptance." : "Gateway transmission unavailable until configured.");
  sendButtonState();
}

function cell(row, value) {
  const node = document.createElement("td");
  node.textContent = value;
  row.appendChild(node);
  return node;
}
function showActivity(events) {
  const body = byId("activity-body");
  body.replaceChildren();
  byId("activity-count").textContent = events.length + " event" + (events.length === 1 ? "" : "s");
  if (!events.length) {
    const row = document.createElement("tr");
    const td = cell(row, "");
    td.colSpan = 4;
    td.className = "empty";
    for (const [tag, content] of [["span", "◷"], ["strong", "No submissions yet"], ["small", "Test gateway events will appear here."]]) {
      const item = document.createElement(tag);
      item.textContent = content;
      td.append(item);
    }
    body.append(row);
    return;
  }
  for (const event of events) {
    const row = document.createElement("tr");
    const time = new Date(event.timestamp_utc);
    cell(row, Number.isNaN(time.getTime()) ? "—" : time.toLocaleTimeString("en-US", { hour12: false, timeZone: "UTC" }));
    const id = cell(row, "");
    const code = document.createElement("code");
    code.textContent = event.submission_id;
    id.append(code);
    cell(row, "Synthetic test");
    const result = cell(row, "");
    const pill = document.createElement("span");
    const ok = event.outcome === "http_2xx_not_fbi_acceptance";
    pill.className = "result" + (ok ? "" : " unknown");
    pill.textContent = ok ? "HTTP " + event.http_status + " · Not FBI acceptance" : event.outcome === "unknown_delivery_do_not_retry" ? "Uncertain · do not retry" : "Rejected / unconfirmed";
    result.append(pill);
    body.append(row);
  }
}
async function refresh() {
  if (!token) return;
  byId("refresh").disabled = true;
  try {
    const [status, log] = await Promise.all([api("/api/status"), api("/api/activity")]);
    showStatus(status);
    showActivity(log.events);
    byId("auth-notice").hidden = true;
  } catch (error) {
    byId("auth-notice").hidden = false;
    byId("auth-message").textContent = error.message;
    if (error.message.includes("restart the local server")) {
      token = "";
      try { sessionStorage.removeItem(storageKey); } catch (_) {}
    }
    gatewayReady = false;
    sendButtonState();
  } finally { byId("refresh").disabled = false; }
}
async function preview() {
  byId("preview").disabled = true;
  try {
    const data = await api("/api/preview", "POST", { padding: Number(byId("padding").value) });
    feedback("preview-feedback", "✓ Validated " + data.bytes.toLocaleString() + " bytes locally; no network transmission.", "success");
  } catch (error) { feedback("preview-feedback", error.message, "error"); }
  finally { byId("preview").disabled = false; }
}
async function sendTest() {
  if (sending || !gatewayReady || !byId("confirmed").checked) return;
  sending = true;
  sendButtonState();
  feedback("send-feedback", "Sending one synthetic sample. Do not retry while delivery is uncertain.");
  try {
    const receipt = await api("/api/send", "POST", {
      padding: Number(byId("padding").value),
      authorization_ref: byId("authorization").value.trim(),
      request_id: crypto.randomUUID(),
      confirmed: true
    });
    feedback("send-feedback", "HTTP " + receipt.http_status + " · Test ID " + receipt.submission_id + ". Not FBI acceptance.", "success");
  } catch (error) {
    feedback("send-feedback", error.message + " Do not retry until prior delivery is reconciled.", "error");
  } finally {
    const note = byId("send-feedback").textContent;
    const outcome = byId("send-feedback").classList.contains("success") ? "success" : "error";
    byId("confirmed").checked = false;
    sending = false;
    await refresh();
    feedback("send-feedback", note, outcome);
    sendButtonState();
  }
}

async function acknowledgeUse() {
  byId("acknowledge-use").disabled = true;
  try {
    if (!byId("accept-use").checked) throw Error("Acknowledgment required.");
    await api("/api/session", "POST", { acknowledge: true });
    byId("use-notice").hidden = true;
    await refresh();
  } catch (error) {
    feedback("ack-feedback", error.message, "error");
    byId("acknowledge-use").disabled = false;
  }
}
async function logout() {
  try { if (token) await api("/api/logout", "POST", {}); } catch (_) {}
  token = "";
  try { sessionStorage.removeItem(storageKey); } catch (_) {}
  byId("use-notice").hidden = true;
  byId("auth-notice").hidden = false;
  byId("auth-message").textContent = "Session ended. Restart the local server to obtain a new admin URL.";
  gatewayReady = false;
  sendButtonState();
}

byId("local-date").textContent = new Date().toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }).toUpperCase();
byId("refresh").addEventListener("click", refresh);
byId("logout").addEventListener("click", logout);
byId("accept-use").addEventListener("change", () => {
  byId("acknowledge-use").disabled = !byId("accept-use").checked;
});
byId("acknowledge-use").addEventListener("click", acknowledgeUse);
byId("preview").addEventListener("click", preview);
byId("send").addEventListener("click", sendTest);
byId("confirmed").addEventListener("change", sendButtonState);
byId("authorization").addEventListener("input", sendButtonState);
for (const nav of document.querySelectorAll(".sidebar nav a")) {
  nav.addEventListener("click", () => {
    for (const a of document.querySelectorAll(".sidebar nav a")) a.classList.remove("selected");
    nav.classList.add("selected");
  });
}
loadToken();
if (!token) sendButtonState();

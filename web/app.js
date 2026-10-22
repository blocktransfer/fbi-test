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
function showReadiness(register) {
  const root = byId("policy-controls");
  root.replaceChildren();
  byId("register-summary").textContent = String(register.control_count) + " mapped requirements · no production approval verified";
  for (const control of register.controls) {
    const item = document.createElement("details");
    item.className = "register-item";
    const summary = document.createElement("summary");
    summary.textContent = control.framework + " " + control.section + " · " + control.responsible_party;
    const text = document.createElement("p");
    text.textContent = control.requirement;
    const citation = document.createElement("small");
    citation.textContent = "Source page(s): " + control.pages + " · " +
      (control.state === "prototype_only" ? "Prototype control only — not verified" : "Unverified / external requirement");
    item.append(summary, text, citation);
    root.append(item);
  }
}

let sectionOneCatalog = null;

function renderDefinitions() {
  const root = byId("definition-list");
  root.replaceChildren();
  if (!sectionOneCatalog) return;
  const query = byId("definition-query").value.toLowerCase().trim();
  const matches = sectionOneCatalog.entries.filter((entry) =>
    [entry.section, entry.term, entry.summary].some((v) => v.toLowerCase().includes(query))
  );
  byId("definition-count").textContent = matches.length + " / " + sectionOneCatalog.total + " terms";
  if (!matches.length) {
    const msg = document.createElement("p");
    msg.className = "hint";
    msg.textContent = "No matching definitions.";
    root.append(msg);
    return;
  }
  for (const entry of matches) {
    const card = document.createElement("details");
    card.className = "definition-card";
    const head = document.createElement("summary");
    const section = document.createElement("span");
    section.className = "section-tag";
    section.textContent = entry.section;
    const term = document.createElement("strong");
    term.textContent = entry.term;
    head.append(section, term);
    const desc = document.createElement("p");
    desc.textContent = entry.summary;
    const source = document.createElement("small");
    source.textContent = "Outsourcing Standard · PDF p. " + entry.pdf_pages + " · " +
      (entry.implementation === "external" ? "External requirement" : "Definition-based guardrail");
    card.append(head, desc, source);
    root.append(card);
  }
}

function showSectionOneResult(result) {
  const root = byId("section-one-output");
  root.replaceChildren();
  const flags = [
    ["CHRI indicated", result.classification.chri_indicated ? "Yes, based on category flags" : "No, based on category flags"],
    ["PII indicated", result.classification.pii_indicated ? "Yes, based on category flags" : "No, based on category flags"],
    ["Positive identification established", "No · requires a reliable external comparison"],
    ["Production use authorized", "No · FBI/agency approval unverified"]
  ];
  for (const [label, value] of flags) {
    const line = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = label + ": ";
    line.append(strong, document.createTextNode(value));
    root.append(line);
  }
  const note = document.createElement("p");
  note.textContent = result.identity.note;
  root.append(note);
  const title = document.createElement("h4");
  title.textContent = "Role and authority findings (unverified)";
  root.append(title);
  for (const f of result.findings) {
    const item = document.createElement("p");
    item.className = f.state === "blocked_by_reported_facts" ? "scenario-issue" : "scenario-note";
    item.textContent = "§" + f.section + ": " + f.explanation;
    root.append(item);
  }
}

async function runSectionOneAssessment(event) {
  event.preventDefault();
  const button = byId("section-one-run");
  button.disabled = true;
  const form = byId("section-one-form");
  const body = {};
  for (const field of form.elements) {
    if (!field.name) continue;
    body[field.name] = field.type === "checkbox" ? field.checked : field.value;
  }
  try {
    const result = await api("/api/section-one/assess", "POST", body);
    showSectionOneResult(result);
  } catch (error) {
    byId("section-one-output").textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

let recipientTemplates = [];
function showRecipientTemplates(data) {
  recipientTemplates = data.templates;
  const select = byId("recipient-template-select");
  const selected = select.value;
  select.replaceChildren();
  const intro = document.createElement("option");
  intro.value = "";
  intro.textContent = "Select a template…";
  select.append(intro);
  for (const item of recipientTemplates) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.title + " · §§" + item.sections.join(", ");
    select.append(option);
  }
  select.value = recipientTemplates.some(t => t.id === selected) ? selected : "";
  changeRecipientTemplate();
}
function changeRecipientTemplate() {
  const found = recipientTemplates.find(t => t.id === byId("recipient-template-select").value);
  byId("recipient-template-text").value = found ? found.body : "";
  byId("recipient-copy-template").disabled = !found;
  byId("recipient-template-note").textContent = found
    ? found.required_review + " This is a blank draft; no delivery has occurred."
    : "Select a document; copies are not sent or stored.";
}
async function copyRecipientTemplate() {
  const text = byId("recipient-template-text").value;
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    byId("recipient-template-note").textContent =
      "Blank text copied. Complete and transmit only using your approved organizational channel.";
  } catch (_) {
    byId("recipient-template-note").textContent =
      "Clipboard permission unavailable. Select the template text to copy manually.";
  }
}
let channelerTemplateCatalog = [];
function showChannelerTemplates(data) {
  channelerTemplateCatalog = data.templates;
  const select = byId("channeler-template-select");
  const oldValue = select.value;
  select.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select a template…";
  select.append(placeholder);
  for (const record of data.templates) {
    const option = document.createElement("option");
    option.value = record.id;
    option.textContent = record.title + " · " + record.sections.join(", ");
    select.append(option);
  }
  select.value = data.templates.some(x => x.id === oldValue) ? oldValue : "";
  chooseChannelerTemplate();
}
function chooseChannelerTemplate() {
  const record = channelerTemplateCatalog.find(x => x.id === byId("channeler-template-select").value);
  byId("channeler-template-text").value = record ? record.body : "";
  byId("channeler-copy-template").disabled = !record;
  byId("channeler-template-feedback").textContent = record ?
    "Blank template only. No documents have been prepared or delivered." :
    "Only the unpopulated template text is copied.";
}
async function copyChannelerTemplate() {
  const body = byId("channeler-template-text").value;
  if (!body) return;
  try {
    await navigator.clipboard.writeText(body);
    byId("channeler-template-feedback").textContent =
      "Blank form copied. Complete using approved organizational records and communication channels.";
  } catch (_) {
    byId("channeler-template-feedback").textContent =
      "Clipboard access unavailable; select and copy the template text manually.";
  }
}
function channelerTime(value) {
  return value ? new Date(value).toISOString() : null;
}
function channelerDisplay(value) {
  return value ? new Date(value).toLocaleString() : "No specific numerical deadline provided";
}
function channelerResult(id, fields) {
  const target = byId(id);
  target.replaceChildren();
  for (const [label, value] of fields) {
    const line = document.createElement("p");
    const key = document.createElement("strong");
    key.textContent = label + ": ";
    line.append(key, document.createTextNode(String(value)));
    target.append(line);
  }
  const note = document.createElement("p");
  note.textContent = "Calculation only. No real data processed and no outside action taken.";
  target.append(note);
}
function showChanneler(payload) {
  const {catalog, progress} = payload;
  byId("channeler-count").textContent =
    progress.reported_count + " / " + catalog.check_count + " reported · none verified";
  const root = byId("channeler-checks");
  root.replaceChildren();
  for (const clause of catalog.clauses) {
    const details = document.createElement("details");
    details.className = "recipient-group";
    const summary = document.createElement("summary");
    summary.textContent = "§" + clause.section + " · " + clause.category.replaceAll("_", " ");
    details.append(summary);
    const overview = document.createElement("p");
    overview.className = "channeler-clause-text";
    overview.textContent = clause.description + " · Printed p. " + clause.printed_page;
    details.append(overview);
    for (const check of catalog.checks.filter(c => c.section === clause.section)) {
      const entry = document.createElement("div");
      entry.className = "recipient-check";
      const label = document.createElement("label");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      const previous = progress.checks[check.id];
      checkbox.checked = Boolean(previous?.reported);
      label.append(checkbox, document.createTextNode(check.label));
      const citation = document.createElement("small");
      citation.textContent = "§" + check.section + " · operator-reported, not verified";
      const row = document.createElement("div");
      row.className = "recipient-entry";
      const evidence = document.createElement("input");
      evidence.type = "text";
      evidence.placeholder = "Nonidentifying document code, e.g. POLICY-2026-001";
      evidence.maxLength = 64;
      evidence.spellcheck = false;
      evidence.autocomplete = "off";
      evidence.value = previous?.evidence_ref || "";
      evidence.setAttribute("aria-label", "Reference for " + check.id);
      const save = document.createElement("button");
      save.className = "recipient-save";
      save.textContent = "Record";
      save.type = "button";
      const feedback = document.createElement("p");
      feedback.className = "recipient-note";
      feedback.setAttribute("aria-live", "polite");
      save.addEventListener("click", async () => {
        save.disabled = true;
        try {
          await api("/api/channeler/check", "POST", {
            id: check.id, reported: checkbox.checked,
            evidence_ref: checkbox.checked ? evidence.value.trim() : null
          });
          // Preserve section disclosure across refresh.
          const wasOpen = details.open;
          const latest = await api("/api/channeler");
          showChanneler(latest);
          const next = Array.from(root.children).find(
            node => node.querySelector("summary")?.textContent?.startsWith("§" + clause.section + " ·")
          );
          if (next) next.open = wasOpen;
        } catch (error) {
          feedback.textContent = error.message;
          save.disabled = false;
        }
      });
      row.append(evidence, save);
      entry.append(label, citation, row, feedback);
      details.append(entry);
    }
    root.append(details);
  }
}
async function runChannelerPlan(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const key = form.id.replace("channeler-", "").replace("-form", "");
  const outputs = {
    "deadline": "/api/channeler/deadlines", "retention": "/api/channeler/retention",
    "training": "/api/channeler/training", "rapback": "/api/channeler/rapback"
  };
  const resultIds = {
    "deadline": "channeler-deadline-result", "retention": "channeler-retention-result",
    "training": "channeler-training-result", "rapback": "channeler-rapback-result"
  };
  const kind = outputs[key] ? key : "deadline";
  const request = {};
  for (const field of form.elements) {
    if (!field.name) continue;
    if (field.type === "datetime-local") {
      if (field.value) request[field.name] = channelerTime(field.value);
    } else if (field.type === "checkbox") {
      request[field.name] = field.checked;
    } else {
      request[field.name] = field.value;
    }
  }
  if (kind === "retention" || kind === "training" || kind === "rapback")
    request.as_of = new Date().toISOString();
  if (kind === "rapback") request.purpose = "synthetic_only";
  try {
    const result = await api(outputs[kind], "POST", request);
    if (kind === "deadline") channelerResult(resultIds[kind], [
      ["Source", result.sections.join(", ")],
      ["Notice/milestone due", channelerDisplay(result.initial_due_utc)],
      ["Written security violation report due", result.written_report_due_utc
        ? channelerDisplay(result.written_report_due_utc) + " (from discovery)" : "Not specified for this event"],
      ["Recipients", result.recipients], ["Action", result.instruction],
      ["Notice sent", "No"]
    ]);
    if (kind === "retention") channelerResult(resultIds[kind], [
      ["Hypothetical destroy-by time", channelerDisplay(result.destroy_by_utc)],
      ["Overdue relative to now", result.overdue ? "Yes" : "No"],
      ["Actual CHRI deleted", "No — no CHRI enters the prototype"]
    ]);
    if (kind === "training") channelerResult(resultIds[kind], [
      ["Channeler training duty", result.channeler_training_duty_applies ? "Applicable" : "Reported retained by Recipient"],
      ["Preassignment training reported", result.preassignment_training_reported ? "Yes" : "No"],
      ["Next refresher", channelerDisplay(result.next_training_due_utc)],
      ["Next certification anniversary", channelerDisplay(result.next_fbi_certification_anniversary_utc)],
      ["FBI certification sent", "No"]
    ]);
    if (kind === "rapback") channelerResult(resultIds[kind], [
      ["Next annual message milestone", channelerDisplay(result.next_annual_validation_message_utc)],
      ["Who actually validates", result.validation_authority],
      ["FBI approval independently verified", "No"],
      ["Messages sent/subscriptions enabled", "No"]
    ]);
  } catch (error) {
    byId(resultIds[kind]).textContent = error.message;
  }
}
let recipientCatalog = null;

function receiptLine(parent, title, content) {
  const p = document.createElement("p");
  const b = document.createElement("strong");
  b.textContent = title + ": ";
  p.append(b, document.createTextNode(content));
  parent.append(p);
}

function showRecipient(data) {
  recipientCatalog = data.catalog;
  const reported = data.progress.checks;
  const list = byId("recipient-controls");
  list.replaceChildren();
  byId("recipient-count").textContent =
    data.progress.reported_count + " / " + data.catalog.control_count + " reported · 0 verified";
  for (const section of data.catalog.sections) {
    const group = document.createElement("details");
    group.className = "recipient-group";
    const title = document.createElement("summary");
    const matching = data.catalog.controls.filter(c => c.section === section);
    const number = matching.filter(c => reported[c.id] && reported[c.id].reported).length;
    title.textContent = "§" + section + " · " + number + "/" + matching.length + " reported";
    group.append(title);
    for (const control of matching) {
      const row = document.createElement("div");
      row.className = "recipient-check";
      const name = document.createElement("label");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = Boolean(reported[control.id] && reported[control.id].reported);
      name.append(checkbox, document.createTextNode(control.description));
      const foot = document.createElement("small");
      foot.textContent = "PDF p. " + control.pdf_page + (control.optional ? " · Optional right" : " · Duty") + " · Self-report only";
      const meta = document.createElement("div");
      meta.className = "recipient-entry";
      const evidence = document.createElement("input");
      evidence.type = "text";
      evidence.maxLength = 64;
      evidence.autocomplete = "off";
      evidence.spellcheck = false;
      evidence.placeholder = "Nonidentifying evidence code, e.g. DOC-2026-001";
      evidence.setAttribute("aria-label", "Evidence reference for " + control.id);
      evidence.value = reported[control.id]?.evidence_ref || "";
      const save = document.createElement("button");
      save.type = "button";
      save.textContent = "Record";
      save.className = "recipient-save";
      const note = document.createElement("p");
      note.className = "recipient-note";
      note.setAttribute("aria-live", "polite");
      save.addEventListener("click", async () => {
        save.disabled = true;
        try {
          await api("/api/recipient/check", "POST", {
            id: control.id,
            reported: checkbox.checked,
            evidence_ref: checkbox.checked ? evidence.value.trim() : null
          });
          const refreshed = await api("/api/recipient");
          showRecipient(refreshed);
        } catch (error) {
          note.textContent = error.message;
          note.className = "recipient-note error";
          save.disabled = false;
        }
      });
      meta.append(evidence, save);
      row.append(name, foot, meta, note);
      group.append(row);
    }
    list.append(group);
  }
}
function refreshRecipientFields() {
  const event = byId("recipient-event").value;
  const incident = event === "pii_breach" || event === "security_violation";
  byId("recipient-initial-notice").disabled = !incident;
  byId("recipient-renewal").disabled = event !== "policy_update_notice";
  if (!incident) byId("recipient-initial-notice").value = "";
  if (event !== "policy_update_notice") byId("recipient-renewal").value = "";
}
async function calculateRecipientDeadlines(event) {
  event.preventDefault();
  const output = byId("recipient-output");
  output.replaceChildren();
  const occurred = byId("recipient-occurred").value;
  if (!occurred) {
    output.textContent = "Enter a valid occurrence or discovery timestamp.";
    return;
  }
  const payload = {
    event: byId("recipient-event").value,
    occurred_at: new Date(occurred).toISOString()
  };
  const notice = byId("recipient-initial-notice").value;
  const renewal = byId("recipient-renewal").value;
  if (notice && !byId("recipient-initial-notice").disabled) payload.initial_notice_at = new Date(notice).toISOString();
  if (renewal && !byId("recipient-renewal").disabled) payload.renewal_at = new Date(renewal).toISOString();
  try {
    const plan = await api("/api/recipient/deadlines", "POST", payload);
    receiptLine(output, "Source", "§" + plan.section + " · PDF p. " + plan.pdf_page);
    receiptLine(output, "Notice / milestone due", plan.external_due_utc
      ? new Date(plan.external_due_utc).toLocaleString() : "Written notice required; no specified numeric deadline");
    if (plan.requires_initial_notice_time) receiptLine(output, "Written report", "Enter initial notice time to calculate five-day due date");
    else if (plan.written_report_due_utc) receiptLine(output, "Written report due", new Date(plan.written_report_due_utc).toLocaleString());
    receiptLine(output, "Recipients", plan.recipients);
    receiptLine(output, "Action", plan.instruction);
    receiptLine(output, "Dispatch status", "No notice or report sent by the application");
  } catch (error) {
    output.textContent = error.message;
  }
}

async function refresh() {
  if (!token) return;
  byId("refresh").disabled = true;
  try {
    const [status, log, register, sectionOne, recipient, templates, channeler, channelerForms] = await Promise.all([api("/api/status"), api("/api/activity"), api("/api/readiness"), api("/api/section-one"), api("/api/recipient"), api("/api/recipient/templates"), api("/api/channeler"), api("/api/channeler/templates")]);
    showStatus(status);
    showActivity(log.events);
    showReadiness(register);
    sectionOneCatalog = sectionOne;
    renderDefinitions();
    showRecipient(recipient);
    showRecipientTemplates(templates);
    showChanneler(channeler);
    showChannelerTemplates(channelerForms);
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

function localDateInput(value) {
  return new Date(value - new Date(value).getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}
function printDeadline(iso) {
  return iso ? new Date(iso).toLocaleString() : "Requires initial notification timestamp";
}
async function calculateIncident() {
  const target = byId("incident-results");
  target.replaceChildren();
  const discovered = byId("incident-discovered").value;
  if (!discovered) {
    target.textContent = "Enter the date and time the incident was discovered.";
    return;
  }
  const payload = {
    role: byId("incident-role").value,
    category: byId("incident-category").value,
    discovered_at: new Date(discovered).toISOString(),
  };
  const notice = byId("incident-notified").value;
  if (notice) payload.initial_notice_at = new Date(notice).toISOString();
  try {
    const data = await api("/api/incident-deadlines", "POST", payload);
    const items = [
      ["CJIS internal report (if incident)", printDeadline(data.internal_incident_report_due_utc)],
      ["External notification", printDeadline(data.external_notification_due_utc)],
      ["Written report", printDeadline(data.written_report_due_utc)],
      ["Notify", data.external_recipients],
      ["Authority", data.security_policy_reference + "; Outsourcing " + data.outsourcing_reference],
    ];
    for (const [name, value] of items) {
      const line = document.createElement("p");
      const title = document.createElement("strong");
      title.textContent = name + ": ";
      line.append(title, document.createTextNode(value));
      target.append(line);
    }
    const warning = document.createElement("p");
    warning.textContent = "No notifications were sent. Organizational reporting must happen immediately.";
    target.append(warning);
  } catch (error) {
    target.textContent = error.message;
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

byId("incident-discovered").value = localDateInput(Date.now());
byId("recipient-occurred").value = localDateInput(Date.now());
for (const id of ["channeler-deadline-form", "channeler-retention-form",
                   "channeler-training-form", "channeler-rapback-form"]) {
  const form = byId(id);
  for (const field of form.elements) {
    if (field.type === "datetime-local" && field.name !== "acknowledged_at"
        && field.name !== "last_training_at") field.value = localDateInput(Date.now());
  }
}
refreshRecipientFields();
byId("local-date").textContent = new Date().toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }).toUpperCase();
byId("refresh").addEventListener("click", refresh);
byId("definition-query").addEventListener("input", renderDefinitions);
byId("section-one-form").addEventListener("submit", runSectionOneAssessment);
byId("incident-calculate").addEventListener("click", calculateIncident);
byId("recipient-event").addEventListener("change", refreshRecipientFields);
for (const formName of ["deadline","retention","training","rapback"]) {
  byId("channeler-" + formName + "-form").addEventListener("submit", runChannelerPlan);
}
byId("recipient-template-select").addEventListener("change", changeRecipientTemplate);
byId("channeler-template-select").addEventListener("change", chooseChannelerTemplate);
byId("channeler-copy-template").addEventListener("click", copyChannelerTemplate);
byId("recipient-copy-template").addEventListener("click", copyRecipientTemplate);
byId("recipient-planner").addEventListener("submit", calculateRecipientDeadlines);
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

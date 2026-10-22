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
async function checkChannelerSchema(kind) {
  const result = byId("channeler-schema-result");
  const current = new Date().toISOString();
  const request = kind === "dissemination" ? {
    recipient_oca_or_ori: "TEST-OCA-ABC123",
    transaction_control_number: "TEST-TCN-ABC123",
    statutory_authority_test_ref: "TEST-AUTH-ABC123",
    disseminated_at: current,
    as_of: current,
    means: "test_secure_electronic"
  } : {
    transaction_control_number: "TEST-TCN-ABC123",
    subscription_identifier: "TEST-RBS-ABC123"
  };
  try {
    const reply = await api(kind === "dissemination"
      ? "/api/channeler/dissemination"
      : "/api/channeler/rapback-reference", "POST", request);
    result.textContent = kind === "dissemination"
      ? "Five required fields structurally valid. Hypothetical minimum log retention until " +
        new Date(reply.minimum_retention_until_utc).toLocaleString() +
        ". No CHRI log stored and no statutory authority verified."
      : "Exactly two synthetic fields valid: TCN and Rap Back Subscription Identifier. No applicant PII stored, no actual subscription created.";
  } catch (error) {
    result.textContent = error.message;
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

async function estimateOversightSample(event) {
  event.preventDefault();
  const target = byId("oversight-sample-result");
  const form = byId("oversight-sample-form");
  const request = { method: "simple_random" };
  for (const field of form.elements) {
    if (!field.name) continue;
    request[field.name] = Number(field.value);
  }
  try {
    const result = await api("/api/fbi-oversight/sample", "POST", request);
    target.replaceChildren();
    const lines = [
      ["Channeler sample estimate", String(result.channeler_sample_estimate)],
      ["Authorized Recipient sample estimate", String(result.recipient_sample_estimate)],
      ["Actual audit sampling program approved", "No"],
      ["Methodology limitation", result.limitations],
    ];
    for (const [key, value] of lines) {
      const line = document.createElement("p");
      const label = document.createElement("strong");
      label.textContent = key + ": ";
      line.append(label, document.createTextNode(value));
      target.append(line);
    }
  } catch (error) { target.textContent = error.message; }
}

let oversightTemplates = [];

function showOversight(payload) {
  const {catalog, progress} = payload;
  byId("oversight-count").textContent =
    progress.reported_count + " / " + catalog.check_count + " reported · 0 independently verified";
  const root = byId("oversight-checks");
  const opened = new Set(Array.from(root.querySelectorAll("details[open]")).map(x => x.dataset.section));
  root.replaceChildren();
  for (const clause of catalog.clauses) {
    const details = document.createElement("details");
    details.className = "recipient-group";
    details.dataset.section = clause.section;
    details.open = opened.has(clause.section);
    const heading = document.createElement("summary");
    heading.textContent = "§" + clause.section + " · " + clause.responsible_party;
    details.append(heading);
    const summary = document.createElement("p");
    summary.className = "channeler-clause-text";
    summary.textContent = clause.description + " · Source printed p. " + clause.printed_page;
    details.append(summary);
    for (const check of catalog.checks.filter(x => x.section === clause.section)) {
      const prior = progress.checks[check.id];
      const line = document.createElement("div");
      line.className = "recipient-check";
      const label = document.createElement("label");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = Boolean(prior?.reported);
      label.append(checkbox, document.createTextNode(check.description));
      const help = document.createElement("small");
      help.textContent = "Actor: " + check.actor + " · reference is operator-reported, never official verification";
      const entry = document.createElement("div");
      entry.className = "recipient-entry";
      const reference = document.createElement("input");
      reference.type = "text";
      reference.maxLength = 64;
      reference.autocomplete = "off";
      reference.spellcheck = false;
      reference.placeholder = "Safe reference code, e.g. REVIEW-2026-001";
      reference.setAttribute("aria-label", "Document reference " + check.id);
      reference.value = prior?.evidence_ref || "";
      const save = document.createElement("button");
      save.type = "button";
      save.className = "recipient-save";
      save.textContent = "Record";
      const note = document.createElement("p");
      note.className = "recipient-note";
      note.setAttribute("aria-live", "polite");
      save.addEventListener("click", async () => {
        save.disabled = true;
        try {
          await api("/api/fbi-oversight/check", "POST", {
            id: check.id, reported: checkbox.checked,
            evidence_ref: checkbox.checked ? reference.value.trim() : null
          });
          showOversight(await api("/api/fbi-oversight"));
        } catch (error) {
          note.textContent = error.message;
          note.className = "recipient-note error";
          save.disabled = false;
        }
      });
      entry.append(reference, save);
      line.append(label, help, entry, note);
      details.append(line);
    }
    root.append(details);
  }
}

async function calculateOversight(event) {
  event.preventDefault();
  const target = byId("oversight-output");
  target.replaceChildren();
  const occurred = byId("oversight-time").value;
  if (!occurred) { target.textContent = "Choose the reference date."; return; }
  const payload = {
    event: byId("oversight-event").value,
    occurred_at: new Date(occurred).toISOString(),
    as_of: new Date().toISOString()
  };
  try {
    const result = await api("/api/fbi-oversight/deadlines", "POST", payload);
    const fields = result.event === "first_approved_chri_receipt" ? [
      ["FBI initial audit certification AND results", result.fbi_initial_audit_and_certification_due_utc],
      ["Combined first representative-sample audit", result.combined_state_federal_first_sample_audit_due_utc],
      ["FBI one-year reference", result.fbi_one_year_audit_reference_utc],
      ["FBI next triennial reference", result.fbi_next_triennial_audit_reference_utc],
      ["Combined next triennial sample-audit reference", result.combined_state_federal_next_triennial_reference_utc],
    ] : result.event === "policy_update_notification" ? [
      ["FBI current documents due", result.policy_versions_available_by_utc],
    ] : [
      ["FBI personnel roster update due", result.access_roster_updated_by_utc],
    ];
    for (const [label, date] of fields) {
      const p = document.createElement("p");
      const strong = document.createElement("strong");
      strong.textContent = label + ": ";
      p.append(strong, document.createTextNode(new Date(date).toLocaleString()));
      target.append(p);
    }
    const caution = document.createElement("p");
    caution.textContent = result.scheduling_assumption || result.notes;
    target.append(caution);
    const notDone = document.createElement("p");
    notDone.textContent = "FBI approvals verified: No. Audits/notifications performed: No.";
    target.append(notDone);
  } catch (error) {
    target.textContent = error.message;
  }
}

function showOversightTemplates(payload) {
  oversightTemplates = payload.templates;
  const select = byId("oversight-template");
  const prior = select.value;
  select.replaceChildren();
  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = "Select a document…";
  select.append(empty);
  for (const entry of oversightTemplates) {
    const option = document.createElement("option");
    option.value = entry.id;
    option.textContent = entry.title + " · " + entry.sections.join(", ");
    select.append(option);
  }
  select.value = oversightTemplates.some(x => x.id === prior) ? prior : "";
  selectOversightTemplate();
}
function selectOversightTemplate() {
  const entry = oversightTemplates.find(x => x.id === byId("oversight-template").value);
  byId("oversight-template-text").value = entry ? entry.body : "";
  byId("oversight-copy").disabled = !entry;
  byId("oversight-template-note").textContent =
    entry ? "Blank outline only. No official FBI/Compact Officer action has occurred." :
            "No document has been sent or approved.";
}
async function copyOversightTemplate() {
  const body = byId("oversight-template-text").value;
  if (!body) return;
  try {
    await navigator.clipboard.writeText(body);
    byId("oversight-template-note").textContent =
      "Blank outline copied. Obtain authentic agency decisions through approved external channels.";
  } catch (_) {
    byId("oversight-template-note").textContent =
      "Clipboard denied; manually select and copy the blank outline.";
  }
}

let miscTemplates = [];

function renderMisc(payload) {
  const {catalog, progress} = payload;
  const container = byId("misc-checks");
  const opened = new Set(Array.from(container.querySelectorAll("details[open]"))
    .map(detail => detail.dataset.section));
  container.replaceChildren();
  byId("misc-count").textContent =
    progress.reported_count + " / " + catalog.check_count + " reported · none verified";
  for (const section of catalog.sections) {
    const clause = catalog.clauses.find(x => x.section === section);
    const group = document.createElement("details");
    group.className = "recipient-group";
    group.dataset.section = section;
    group.open = opened.has(section);
    const summary = document.createElement("summary");
    summary.textContent = "§" + section + " · " + clause.topic.replaceAll("_", " ");
    const explanation = document.createElement("p");
    explanation.className = "channeler-clause-text";
    explanation.textContent = clause.description + " · PDF page " + clause.pdf_page;
    group.append(summary, explanation);
    for (const check of catalog.checks.filter(x => x.section === section)) {
      const previous = progress.checks[check.id];
      const row = document.createElement("div");
      row.className = "recipient-check";
      const label = document.createElement("label");
      const box = document.createElement("input");
      box.type = "checkbox";
      box.checked = Boolean(previous?.reported);
      label.append(box, document.createTextNode(check.description));
      const help = document.createElement("small");
      help.textContent = "Operator-reported evidence only · NEVER authorizes a waiver, audit or mail dispatch";
      const controls = document.createElement("div");
      controls.className = "recipient-entry";
      const reference = document.createElement("input");
      reference.type = "text";
      reference.maxLength = 64;
      reference.autocomplete = "off";
      reference.spellcheck = false;
      reference.placeholder = "Nonidentifying reference e.g. GOV-2026-001";
      reference.setAttribute("aria-label", "Evidence code for " + check.id);
      reference.value = previous?.evidence_ref || "";
      const save = document.createElement("button");
      save.type = "button";
      save.className = "recipient-save";
      save.textContent = "Record";
      const feedback = document.createElement("p");
      feedback.className = "recipient-note";
      feedback.setAttribute("aria-live", "polite");
      save.addEventListener("click", async () => {
        save.disabled = true;
        try {
          await api("/api/misc/check", "POST", {
            id: check.id, reported: box.checked,
            evidence_ref: box.checked ? reference.value.trim() : null
          });
          await updateMisc();
        } catch (error) {
          feedback.textContent = error.message;
          feedback.className = "recipient-note error";
          save.disabled = false;
        }
      });
      controls.append(reference, save);
      row.append(label, help, controls, feedback);
      group.append(row);
    }
    container.append(group);
  }
}
async function updateMisc() {
  renderMisc(await api("/api/misc"));
}
function putMiscRows(target, rows) {
  target.replaceChildren();
  for (const [label, value] of rows) {
    const p = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = label + ": ";
    p.append(strong, document.createTextNode(String(value)));
    target.append(p);
  }
  const caution = document.createElement("p");
  caution.textContent = "No agency decision, approval, waiver, mail dispatch or CHRI operation was performed.";
  target.append(caution);
}
async function evaluateMisc(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const kind = form.dataset.route;
  const body = {};
  for (const field of form.elements) {
    if (!field.name) continue;
    body[field.name] = field.type === "checkbox" ? field.checked : field.value;
  }
  const target = byId("misc-" + kind + "-result");
  try {
    const data = await api("/api/misc/" + kind, "POST", body);
    if (kind === "scope") {
      putMiscRows(target, [
        ["Recipient-supporting asset covered", data.covered_by_section_5_01 ? "Yes" : "Not determined by this clause"],
        ["Named party under §5.02", data.party_named_by_section_5_02 ? "Yes" : "No"],
        ["CJISSECPOL incorporated", "Yes · §5.03"],
        ["New rights granted", "No"]
      ]);
    } else if (kind === "changes") {
      putMiscRows(target, [
        ["Review outcome", data.status],
        ["Required authority", data.formal_change_authority],
        ["Restriction", data.reason],
        ["Minimums relaxed", "No; claimed approvals unverified"]
      ]);
    } else if (kind === "authority") {
      putMiscRows(target, [
        ["Source section", data.section],
        ["Actor named for requested action", data.named_authority_for_action ? "Yes" : "No"],
        ["Official identity or delegation verified", "No"],
        ["Audit or investigation performed", "No"]
      ]);
    } else {
      const address = data.published_2023_routing;
      putMiscRows(target, [
        ["Required method in 2023 Standard", address.method],
        ["Recipient", address.recipient],
        ["Routing", address.routing],
        ["Organization", address.organization],
        ["Street", address.street],
        ["City/state/ZIP", address.city_state_zip],
        ["Current address confirmed", "No — verify with official authority"],
        ["Notice dispatched or received", "No"]
      ]);
    }
  } catch (error) {
    target.textContent = error.message;
  }
}
function showMiscTemplates(payload) {
  miscTemplates = payload.templates;
  const select = byId("misc-template-select");
  const existing = select.value;
  select.replaceChildren();
  const blank = document.createElement("option");
  blank.value = "";
  blank.textContent = "Choose a blank template…";
  select.append(blank);
  for (const item of miscTemplates) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.title + " · " + item.sections.join(", ");
    select.append(option);
  }
  select.value = miscTemplates.some(x => x.id === existing) ? existing : "";
  chooseMiscTemplate();
}
function chooseMiscTemplate() {
  const current = miscTemplates.find(x => x.id === byId("misc-template-select").value);
  byId("misc-template-text").value = current ? current.body : "";
  byId("misc-template-copy").disabled = !current;
  byId("misc-template-feedback").textContent = current
    ? "Unpopulated draft only. No mailing, government action or policy amendment."
    : "No document is sent or approved.";
}
async function copyMiscTemplate() {
  const text = byId("misc-template-text").value;
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    byId("misc-template-feedback").textContent =
      "Blank outline copied. Complete and deliver only through an authorized external process.";
  } catch (_) {
    byId("misc-template-feedback").textContent =
      "Clipboard unavailable; manually select and copy the blank document.";
  }
}

async function refresh() {
  if (!token) return;
  byId("refresh").disabled = true;
  try {
    const [status, log, register, sectionOne, recipient, templates, channeler, channelerForms, oversight, oversightForms, misc, miscForms] = await Promise.all([api("/api/status"), api("/api/activity"), api("/api/readiness"), api("/api/section-one"), api("/api/recipient"), api("/api/recipient/templates"), api("/api/channeler"), api("/api/channeler/templates"), api("/api/fbi-oversight"), api("/api/fbi-oversight/templates"), api("/api/misc"), api("/api/misc/templates")]);
    showStatus(status);
    showActivity(log.events);
    showReadiness(register);
    sectionOneCatalog = sectionOne;
    renderDefinitions();
    showRecipient(recipient);
    showRecipientTemplates(templates);
    showChanneler(channeler);
    showChannelerTemplates(channelerForms);
    showOversight(oversight);
    showOversightTemplates(oversightForms);
    renderMisc(misc);
    showMiscTemplates(miscForms);
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
byId("oversight-time").value = localDateInput(Date.now());
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
byId("oversight-planner").addEventListener("submit", calculateOversight);
byId("oversight-sample-form").addEventListener("submit", estimateOversightSample);
byId("oversight-template").addEventListener("change", selectOversightTemplate);
byId("oversight-copy").addEventListener("click", copyOversightTemplate);
for (const id of ["scope", "changes", "authority", "mail"]) {
  byId("misc-" + id + "-form").addEventListener("submit", evaluateMisc);
}
byId("misc-template-select").addEventListener("change", chooseMiscTemplate);
byId("misc-template-copy").addEventListener("click", copyMiscTemplate);
byId("channeler-check-dissemination").addEventListener("click", () => checkChannelerSchema("dissemination"));
byId("channeler-check-rapback-ref").addEventListener("click", () => checkChannelerSchema("rapback"));
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

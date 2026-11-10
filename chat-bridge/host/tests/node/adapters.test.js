// Chat Bridge v2 — Node tests for the provider adapters (spec section 8).
// Runs with a minimal fake DOM: `node adapters.test.js`.
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

// ---------------- Minimal fake DOM ----------------

class FakeElement {
  constructor(tag, attrs = {}, options = {}) {
    this.tagName = String(tag).toUpperCase();
    this.attributes = {};
    this.children = [];
    this.parent = null;
    this._text = options.text || "";
    this._height = options.height == null ? 100 : options.height;
    this._listeners = {};
    this._clicked = 0;
    this.value = options.value;
    this.disabled = false;
    this.title = attrs.title || "";
    for (const [k, v] of Object.entries(attrs)) this.attributes[k] = String(v);
  }
  get classList() {
    const self = this;
    return {
      contains: (c) => (self.attributes.class || "").split(/\s+/).includes(c)
    };
  }
  get className() { return this.attributes.class || ""; }
  get textContent() {
    const kids = this.children.map((c) => c.textContent).join("");
    return this._text + kids;
  }
  set textContent(value) { this._text = String(value); this.children = []; }
  get innerText() { return this.textContent; }
  get parentElement() { return this.parent; }
  setAttribute(k, v) { this.attributes[k] = String(v); }
  getAttribute(k) { return k in this.attributes ? this.attributes[k] : null; }
  appendChild(child) { child.parent = this; this.children.push(child); return child; }
  addEventListener(type, fn) { (this._listeners[type] = this._listeners[type] || []).push(fn); }
  dispatchEvent(event) {
    (this._listeners[event.type] || []).forEach((fn) => fn(event));
    if (event.bubbles && this.parent) this.parent.dispatchEvent(event);
    return !event.defaultPrevented;
  }
  focus() {}
  click() { this._clicked += 1; this.dispatchEvent({ type: "click", bubbles: true }); }
  getBoundingClientRect() { return { width: 100, height: this._height, top: 0, left: 0, bottom: this._height }; }
  closest(selector) {
    let node = this;
    while (node) {
      if (node.matches && node.matches(selector)) return node;
      node = node.parent;
    }
    return null;
  }
  matches(selector) {
    return isElementMatch(this, splitComma(selector));
  }
  querySelectorAll(selector) { return this._descendants().filter((el) => isElementMatch(el, splitComma(selector))); }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  _descendants() {
    const out = [];
    const walk = (el) => { for (const child of el.children) { out.push(child); walk(child); } };
    walk(this);
    return out;
  }
}

function splitComma(selector) {
  return selector.split(",").map((s) => s.trim()).filter(Boolean);
}

// Match one compound simple selector (no combinators) against an element.
function matchesCompound(el, part) {
  let rest = part.trim();
  let tag = null, id = null;
  const classes = [];
  const attrs = [];
  const re = /([#.])?([A-Za-z0-9_-]+)|\[(([A-Za-z-]+))\s*([*^$~|]?=)?\s*("([^"]*)"|'([^']*)'|([^\]]+))?\]/g;
  let m;
  while ((m = re.exec(rest))) {
    if (m[1] === "#") id = m[2];
    else if (m[1] === ".") classes.push(m[2]);
    else if (!m[1] && m[2] && !attrs.length && !tag) tag = m[2];
    else if (m[3]) {
      const name = m[4];
      const op = m[5] || "";
      let value = m[6] != null ? m[6] : m[7] != null ? m[7] : m[8] != null ? m[8] : "";
      value = value.replace(/^["']|["']$/g, "");
      attrs.push({ name, op, value });
    }
  }
  if (tag && el.tagName !== tag.toUpperCase()) return false;
  if (id && el.attributes.id !== id) return false;
  for (const cls of classes) if (!el.className.split(/\s+/).includes(cls)) return false;
  for (const a of attrs) {
    const actual = el.attributes[a.name];
    if (actual == null) return false;
    if (!a.op) continue;
    if (a.op === "=" && actual !== a.value) return false;
    if (a.op === "*=" && !actual.includes(a.value)) return false;
    if (a.op === "^=" && !actual.startsWith(a.value)) return false;
    if (a.op === "$=" && !actual.endsWith(a.value)) return false;
  }
  return true;
}

// Full selector with descendant combinators (split on whitespace).
function isElementMatch(el, selectorParts) {
  return selectorParts.some((part) => {
    const steps = part.split(/\s+/);
    // Element must match the last step; each earlier step must be an ancestor.
    if (!matchesCompound(el, steps[steps.length - 1])) return false;
    let ancestor = el.parent;
    let i = steps.length - 2;
    while (i >= 0 && ancestor) {
      if (matchesCompound(ancestor, steps[i])) i -= 1;
      ancestor = ancestor.parent;
    }
    return i < 0;
  });
}

function makeDocument(root) {
  return {
    documentElement: root,
    body: root,
    title: "Fake",
    querySelectorAll: (sel) => root.querySelectorAll(sel),
    querySelector: (sel) => root.querySelector(sel),
    execCommand: () => true,
    addEventListener: () => {}
  };
}

// ---------------- Load adapters in a sandbox ----------------

function loadAdapters(doc) {
  const registry = new Map();
  const windowShim = {
    __cb: {
      registerAdapter(adapter) { registry.set(adapter.id, adapter); },
      _fallbackKeys: null
    },
    location: null,
    addEventListener: () => {}
  };
  const sandbox = {
    window: windowShim,
    document: doc,
    location: docLocation,
    HTMLElement: Function,
    HTMLTextAreaElement: class {},
    HTMLInputElement: class {},
    Event: class { constructor(type, opts = {}) { this.type = type; Object.assign(this, opts); } },
    InputEvent: class { constructor(type, opts = {}) { this.type = type; Object.assign(this, opts); } },
    KeyboardEvent: class { constructor(type, opts = {}) { this.type = type; Object.assign(this, opts); } },
    MutationObserver: class { observe() {} },
    setTimeout: () => 0,
    clearTimeout: () => {},
    setInterval: () => 0,
    clearInterval: () => {},
    Date,
    JSON,
    console,
    Math
  };
  windowShim.location = docLocation;
  sandbox.window.location = docLocation;
  vm.createContext(sandbox);
  const dir = path.join(__dirname, "..", "..", "..", "extension");
  for (const file of ["adapter-chatgpt.js", "adapter-claude.js", "adapter-gemini.js", "adapter-grok.js"]) {
    const code = fs.readFileSync(path.join(dir, file), "utf8");
    vm.runInContext(code, sandbox, { filename: file });
  }
  return registry;
}

let docLocation;

// ---------------- Tiny test harness ----------------

let passed = 0;
let failed = 0;
function check(name, condition, extra) {
  if (condition) {
    passed += 1;
    console.log(`  ok    ${name}`);
  } else {
    failed += 1;
    console.log(`  FAIL  ${name}${extra ? ` — ${JSON.stringify(extra)}` : ""}`);
  }
}
function section(name) { console.log(`\n${name}`); }

// ---------------- Tests ----------------

section("conversation id parsing");
{
  const mk = (href) => {
    const u = new URL(href);
    return { pathname: u.pathname, search: u.search, href };
  };
  const registry = loadAdapters(makeDocument(new FakeElement("html")));
  const cid = (adapter, href) => adapter.conversationId(mk(href));

  check("chatgpt /c/<id>", cid(registry.get("chatgpt"), "https://chatgpt.com/c/abc-123") === "abc-123");
  check("chatgpt /c/<id> with query", cid(registry.get("chatgpt"), "https://chatgpt.com/c/xyz?x=1") === "xyz");
  check("chatgpt home -> null", cid(registry.get("chatgpt"), "https://chatgpt.com/") === null);
  check("chat.openai.com alias", cid(registry.get("chatgpt"), "https://chat.openai.com/c/oid") === "oid");

  check("claude /chat/<id>", cid(registry.get("claude"), "https://claude.ai/chat/xyz-1") === "xyz-1");
  check("claude home -> null", cid(registry.get("claude"), "https://claude.ai/") === null);

  check("gemini /app/<id>", cid(registry.get("gemini"), "https://gemini.google.com/app/u/0/abc") === "abc");
  check("gemini /app/<id> (u/0)", cid(registry.get("gemini"), "https://gemini.google.com/app/def") === "def");
  check("gemini home -> null", cid(registry.get("gemini"), "https://gemini.google.com/") === null);

  check("grok /chat/<id>", cid(registry.get("grok"), "https://grok.com/chat/42") === "42");
  check("grok home -> null", cid(registry.get("grok"), "https://grok.com/") === null);
}

section("chatgpt extract mapping (verified 2026-11-10 DOM)");
{
  const root = new FakeElement("html");
  docLocation = { pathname: "/c/conv-1", href: "https://chatgpt.com/c/conv-1" };
  const registry = loadAdapters(makeDocument(root));
  const gpt = registry.get("chatgpt");

  const user = new FakeElement("div", { "data-chatgpt-search-unit-key": "k:0:user", "data-chatgpt-search-message-ids": "uuid-u1 uuid-x" }, { text: "Hello there" });
  const assistant = new FakeElement("div", { "data-chatgpt-search-unit-key": "k:1:assistant", "data-chatgpt-search-message-ids": "uuid-a1" }, { text: "ChatGPT said: Hi! How can I help?" });
  root.appendChild(user);
  root.appendChild(assistant);

  const units = gpt.extractUnits(root);
  check("two units extracted", units.length === 2, units.map((u) => u.role));
  check("user role + key", units[0].role === "user" && units[0].key === "dom:uuid-u1", units[0]);
  check("assistant role + key", units[1].role === "assistant" && units[1].key === "dom:uuid-a1", units[1]);
  check("screen-reader label stripped", gpt.cleanText(assistant) === "Hi! How can I help?", gpt.cleanText(assistant));
  check("user text intact", gpt.cleanText(user) === "Hello there");
}

section("chatgpt legacy DOM fallback + new-DOM preference");
{
  const root = new FakeElement("html");
  docLocation = { pathname: "/c/conv-2", href: "https://chatgpt.com/c/conv-2" };
  const registry = loadAdapters(makeDocument(root));
  const gpt = registry.get("chatgpt");

  const legacyUser = new FakeElement("div", { "data-message-author-role": "user", "data-message-id": "L1" }, { text: "legacy hi" });
  root.appendChild(legacyUser);
  let units = gpt.extractUnits(root);
  check("legacy units mapped", units.length === 1 && units[0].role === "user" && units[0].key === "dom:L1", units);

  const fresh = new FakeElement("div", { "data-chatgpt-search-unit-key": "k:0:user", "data-chatgpt-search-message-ids": "F1" }, { text: "fresh hi" });
  root.appendChild(fresh);
  units = gpt.extractUnits(root);
  check("fresh DOM preferred over legacy", units.length === 1 && units[0].key === "dom:F1", units);
}

section("chatgpt composer detection");
{
  const root = new FakeElement("html");
  docLocation = { pathname: "/c/conv-3", href: "https://chatgpt.com/c/conv-3" };
  const registry = loadAdapters(makeDocument(root));
  const gpt = registry.get("chatgpt");

  const hidden = new FakeElement("div", { class: "ProseMirror", role: "textbox", "aria-label": "Ask ChatGPT" }, { height: 0 });
  const visible = new FakeElement("div", { class: "ProseMirror", role: "textbox", "aria-label": "Ask ChatGPT" });
  root.appendChild(hidden);
  root.appendChild(visible);
  const composer = gpt.findComposer(root);
  check("visible ProseMirror picked over hidden", composer === visible);

  const root2 = new FakeElement("html");
  const legacy = new FakeElement("textarea", { id: "prompt-textarea" });
  root2.appendChild(legacy);
  check("#prompt-textarea fallback", registry.get("chatgpt").findComposer(root2) === legacy);
}

section("chatgpt send button (primary-action footer slot, verified path)");
{
  const root = new FakeElement("html");
  docLocation = { pathname: "/c/conv-4", href: "https://chatgpt.com/c/conv-4" };
  const registry = loadAdapters(makeDocument(root));
  const gpt = registry.get("chatgpt");

  const composer = new FakeElement("div", { class: "ProseMirror", role: "textbox" });
  const mic = new FakeElement("button", { "aria-label": "Voice" });
  const send = new FakeElement("button", {});
  send.appendChild(new FakeElement("span", { class: "primary-action-slot" }));
  const footer = new FakeElement("div", { class: "composer-footer" });
  footer.appendChild(mic);
  footer.appendChild(send);
  const wrap = new FakeElement("div", { class: "composer-wrap" });
  wrap.appendChild(composer);
  wrap.appendChild(footer);
  root.appendChild(wrap);

  const button = gpt.findSendButton(root, composer);
  check("primary-action button found via footer walk", button === send, button && button.tagName);
  check("clickable", typeof button.click === "function");
}

section("claude extract mapping (best-effort candidates)");
{
  const root = new FakeElement("html");
  docLocation = { pathname: "/chat/cla-1", href: "https://claude.ai/chat/cla-1" };
  const registry = loadAdapters(makeDocument(root));
  const claude = registry.get("claude");

  const user = new FakeElement("div", { "data-view": "user" }, { text: "Claude, hi" });
  const stream = new FakeElement("div", { "data-stream": "true" });
  const markdown = new FakeElement("div", { class: "markdown" }, { text: "Hello! I am Claude." });
  stream.appendChild(markdown);
  root.appendChild(user);
  root.appendChild(stream);

  const units = claude.extractUnits(root);
  check("user via data-view", units.some((u) => u.role === "user" && u.node === user), units.map((u) => u.role));
  check("assistant via stream markdown", units.some((u) => u.role === "assistant" && u.node === markdown));

  const diag = claude.diagnose(root);
  check("claude diagnose: not failed", diag.capture_failed === false, diag);
}

section("claude composer + diagnose failure mode");
{
  const root = new FakeElement("html");
  docLocation = { pathname: "/chat/cla-2", href: "https://claude.ai/chat/cla-2" };
  const registry = loadAdapters(makeDocument(root));
  const claude = registry.get("claude");

  const portal = new FakeElement("div", { id: "claude-chat-provider-portal" });
  const editable = new FakeElement("div", { contenteditable: "true" });
  portal.appendChild(editable);
  root.appendChild(portal);
  check("composer via portal descendant", claude.findComposer(root) === editable);

  const emptyRoot = new FakeElement("html");
  docLocation = { pathname: "/chat/cla-3", href: "https://claude.ai/chat/cla-3" };
  const registry2 = loadAdapters(makeDocument(emptyRoot));
  const diag = registry2.get("claude").diagnose(emptyRoot);
  check("diagnose reports failure + reason", diag.capture_failed === true && diag.reason.length > 0, diag);
  check("diagnose reports candidates", typeof diag.candidates === "object" && "editables" in diag.candidates, diag.candidates);
}

section("gemini extract + composer");
{
  const root = new FakeElement("html");
  docLocation = { pathname: "/app/u/0/gem-1", href: "https://gemini.google.com/app/u/0/gem-1" };
  const registry = loadAdapters(makeDocument(root));
  const gemini = registry.get("gemini");

  const userQuery = new FakeElement("user-query", { "message-id": "gm-u1" }, { text: "Tell me a fact" });
  const modelResp = new FakeElement("model-response", { "message-id": "gm-a1" }, { text: "Octopuses have three hearts." });
  root.appendChild(userQuery);
  root.appendChild(modelResp);
  const units = gemini.extractUnits(root);
  check("user-query -> user", units.some((u) => u.role === "user" && u.key === "dom:gm-u1"), units);
  check("model-response -> assistant", units.some((u) => u.role === "assistant" && u.key === "dom:gm-a1"));

  const rich = new FakeElement("rich-textarea", {});
  const editable = new FakeElement("div", { contenteditable: "true" });
  rich.appendChild(editable);
  root.appendChild(rich);
  check("composer via rich-textarea descendant", gemini.findComposer(root) === editable);
}

section("grok extract + composer");
{
  const root = new FakeElement("html");
  docLocation = { pathname: "/chat/gro-1", href: "https://grok.com/chat/gro-1" };
  const registry = loadAdapters(makeDocument(root));
  const grok = registry.get("grok");

  const userEl = new FakeElement("div", { "data-message-role": "user", "data-message-id": "gr-u1" }, { text: "hi grok" });
  const asstEl = new FakeElement("div", { "data-message-role": "assistant", "data-message-id": "gr-a1" }, { text: "hi back" });
  root.appendChild(userEl);
  root.appendChild(asstEl);
  const units = grok.extractUnits(root);
  check("user role mapping", units.some((u) => u.role === "user" && u.key === "dom:gr-u1"), units);
  check("assistant role mapping", units.some((u) => u.role === "assistant" && u.key === "dom:gr-a1"));

  const textarea = new FakeElement("textarea", { placeholder: "Message Grok" });
  root.appendChild(textarea);
  check("composer via Grok placeholder", grok.findComposer(root) === textarea);
}

section("shared transport wiring");
{
  const root = new FakeElement("html");
  docLocation = { pathname: "/c/conv-9", href: "https://chatgpt.com/c/conv-9" };
  const registry = loadAdapters(makeDocument(root));
  check("four adapters registered", registry.size === 4, [...registry.keys()]);
  check("ids", ["chatgpt", "claude", "gemini", "grok"].every((id) => registry.has(id)));
}

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);

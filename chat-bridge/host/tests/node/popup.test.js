// Chat Bridge v2 — regression guard: every element id referenced in popup.js
// must exist in popup.html (this exact gap caused the 2026-11-10 popup crash:
// `$("allowSend")` was null because the checkbox input was missing from the HTML).
"use strict";
const fs = require("fs");
const path = require("path");

const extDir = path.join(__dirname, "..", "..", "..", "extension");
const js = fs.readFileSync(path.join(extDir, "popup.js"), "utf8");
const html = fs.readFileSync(path.join(extDir, "popup.html"), "utf8");

const referenced = new Set();
for (const m of js.matchAll(/\$\(\s*"([A-Za-z0-9_-]+)"\s*\)/g)) referenced.add(m[1]);

let passed = 0;
let failed = 0;
for (const id of [...referenced].sort()) {
  const present = new RegExp(`id\\s*=\\s*"${id}"`).test(html) || new RegExp(`id\\s*=\\s*'${id}'`).test(html);
  if (present) {
    passed += 1;
    console.log(`  ok    #${id}`);
  } else {
    failed += 1;
    console.log(`  FAIL  #${id} referenced in popup.js but missing from popup.html`);
  }
}
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);

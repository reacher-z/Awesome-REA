/* Run the pinned awesome-lint on one Markdown file and save every finding as JSON for
   scripts/awesome_lint_report.py. The findings never set the exit status; only a failure to lint does. */
import fs from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';
import process from 'node:process';

const [input = 'README.md', output = '.cache/awesome-lint/findings.json'] = process.argv.slice(2);
let lint;
try {
  // The package has no `exports` or `main` field, so import its entry file by name.
  ({default: lint} = await import('awesome-lint/index.js'));
} catch (error) {
  console.error(`awesome-lint is not installed (${error.code || error.message}); run \`npm ci --prefix tests/awesome-lint --ignore-scripts\`.`);
  process.exit(1);
}
// The repository-metadata rule reads `github_token` when it is set; the workflow passes a read-only token.
const files = await lint({filename: input});
const findings = files.flatMap(file => file.messages.map(message => ({
  file: path.basename(file.path), rule: message.ruleId || message.source || 'unknown',
  line: message.line ?? null, column: message.column ?? null, reason: String(message.reason),
})));
fs.mkdirSync(path.dirname(output), {recursive: true});
const {version} = createRequire(import.meta.url)('awesome-lint/package.json');
fs.writeFileSync(output, JSON.stringify({linter: `awesome-lint@${version}`, input, findings}, null, 2) + '\n');
console.log(`awesome-lint reported ${findings.length} finding(s) in ${input}; saved to ${output}.`);

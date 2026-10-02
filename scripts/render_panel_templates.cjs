// Compatibility entry point. Render from catalog geometry without browser automation.
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const result = spawnSync(process.env.PYTHON || 'python', [
  path.join(__dirname, 'render_panel_templates.py'), ...process.argv.slice(2)
], { stdio: 'inherit', windowsHide: true });
if (result.error) console.error(result.error.message);
process.exit(result.status === null ? 1 : result.status);

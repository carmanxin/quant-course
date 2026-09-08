// Test precompute on a single file (usage: node run-one.mjs <hash>)
import { runOne } from '../../scripts/precompute-py-outputs.mjs';
import path from 'node:path';

const hash = process.argv[2] || '93ba1436';
const pyFile = path.resolve(`public/code/_auto/${hash}.py`);
console.log('Running:', pyFile);
const result = await runOne(pyFile);
console.log('Result:', result);
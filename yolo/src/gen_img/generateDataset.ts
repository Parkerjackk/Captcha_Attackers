import * as fs from 'fs';
import * as path from 'path';
import { createCaptchaSession } from './captchaService.js';
import { renderCaptchaScene } from './renderService.js';

// Match PO V-Ray image size (400x400)
const IMAGE_SIZE = 400;

// Camera angles to cover all views: multiples of 15deg
const ANGLES: Array<{ rotX: number; rotY: number }> = [];
for (let rx = -85; rx <= 85; rx += 5) {
  for (let ry = -85; ry <= 85; ry += 5) {
    ANGLES.push({ rotX: rx, rotY: ry });
  }
}

// Same character set as in captchaService.ts
const CAPTCHA_CHARS = [
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U',
  'V', 'W', 'X', 'Y', 'Z',
  '2', '3', '4', '5', '8',
  '@', '#', '$', '%', '&', '*', '+', '='
];

const CHAR_TO_ID = new Map<string, number>(
  CAPTCHA_CHARS.map((c, idx) => [c, idx])
);

function charToId(c: string): number {
  const id = CHAR_TO_ID.get(c.toUpperCase());
  if (id === undefined) {
    throw new Error(`Unknown character "${c}" in dataset generator`);
  }
  return id;
}

// Dataset size
const NUM_SESSIONS = 207; // 9*23
const MAX_PARALLEL = 128;

type Split = 'train' | 'val';

// Approximate 95/5 split
function chooseSplit(): Split {
  const r = Math.random();
  if (r < 0.95) return 'train';
  return 'val';
}

async function main() {
  const outRoot = path.join(process.cwd(), 'dataset');
  const imgRoot = path.join(outRoot, 'images');
  const lblRoot = path.join(outRoot, 'labels');

  // Clean existing images/labels folders if they already exist
  if (fs.existsSync(imgRoot)) {
    fs.rmSync(imgRoot, { recursive: true, force: true });
  }
  if (fs.existsSync(lblRoot)) {
    fs.rmSync(lblRoot, { recursive: true, force: true });
  }

  // Recreate folder structure
  const splits: Split[] = ['train', 'val'];
  for (const split of splits) {
    fs.mkdirSync(path.join(imgRoot, split), { recursive: true });
    fs.mkdirSync(path.join(lblRoot, split), { recursive: true });
  }

  console.log('Generating YOLO dataset...');

  for (let i = 0; i < NUM_SESSIONS; i++) {
    const session = createCaptchaSession();
    const { sessionId, shapes } = session;

    const tempDir = path.join('/dev/shm/YOLO_attacker', 'temp', sessionId);
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }

    // Multi-processing
    const angleBatches: Array<Array<{ rotX: number; rotY: number }>> = [];
    for (let j = 0; j < ANGLES.length; j += MAX_PARALLEL) {
      angleBatches.push(ANGLES.slice(j, j + MAX_PARALLEL));
    }

    // Process each batch sequentially, but each batch in parallel
    for (const batch of angleBatches) {
      await Promise.all(
        batch.map(async ({ rotX, rotY }) => {
          const { imageBuffer, clickRegions } =
            await renderCaptchaScene(sessionId, shapes, rotX, rotY);

          const split = chooseSplit();
          const imgDir = path.join(imgRoot, split);
          const lblDir = path.join(lblRoot, split);

          const baseName = `${sessionId}_rx${rotX}_ry${rotY}`;
          const imageFile = path.join(imgDir, `${baseName}.png`);
          const labelFile = path.join(lblDir, `${baseName}.txt`);

          // Save image
          fs.writeFileSync(imageFile, imageBuffer);

          // Build YOLO labels (one line per visible character)
          const lines: string[] = [];

          for (const region of clickRegions) {
            const shape = shapes.find(s => s.id === region.id);
            if (!shape || !shape.params?.text) continue;

            const ch = shape.params.text as string;
            const classId = charToId(ch);

            const xCenter = (region.x + region.width / 2) / IMAGE_SIZE;
            const yCenter = (region.y + region.height / 2) / IMAGE_SIZE;
            const w = region.width / IMAGE_SIZE;
            const h = region.height / IMAGE_SIZE;

            lines.push(
              `${classId} ${xCenter.toFixed(6)} ${yCenter.toFixed(6)} ${w.toFixed(6)} ${h.toFixed(6)}`
            );
          }

          fs.writeFileSync(labelFile, lines.join('\n'), 'utf-8');
        })
      );
    }

    // Clean up temp dir if exists
    if (fs.existsSync(tempDir)) {
      fs.rmdirSync(tempDir, { recursive: true });
    }

    console.log(`Generated dataset for session ${i + 1}/${NUM_SESSIONS}`);
  }

  // Auto-generate YOLO dataset YAML
  const datasetPath = path.resolve(outRoot);
  const yamlPath = path.join(outRoot, 'captcha.yaml');

  let yaml = '';
  yaml += `path: ${datasetPath}\n`;
  yaml += `train: images/train\n`;
  yaml += `val: images/val\n`;
  yaml += `\n`;
  yaml += `names:\n`;

  CAPTCHA_CHARS.forEach((ch, idx) => {
    // JSON.stringify handles symbols like @,#,$ correctly
    yaml += `  ${idx}: ${JSON.stringify(ch)}\n`;
  });

  fs.writeFileSync(yamlPath, yaml, 'utf-8');
}

main().catch(err => {
  console.error('Dataset generation failed:', err);
  process.exit(1);
});

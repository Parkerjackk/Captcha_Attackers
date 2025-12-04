import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';
import { PNG } from 'pngjs';

import { ShapeData } from './captcha.js';

const execAsync = promisify(exec);
const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);
const unlinkAsync = promisify(fs.unlink);

// In-memory cache of rendered images per session and camera angle
// Map<sessionId, Map<angleKey, Buffer>>
const imageCache = new Map<string, Map<string, Buffer>>();

// Camera / rendering constants
const IMAGE_SIZE = 400;
const CAMERA_DISTANCE = 20;

// Key for caching by camera rotation
function getAngleKey(rotX: number, rotY: number): string {
  return `${rotX}_${rotY}`;
}

// 2D click-region interface
export interface ClickRegion {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

// Render result interface
export interface RenderResult {
  imageBuffer: Buffer;
  clickRegions: ClickRegion[];
}

type Vec3 = [number, number, number];

function normalize([x, y, z]: Vec3): Vec3 {
  const len = Math.sqrt(x * x + y * y + z * z) || 1;
  return [x / len, y / len, z / len];
}

function dot([ax, ay, az]: Vec3, [bx, by, bz]: Vec3): number {
  return ax * bx + ay * by + az * bz;
}

// Convert hex colour into POV-Ray RGB components (0–1 range)
function hexToRgb(hex: string): [number, number, number] {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (result) {
    return [
      parseInt(result[1], 16) / 255,
      parseInt(result[2], 16) / 255,
      parseInt(result[3], 16) / 255
    ];
  }
  return [1, 1, 1];
}

// Compute camera position from the same rotations used in generatePovScene
function getCameraPosition(
  cameraRotX: number,
  cameraRotY: number,
  distance: number = CAMERA_DISTANCE
): Vec3 {
  const rotXRad = cameraRotX * Math.PI / 180;
  const rotYRad = cameraRotY * Math.PI / 180;

  // Spherical-ish coordinates around the origin
  const camX = distance * Math.sin(rotYRad) * Math.cos(rotXRad);
  const camY = distance * Math.sin(rotXRad);
  const camZ = distance * Math.cos(rotYRad) * Math.cos(rotXRad);

  return [camX, camY, camZ];
}

// Apply Euler rotations (rx, ry, rz in radians) to a vector, in the same order POV-Ray does
function applyEulerRotation(vec: Vec3, rot: Vec3): Vec3 {
  let [x, y, z] = vec;
  const [rx, ry, rz] = rot;

  // Rotate around X
  if (rx !== 0) {
    const cosX = Math.cos(rx);
    const sinX = Math.sin(rx);
    const ny = y * cosX - z * sinX;
    const nz = y * sinX + z * cosX;
    y = ny; z = nz;
  }

  // Rotate around Y
  if (ry !== 0) {
    const cosY = Math.cos(ry);
    const sinY = Math.sin(ry);
    const nx = x * cosY + z * sinY;
    const nz = -x * sinY + z * cosY;
    x = nx; z = nz;
  }

  // Rotate around Z
  if (rz !== 0) {
    const cosZ = Math.cos(rz);
    const sinZ = Math.sin(rz);
    const nx = x * cosZ - y * sinZ;
    const ny = x * sinZ + y * cosZ;
    x = nx; y = ny;
  }

  return [x, y, z];
}

// How strict we are about a character being "front-facing" relative to the camera
const FACING_ANGLE_THRESHOLD = 61 * Math.PI / 180; // 61 degrees

// Is the front of this 3D text shape facing the camera?
function isShapeFacingCamera(
  shape: ShapeData,
  cameraRotX: number,
  cameraRotY: number
): boolean {
  const [camX, camY, camZ] = getCameraPosition(cameraRotX, cameraRotY, CAMERA_DISTANCE);

  const [sx, sy, sz] = shape.position;
  const toCamera = normalize([camX - sx, camY - sy, camZ - sz]);

  // In object space assume the glyph's front faces +Z
  const baseFront: Vec3 = [0, 0, 1];
  const frontWorld = normalize(applyEulerRotation(baseFront, shape.rotation as Vec3));

  const cosAngle = dot(frontWorld, toCamera);
  const angle = Math.acos(Math.max(-1, Math.min(1, cosAngle)));

  return (angle <= FACING_ANGLE_THRESHOLD || (Math.PI - angle) <= FACING_ANGLE_THRESHOLD);
}

function generateMaskSceneForShape(
  shape: ShapeData,
  cameraRotX: number = 0,
  cameraRotY: number = 0
): string {
  const [camX, camY, camZ] = getCameraPosition(cameraRotX, cameraRotY, CAMERA_DISTANCE);

  const text = shape.params.text || '?';
  const fontSize = (shape.params.fontSize || 1) * shape.scale;
  const depth = (shape.params.textDepth || 0.3) * shape.scale;

  const rotX = shape.rotation[0] * 180 / Math.PI;
  const rotY = shape.rotation[1] * 180 / Math.PI;
  const rotZ = shape.rotation[2] * 180 / Math.PI;

  return `
// POV-Ray mask scene for single glyph
#version 3.7;
global_settings { assumed_gamma 1.0 }

// Camera: same as normal render
camera {
  orthographic
  location <${camX.toFixed(2)}, ${camY.toFixed(2)}, ${camZ.toFixed(2)}>
  look_at <0, 0, 0>
  sky <0, 1, 0>
  angle 60
}

// Pure black background
background { color rgb <0, 0, 0> }

// No lights needed if we use ambient 1
// Single white glyph, no shading
text {
  ttf "crystal.ttf" "${text}" ${depth.toFixed(2)}, 0
  pigment { color rgb <1, 1, 1> }
  finish {
    ambient 1
    diffuse 0
  }
  scale ${fontSize.toFixed(2)}
  rotate <${rotX.toFixed(2)}, ${rotY.toFixed(2)}, ${rotZ.toFixed(2)}>
  translate <${shape.position[0].toFixed(2)}, ${shape.position[1].toFixed(2)}, ${shape.position[2].toFixed(2)}>
}
`;
}

// Render a single-character mask image (white glyph on black background)
export async function renderCharacterMask(
  sessionId: string,
  shape: ShapeData,
  cameraRotX: number,
  cameraRotY: number
): Promise<Buffer> {
  // const tempDir = path.join(process.cwd(), 'temp', sessionId);
  const tempDir = path.join('/dev/shm/YOLO_attacker', 'temp', sessionId);
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }

  const angleKey = getAngleKey(cameraRotX, cameraRotY);
  const safeId = shape.id.replace(/[^a-zA-Z0-9_-]/g, '_');

  const povBase = `${sessionId}_${safeId}_${angleKey}_mask.pov`;
  const pngBase = `${sessionId}_${safeId}_${angleKey}_mask.png`;
  const povFile = path.join(tempDir, povBase);
  const pngFile = path.join(tempDir, pngBase);

  const scene = generateMaskSceneForShape(shape, cameraRotX, cameraRotY);
  await writeFileAsync(povFile, scene);

  // For a mask, disable antialiasing to keep edges crisp: -A
  const povrayCmd = `povray +I"${povBase}" +O"${pngBase}" +W${IMAGE_SIZE} +H${IMAGE_SIZE} +Q9 -D -A 2>&1`;

  try {
    const { stdout, stderr } = await execAsync(povrayCmd, { timeout: 30000, cwd: tempDir });
    if (stderr) console.error('[mask] POV-Ray stderr:', stderr);
  } catch (error: any) {
    console.error('POV-Ray mask rendering failed:', error.message);
    if (error.stderr) console.error('POV-Ray stderr:\n', error.stderr);
    throw new Error('POV-Ray mask rendering failed');
  }

  const imageBuffer = await readFileAsync(pngFile);

  // await unlinkAsync(povFile).catch(() => {});
  // await unlinkAsync(pngFile).catch(() => {});

  return imageBuffer;
}

// POV-Ray scene generation
function generatePovScene(shapes: ShapeData[], cameraRotX: number = 0, cameraRotY: number = 0): string {
  // Calculate camera position based on rotation
  const [camX, camY, camZ] = getCameraPosition(cameraRotX, cameraRotY, CAMERA_DISTANCE);

  let scene = `
// POV-Ray Scene for 3D Captcha
#version 3.7;
global_settings { assumed_gamma 1.0 }

// Camera
camera {
  orthographic
  location <${camX.toFixed(2)}, ${camY.toFixed(2)}, ${camZ.toFixed(2)}>
  look_at <0, 0, 0>
  sky <0, 1, 0>
  angle 60
}

// Background
background { color rgb <0.1, 0.1, 0.18> }

// Two lights for 3D depth while keeping good performance
light_source { <10, 15, 20> color rgb <1, 1, 1> shadowless }
light_source { <-10, 5, -10> color rgb <0.3, 0.3, 0.3> shadowless }

`;

  // Add each 3D text glyph
  shapes.forEach((shape, index) => {
    const text = shape.params.text || '?';
    const [r, g, b] = hexToRgb(shape.color);
    const fontSize = (shape.params.fontSize || 1) * shape.scale;
    const depth = (shape.params.textDepth || 0.3) * shape.scale;

    // Add each 3D text glyph
    const rotX = shape.rotation[0] * 180 / Math.PI;
    const rotY = shape.rotation[1] * 180 / Math.PI;
    const rotZ = shape.rotation[2] * 180 / Math.PI;

    scene += `
// Shape ${index + 1}: "${text}"
text {
  ttf "crystal.ttf" "${text}" ${depth.toFixed(2)}, 0
  pigment { color rgb <${r.toFixed(3)}, ${g.toFixed(3)}, ${b.toFixed(3)}> }
  finish {
    ambient 0.4
    diffuse 0.6
  }
  scale ${fontSize.toFixed(2)}
  rotate <${rotX.toFixed(2)}, ${rotY.toFixed(2)}, ${rotZ.toFixed(2)}>
  translate <${shape.position[0].toFixed(2)}, ${shape.position[1].toFixed(2)}, ${shape.position[2].toFixed(2)}>
}
`;
  });

  return scene;
}

async function calculateClickRegionsFromMasks(
  sessionId: string,
  shapes: ShapeData[],
  cameraRotX: number = 0,
  cameraRotY: number = 0
): Promise<ClickRegion[]> {
  // How much of a shape’s mask must be covered by nearer shapes to consider it invisible
  const OCCLUSION_THRESHOLD = 0.1;

  type ShapeMaskInfo = {
    shape: ShapeData;
    id: string;
    depth: number;
    facing: boolean;
    width: number;
    height: number;
    data: Buffer; // RGBA
    bbox: { x: number; y: number; w: number; h: number } | null;
    area: number; // total non-black pixels in mask
  };

  const shapeMasks: ShapeMaskInfo[] = [];

  // Camera position + forward vector
  const [camX, camY, camZ] = getCameraPosition(cameraRotX, cameraRotY, CAMERA_DISTANCE);
  const camPos: Vec3 = [camX, camY, camZ];
  const lookAt: Vec3 = [0, 0, 0];
  const forward = normalize([
    lookAt[0] - camPos[0],
    lookAt[1] - camPos[1],
    lookAt[2] - camPos[2],
  ]);

  // Build mask + bbox + depth info for every shape
  for (const shape of shapes) {
    const maskBuf = await renderCharacterMask(sessionId, shape, cameraRotX, cameraRotY);
    const png = PNG.sync.read(maskBuf);
    const { width, height, data } = png;

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    let area = 0;

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * width + x) * 4;
        const r = data[idx], g = data[idx + 1], b = data[idx + 2];
        if (r || g || b) {
          area++;
          if (x < minX) minX = x;
          if (x > maxX) maxX = x;
          if (y < minY) minY = y;
          if (y > maxY) maxY = y;
        }
      }
    }

    let bbox: { x: number; y: number; w: number; h: number } | null = null;
    if (Number.isFinite(minX)) {
      bbox = {
        x: minX,
        y: minY,
        w: maxX - minX + 1,
        h: maxY - minY + 1,
      };
    }

    // Depth along camera forward vector
    const [sx, sy, sz] = shape.position;
    const toPoint: Vec3 = [sx - camPos[0], sy - camPos[1], sz - camPos[2]];
    const depth = dot(toPoint, forward); // larger = further away along view dir

    const facing = isShapeFacingCamera(shape, cameraRotX, cameraRotY);

    shapeMasks.push({
      shape,
      id: shape.id,
      depth,
      facing,
      width,
      height,
      data,
      bbox,
      area,
    });
  }

  // For each candidate shape, compute occlusion by all nearer shapes
  const regions: ClickRegion[] = [];

  for (const sm of shapeMasks) {
    // Only shapes that are facing (front or back) and have a mask
    if (!sm.facing) continue;
    if (!sm.bbox) continue;
    if (sm.area === 0) continue;

    // All shapes closer to camera that have any mask pixels act as occluders,
    // even if they themselves won't get a bbox
    const occluders = shapeMasks.filter(
      o => o !== sm && o.area > 0 && o.depth < sm.depth
    );

    if (occluders.length === 0) {
      // Nothing in front, we keep this bbox
      regions.push({
        id: sm.id,
        x: sm.bbox.x,
        y: sm.bbox.y,
        width: sm.bbox.w,
        height: sm.bbox.h,
      });
      continue;
    }

    let occludedPixels = 0;

    // Assume all masks share the same resolution (IMAGE_SIZE x IMAGE_SIZE)
    const { width, height, data } = sm;

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * width + x) * 4;
        const r = data[idx], g = data[idx + 1], b = data[idx + 2];

        // Not part of this shape
        if (!(r || g || b)) continue;

        // Check if any nearer shape covers this pixel
        let covered = false;
        for (const occ of occluders) {
          const or = occ.data[idx];
          const og = occ.data[idx + 1];
          const ob = occ.data[idx + 2];
          if (or || og || ob) {
            covered = true;
            break;
          }
        }

        if (covered) {
          occludedPixels++;
        }
      }
    }

    const occlusionRatio = occludedPixels / sm.area;

    // If most of this shape's visible pixels are covered by nearer shapes, drop it
    if (occlusionRatio >= OCCLUSION_THRESHOLD) {
      continue;
    }

    // Otherwise, keep its bbox
    regions.push({
      id: sm.id,
      x: sm.bbox.x,
      y: sm.bbox.y,
      width: sm.bbox.w,
      height: sm.bbox.h,
    });
  }

  return regions;
}


// Rendering helpers
async function renderSingleImage(sessionId: string, shapes: ShapeData[], rotX: number, rotY: number): Promise<Buffer> {
  const tempDir = path.join('/dev/shm/YOLO_attacker', 'temp', sessionId);
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }
  const angleKey = getAngleKey(rotX, rotY);
  const povBase = `${sessionId}_${angleKey}.pov`;
  const pngBase = `${sessionId}_${angleKey}.png`;
  const povFile = path.join(tempDir, povBase);
  const pngFile = path.join(tempDir, pngBase);

  const scene = generatePovScene(shapes, rotX, rotY);
  await writeFileAsync(povFile, scene);

  const povrayCmd = `povray +I"${povBase}" +O"${pngBase}" +W400 +H400 +Q9 -D +A0.3 2>&1`;
    
  try {
    await execAsync(povrayCmd, { timeout: 30000, cwd: tempDir }); // make POV-Ray’s working dir the temp dir
  } catch (error: any) {
    console.error('POV-Ray rendering failed:', error.message);
    if (error.stdout) console.error('POV-Ray stdout:\n', error.stdout);
    if (error.stderr) console.error('POV-Ray stderr:\n', error.stderr);
    throw new Error('POV-Ray rendering failed');
  }

  const imageBuffer = await readFileAsync(pngFile);

  // await unlinkAsync(povFile).catch(() => {});
  // await unlinkAsync(pngFile).catch(() => {});

  return imageBuffer;
}

// Public API

// Render a captcha scene at a given camera rotation, with caching + neighbour pre-rendering
// clickRegions are PER-VIEW and include ONLY "front-facing" characters
export async function renderCaptchaScene(sessionId: string, shapes: ShapeData[], cameraRotX: number = 0, cameraRotY: number = 0): Promise<RenderResult> {
  // Ensure session cache exists
  if (!imageCache.has(sessionId)) {
    imageCache.set(sessionId, new Map());
  }
  const sessionCache = imageCache.get(sessionId)!;

  const angleKey = getAngleKey(cameraRotX, cameraRotY);

  // Cache lookup
  let imageBuffer: Buffer;
  if (sessionCache.has(angleKey)) {
    imageBuffer = sessionCache.get(angleKey)!;
  } else {
    imageBuffer = await renderSingleImage(sessionId, shapes, cameraRotX, cameraRotY);
    sessionCache.set(angleKey, imageBuffer);
  }

  // View-dependent click regions
  // const clickRegions = calculateClickRegions(shapes, cameraRotX, cameraRotY, IMAGE_SIZE);
  const clickRegions = await calculateClickRegionsFromMasks(
    sessionId,
    shapes,
    cameraRotX,
    cameraRotY
  );

  return { imageBuffer, clickRegions };
}

// Drop all cached images for a given session
export function deleteStoredImage(sessionId: string): void {
  imageCache.delete(sessionId);
}

// Remove image cache entries for sessions that no longer exist
export function cleanupExpiredImages(validSessionIds: Set<string>): void {
  for (const sessionId of imageCache.keys()) {
    if (!validSessionIds.has(sessionId)) {
      imageCache.delete(sessionId);
    }
  }
}

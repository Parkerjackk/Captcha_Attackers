// Backend type definitions
export type ShapeType = 'text3D';  // Only use 3D icon characters

// Shape parameters
export interface ShapeParams {
  // Vertex data of random shapes
  vertices?: number[];       // Vertex coordinates [x1,y1,z1, x2,y2,z2, ...]
  indices?: number[];        // Triangle indices

  // Random parameters (used for generation algorithms)
  seed?: number;             // Random seed (for reproducing the same shape)
  complexity?: number;       // Complexity (number of vertices)
  roughness?: number;        // Roughness
  spikiness?: number;        // Spikiness
  irregularity?: number;     // Irregularity
  noiseScale?: number;       // Noise scale
  noiseStrength?: number;    // Noise strength

  // Deformation parameters
  deformationType?: string;  // Deformation type
  deformationAmount?: number; // Amount of deformation

  // 3D text parameters
  text?: string;             // Text content
  fontSize?: number;         // Font size
  textDepth?: number;        // Text thickness
  bevelEnabled?: boolean;    // Whether bevel is enabled
}

export interface ShapeData {
  id: string;
  type: ShapeType;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: number;
  color: string;
  params: ShapeParams;
}

export interface CaptchaSession {
  sessionId: string;
  shapes: ShapeData[];
  correctAnswer?: string;
  createdAt: Date;
}

export interface VerifyRequest {
  sessionId: string;
  userInput: string;
  fingerprint?: string;  // Browser fingerprint
}

export interface VerifyResponse {
  success: boolean;
  message: string;
}

// Click region (for image captcha)
export interface ClickRegion {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

// Client session response (excluding sensitive information)
export interface ClientCaptchaSession {
  sessionId: string;
  clickRegions: ClickRegion[];
  initialRotX: number;
  initialRotY: number;
}

// Block record (IP or fingerprint)
export interface BlockRecord {
  identifier: string;           // IP address or fingerprint hash
  type: 'ip' | 'fingerprint';   // Type of identifier
  failures: number;
  blocked_at: number | null;    // Timestamp when blocked (NULL = not blocked)
  first_seen: number;           // First appearance timestamp
  last_seen: number;            // Last activity timestamp
}

// Verification log entry
export interface VerificationLog {
  id?: number;
  ip: string;
  fingerprint: string | null;
  session_id: string;
  user_input: string;
  success: boolean;             // Whether verification succeeded
  timestamp: number;            // Request timestamp
  user_agent?: string;          // User-Agent header
}

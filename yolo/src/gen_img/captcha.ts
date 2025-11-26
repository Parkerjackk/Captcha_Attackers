// 后端类型定义（与前端保持一致）
export type ShapeType = 'text3D';  // 只使用3D图标字符

// 形状参数（用于创建更复杂和独特的形状）
export interface ShapeParams {
  // 随机形状的顶点数据（存储完整的几何体信息）
  vertices?: number[];       // 顶点坐标 [x1,y1,z1, x2,y2,z2, ...]
  indices?: number[];        // 三角形索引

  // 随机参数（用于生成算法）
  seed?: number;             // 随机种子（用于重现相同形状）
  complexity?: number;       // 复杂度（顶点数量）
  roughness?: number;        // 粗糙度
  spikiness?: number;        // 尖刺程度
  irregularity?: number;     // 不规则程度
  noiseScale?: number;       // 噪声缩放
  noiseStrength?: number;    // 噪声强度

  // 变形参数
  deformationType?: string;  // 变形类型
  deformationAmount?: number; // 变形量

  // 3D文字参数
  text?: string;             // 文字内容
  fontSize?: number;         // 字体大小
  textDepth?: number;        // 文字厚度
  bevelEnabled?: boolean;    // 是否启用倒角
}

export interface ShapeData {
  id: string;
  type: ShapeType;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: number;
  color: string;
  params: ShapeParams;  // 新增：形状参数
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

// 点击区域（用于图片验证码）
export interface ClickRegion {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

// 客户端会话响应（不包含敏感信息）
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

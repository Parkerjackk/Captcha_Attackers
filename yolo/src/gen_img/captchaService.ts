import { v4 as uuidv4 } from 'uuid';
import { ShapeType, ShapeData, ShapeParams, CaptchaSession } from './captcha.js';

// Session storage (should use Redis or database in production)
const sessions = new Map<string, CaptchaSession>();

// Characters for captcha (avoid confusing chars like 0/O, 1/I/l, 6/9, 7/L)
const CAPTCHA_CHARS = [
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
  '2', '3', '4', '5', '8',
  '@', '#', '$', '%', '&', '*', '+', '='
];

// Available colors
const COLORS = [
  '#FF6B6B', // Red
  '#4ECDC4', // Cyan
  '#45B7D1', // Blue
  '#FFA07A', // Orange
  '#98D8C8', // Mint green
  '#F7DC6F', // Yellow
  '#BB8FCE', // Purple
  '#85C1E2', // Sky blue
];

// Balanced character bank for dataset training
// supports 36 / 4 = 9 sessions where each char appears once
let charBank: string[] = [];
let bankIndex = 0;

// Track how often each char has been chosen as the answer
const answerCounts = new Map<string, number>(
  CAPTCHA_CHARS.map(ch => [ch, 0])
);

// Shuffle
function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// Get N unique chars for a session from global bank
function getUniqueCharsFromBank(count: number): string[] {
  if (charBank.length === 0 || bankIndex + count > charBank.length) {
    charBank = shuffle(CAPTCHA_CHARS);
    bankIndex = 0;
  }
  const result = charBank.slice(bankIndex, bankIndex + count);
  bankIndex += count;
  return result;
}

// Choose answer char among given chars
function pickBalancedAnswer(chars: string[]): string {
  let minCount = Infinity;
  let candidates: string[] = [];
  for (const ch of chars) {
    const c = answerCounts.get(ch) ?? 0;
    if (c < minCount) {
      minCount = c;
      candidates = [ch];
    } else if (c === minCount) {
      candidates.push(ch);
    }
  }
  const answer = randomElement(candidates);
  answerCounts.set(answer, (answerCounts.get(answer) ?? 0) + 1);
  return answer;
}

// Generate a random number in range
function randomInRange(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

// Randomly select an element from an array
function randomElement<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}

// Generate captcha with one repeated character
function generateCaptchaWithDuplicate(): { chars: string[], answer: string } {
  const numChars = 5; // Total characters to show
  
  const uniqueChars = getUniqueCharsFromBank(numChars - 1); // Get 4 unique chars
  const answer = pickBalancedAnswer(uniqueChars); // Pick duplicated answer
  const chars = shuffle([...uniqueChars, answer]); // Build and shuffle the final chars

  return { chars, answer };
}

// Create a new CAPTCHA session
export function createCaptchaSession(): CaptchaSession {
  const sessionId = uuidv4();
  const { chars, answer } = generateCaptchaWithDuplicate();
  const shapes: ShapeData[] = [];

  // Create a shape for each character, arranged horizontally
  const spacing = 3; // spacing between characters
  const startX = -((chars.length - 1) * spacing) / 2;

  // Same as camera so that there is a guarantee a character will face the camera in at least one view
  const CAMERA_ANGLES: Array<{ rotX: number; rotY: number }> = [];
  for (let rx = -85; rx <= 85; rx += 5) {
    for (let ry = -85; ry <= 85; ry += 5) {
      CAMERA_ANGLES.push({ rotX: rx, rotY: ry });
    }
  }

  // Convert degrees to radians
  const degToRad = (deg: number) => (deg * Math.PI) / 180;
  const shuffledAngles = [...CAMERA_ANGLES].sort(() => Math.random() - 0.5);
  chars.forEach((char, index) => {
    const homeAngle = shuffledAngles[index];;
    const rotXShape = -degToRad(homeAngle.rotX);
    let rotYShape =  degToRad(homeAngle.rotY);
    // 50% chance of being backwards
    if (Math.random() < 0.5) {
      rotYShape += Math.PI;
    }

    const shape: ShapeData = {
      id: uuidv4(),
      type: 'text3D',
      position: [
        startX + index * spacing,
        randomInRange(-0.5, 0.5),
        randomInRange(-1, 1)
      ],
      rotation: [
        rotXShape,
        rotYShape,
        0
      ],
      scale: randomInRange(1.2, 1.8),
      color: randomElement(COLORS),
      params: {
        text: char,
        fontSize: 1.5,
        textDepth: 0.4
      }
    };

    shapes.push(shape);
  });

  const session: CaptchaSession = {
    sessionId,
    shapes,
    correctAnswer: answer,
    createdAt: new Date()
  };

  console.log('=== CAPTCHA DEBUG ===');
  console.log('Chars:', chars.join(' '));
  console.log('Answer:', answer);
  console.log('====================');

  sessions.set(sessionId, session);
  // cleanupExpiredSessions();

  return session;
}

// Verify user input
export function verifyCaptcha(sessionId: string, userInput: string): { success: boolean; message: string } {
  const session = sessions.get(sessionId);

  if (!session) {
    return {
      success: false,
      message: 'Session expired, please refresh'
    };
  }

  // Case-insensitive comparison
  const isCorrect = userInput.toUpperCase() === session.correctAnswer?.toUpperCase();

  console.log('=== VERIFY DEBUG ===');
  console.log('User input:', userInput.toUpperCase());
  console.log('Correct answer:', session.correctAnswer?.toUpperCase());
  console.log('Result:', isCorrect ? 'SUCCESS' : 'FAILED');
  console.log('====================');

  if (isCorrect) {
    sessions.delete(sessionId);
    return {
      success: true,
      message: 'Verification successful'
    };
  } else {
    return {
      success: false,
      message: 'Incorrect, please try again'
    };
  }
}

function cleanupExpiredSessions() {
  const now = new Date();
  const expirationTime = 10 * 60 * 1000;

  for (const [sessionId, session] of sessions.entries()) {
    if (now.getTime() - session.createdAt.getTime() > expirationTime) {
      sessions.delete(sessionId);
    }
  }
}

// Get session by ID
export function getSession(sessionId: string): CaptchaSession | undefined {
  return sessions.get(sessionId);
}

export function getSessionStats() {
  return {
    activeSessions: sessions.size
  };
}

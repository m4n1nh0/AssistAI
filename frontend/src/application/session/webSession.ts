const USER_ID_KEY = "assistai.web.user_id";
const CONVERSATION_ID_KEY = "assistai.web.conversation_id";

export interface WebSession {
  userId: string;
  conversationId: string;
}

export function getWebSession(): WebSession {
  return {
    userId: getOrCreateId(USER_ID_KEY, "web-user"),
    conversationId: getOrCreateId(CONVERSATION_ID_KEY, "chat")
  };
}

export function createRequestId(): string {
  return `req-web-${randomId()}`;
}

function getOrCreateId(storageKey: string, prefix: string): string {
  const existing = window.localStorage.getItem(storageKey);
  if (existing) {
    return existing;
  }

  const value = `${prefix}-${randomId()}`;
  window.localStorage.setItem(storageKey, value);
  return value;
}

function randomId(): string {
  if (window.crypto?.randomUUID) {
    return window.crypto.randomUUID().slice(0, 12);
  }

  return Math.random().toString(36).slice(2, 14);
}

export const appConfig = {
  apiUrl: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  webUserId: import.meta.env.VITE_WEB_USER_ID ?? "web-user-001"
} as const;

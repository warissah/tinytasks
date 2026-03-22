export type GuestUser = {
  user_id: string;
  email: string;
  phone: string;
  persistence: "mongo" | "demo_fallback";
};

const KEY_ID = "guest_user_id";
const KEY_EMAIL = "guest_user_email";
const KEY_PHONE = "guest_user_phone";
const KEY_PERSISTENCE = "guest_user_persistence";

function hasStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function getStoredGuestUser(): GuestUser | null {
  if (!hasStorage()) return null;
  const user_id = window.localStorage.getItem(KEY_ID);
  if (!user_id) return null;
  return {
    user_id,
    email: window.localStorage.getItem(KEY_EMAIL) ?? "",
    phone: window.localStorage.getItem(KEY_PHONE) ?? "",
    persistence:
      (window.localStorage.getItem(KEY_PERSISTENCE) as GuestUser["persistence"] | null) ??
      "mongo",
  };
}

export function storeGuestUser(user: GuestUser): void {
  if (!hasStorage()) return;
  window.localStorage.setItem(KEY_ID, user.user_id);
  window.localStorage.setItem(KEY_EMAIL, user.email);
  window.localStorage.setItem(KEY_PHONE, user.phone);
  window.localStorage.setItem(KEY_PERSISTENCE, user.persistence);
}


export function clearStoredGuestUser(): void {
  if (!hasStorage()) return;
  window.localStorage.removeItem(KEY_ID);
  window.localStorage.removeItem(KEY_EMAIL);
  window.localStorage.removeItem(KEY_PHONE);
  window.localStorage.removeItem(KEY_PERSISTENCE);
}

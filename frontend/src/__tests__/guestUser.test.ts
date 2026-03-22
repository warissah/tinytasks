import { beforeEach, describe, expect, it } from "vitest";

import { clearStoredGuestUser, getStoredGuestUser, storeGuestUser } from "../utils/guestUser";

describe("guestUser storage", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("stores and reads the guest user bundle", () => {
    storeGuestUser({
      user_id: "guest-123",
      email: "user@example.com",
      phone: "+15551234567",
      persistence: "mongo",
    });

    expect(getStoredGuestUser()).toEqual({
      user_id: "guest-123",
      email: "user@example.com",
      phone: "+15551234567",
      persistence: "mongo",
    });
  });

  it("clears the stored guest user bundle", () => {
    storeGuestUser({
      user_id: "guest-123",
      email: "user@example.com",
      phone: "+15551234567",
      persistence: "mongo",
    });

    clearStoredGuestUser();

    expect(getStoredGuestUser()).toBeNull();
  });
});

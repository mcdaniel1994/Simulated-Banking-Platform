import { apiRequest } from "./client";
import { ApiError } from "./errors";

describe("apiRequest", () => {
  it("sends credentials and the readable CSRF token on unsafe requests", async () => {
    document.cookie = "csrf_token=test-csrf; Path=/";
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response(null, { status: 204 }));

    await apiRequest<void>("/api/auth/logout", { method: "POST" });

    const init = fetchMock.mock.calls[0][1]!;
    expect(init.credentials).toBe("include");
    expect(new Headers(init.headers).get("X-CSRF-Token")).toBe("test-csrf");
  });

  it("maps the stable backend envelope into an ApiError", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      Response.json(
        {
          error: {
            code: "INSUFFICIENT_FUNDS",
            message: "Insufficient funds",
            fields: { amount: "Too large" },
          },
        },
        { status: 409 },
      ),
    );

    await expect(apiRequest("/api/example")).rejects.toEqual(
      new ApiError(409, "INSUFFICIENT_FUNDS", "Insufficient funds", {
        amount: "Too large",
      }),
    );
  });
});

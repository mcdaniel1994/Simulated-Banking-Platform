import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

import { AuthProvider } from "./AuthContext";
import { AppRoutes } from "../../routes/AppRoutes";

function renderApp(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe("authentication flow", () => {
  it("redirects an anonymous protected route and validates login", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      Response.json(
        {
          error: {
            code: "UNAUTHENTICATED",
            message: "Authentication required",
            fields: {},
          },
        },
        { status: 401 },
      ),
    );
    renderApp("/dashboard");
    expect(
      await screen.findByRole("heading", { name: "Log in" }),
    ).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(
      screen.getByText("Enter a valid email address."),
    ).toBeInTheDocument();
    expect(screen.getByText("Enter your password.")).toBeInTheDocument();
  });

  it("renders customer navigation from the SQL-backed current user", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        Response.json({
          id: 2,
          email: "alex.customer@demo.bank.test",
          first_name: "Alex",
          last_name: "Carter",
          role: "CUSTOMER",
          is_active: true,
        }),
      )
      .mockResolvedValueOnce(Response.json([]));
    renderApp("/dashboard");
    expect(
      await screen.findByText("No accounts are available."),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Accounts" })).toBeInTheDocument();
    await waitFor(() =>
      expect(
        screen.queryByRole("link", { name: "Admin" }),
      ).not.toBeInTheDocument(),
    );
  });

  it("opens and closes the accessible mobile navigation", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        Response.json({
          id: 2,
          email: "alex.customer@demo.bank.test",
          first_name: "Alex",
          last_name: "Carter",
          role: "CUSTOMER",
          is_active: true,
        }),
      )
      .mockResolvedValueOnce(Response.json([]));
    renderApp("/dashboard");
    await screen.findByText("No accounts are available.");

    const menuButton = screen.getByRole("button", {
      name: "Open navigation menu",
    });
    await userEvent.click(menuButton);
    expect(menuButton).toHaveAttribute("aria-expanded", "true");
    expect(
      screen.getByRole("navigation", {
        name: "Mobile primary navigation",
      }),
    ).toBeInTheDocument();

    await userEvent.keyboard("{Escape}");
    expect(menuButton).toHaveAttribute("aria-expanded", "false");
    expect(menuButton).toHaveFocus();
  });

  it("shows the backend's safe generic login failure", async () => {
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        Response.json(
          {
            error: {
              code: "UNAUTHENTICATED",
              message: "Authentication required",
              fields: {},
            },
          },
          { status: 401 },
        ),
      )
      .mockResolvedValueOnce(
        Response.json(
          {
            error: {
              code: "UNAUTHENTICATED",
              message: "Invalid email or password",
              fields: {},
            },
          },
          { status: 401 },
        ),
      );
    renderApp("/login");
    await screen.findByRole("heading", { name: "Log in" });
    await userEvent.type(
      screen.getByLabelText("Email"),
      "alex.customer@demo.bank.test",
    );
    await userEvent.type(screen.getByLabelText("Password"), "wrong");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(
      await screen.findByText("Invalid email or password"),
    ).toBeInTheDocument();
  });
});

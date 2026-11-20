import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthForm } from "@/components/AuthForm";
import { ApiError } from "@/lib/http";

const push = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push, refresh: vi.fn() }) }));
vi.mock("next/link", () => ({ default: ({ href, children }: { href: string; children: React.ReactNode }) => <a href={href}>{children}</a> }));

const login = vi.fn();
const register = vi.fn();
const availability = vi.fn();
vi.mock("@/lib/api", () => ({
  api: { auth: { login: (...a: unknown[]) => login(...a), register: (...a: unknown[]) => register(...a), availability: (...a: unknown[]) => availability(...a) } },
}));

const user = { id: "u1", full_name: "Ann", username: "ann", email: "ann@x.com", avatar_url: null };
const token = `h.${btoa(JSON.stringify({ sub: "u1", role: "member", exp: 9999999999 }))}.s`;

beforeEach(() => {
  vi.clearAllMocks();
  document.cookie = "kanban_token=; Max-Age=0; Path=/";
});

describe("AuthForm", () => {
  it("renders the login fields without a name field", () => {
    render(<AuthForm mode="login" />);
    expect(screen.getByLabelText("Username or email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.queryByLabelText("Full name")).toBeNull();
  });

  it("renders the register fields", () => {
    render(<AuthForm mode="register" />);
    expect(screen.getByLabelText("Full name")).toBeInTheDocument();
  });

  it("submits identifier and password, stores the token and goes to the boards", async () => {
    login.mockResolvedValue({ user, token });
    render(<AuthForm mode="login" />);
    await userEvent.type(screen.getByLabelText("Username or email"), "ann@x.com");
    await userEvent.type(screen.getByLabelText("Password"), "secret-pass");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/boards"));
    expect(login).toHaveBeenCalledWith({ identifier: "ann@x.com", password: "secret-pass" });
    expect(document.cookie).toContain("kanban_token=");
  });

  it("shows a server error message", async () => {
    login.mockRejectedValue(new ApiError(401, "UNAUTHORIZED", "Invalid credentials"));
    render(<AuthForm mode="login" />);
    await userEvent.type(screen.getByLabelText("Username or email"), "abc");
    await userEvent.type(screen.getByLabelText("Password"), "b");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid username, email or password.");
    expect(push).not.toHaveBeenCalled();
  });

  it("maps validation details onto the fields", async () => {
    register.mockRejectedValue(
      new ApiError(400, "VALIDATION_ERROR", "Validation failed", { password: ["password must be at least 8 characters"] }),
    );
    render(<AuthForm mode="register" />);
    await userEvent.type(screen.getByLabelText("Full name"), "Ann");
    await userEvent.type(screen.getByLabelText("Username"), "ann");
    await userEvent.type(screen.getByLabelText("Email"), "ann@x.com");
    await userEvent.type(screen.getByLabelText("Password"), "short");
    await userEvent.click(screen.getByRole("button", { name: "Register" }));
    expect(await screen.findByText("password must be at least 8 characters")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toHaveAttribute("aria-invalid", "true");
  });

  it("sends no request for an identifier that is neither a username nor an email", async () => {
    render(<AuthForm mode="login" />);
    await userEvent.type(screen.getByLabelText("Username or email"), "not valid");
    await userEvent.type(screen.getByLabelText("Password"), "secret-pass");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByText("Enter a valid username or email.")).toBeInTheDocument();
    await userEvent.clear(screen.getByLabelText("Username or email"));
    await userEvent.type(screen.getByLabelText("Username or email"), "a@b");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByText("Enter a valid email address.")).toBeInTheDocument();
    expect(login).not.toHaveBeenCalled();
  });

  it("shows a countdown and disables the button after a 429", async () => {
    login.mockRejectedValue(new ApiError(429, "RATE_LIMITED", "Too many attempts", undefined, 90));
    render(<AuthForm mode="login" />);
    await userEvent.type(screen.getByLabelText("Username or email"), "ann");
    await userEvent.type(screen.getByLabelText("Password"), "secret-pass");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByText(/Try again in 01:30/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Log in" })).toBeDisabled();
  });

  it("checks availability on blur and shows the taken message", async () => {
    availability.mockResolvedValue({ username: { available: false } });
    render(<AuthForm mode="register" />);
    await userEvent.type(screen.getByLabelText("Username"), "ann");
    await userEvent.tab();
    expect(await screen.findByText("This username is already taken.")).toBeInTheDocument();
  });

  it("stays silent when the availability check is rate limited", async () => {
    availability.mockRejectedValue(new ApiError(429, "RATE_LIMITED", "Too many", undefined, 30));
    render(<AuthForm mode="register" />);
    await userEvent.type(screen.getByLabelText("Username"), "ann");
    await userEvent.tab();
    await waitFor(() => expect(availability).toHaveBeenCalled());
    expect(screen.queryByRole("alert")).toBeNull();
  });
});

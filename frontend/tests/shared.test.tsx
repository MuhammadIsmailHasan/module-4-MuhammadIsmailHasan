import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { BaseBadge } from "@/components/shared/BaseBadge";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseModal } from "@/components/shared/BaseModal";

describe("BaseButton", () => {
  it("renders a type=button by default and fires onClick", async () => {
    const onClick = vi.fn();
    render(<BaseButton onClick={onClick}>Save</BaseButton>);
    const btn = screen.getByRole("button", { name: "Save" });
    expect(btn).toHaveAttribute("type", "button");
    await userEvent.click(btn);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("applies variant and size classes and honours disabled", async () => {
    const onClick = vi.fn();
    render(
      <BaseButton variant="danger" size="sm" disabled onClick={onClick}>
        Delete
      </BaseButton>,
    );
    const btn = screen.getByRole("button", { name: "Delete" });
    expect(btn).toBeDisabled();
    expect(btn).toHaveAttribute("data-variant", "danger");
    await userEvent.click(btn);
    expect(onClick).not.toHaveBeenCalled();
  });
});

describe("BaseBadge", () => {
  it("renders its text and exposes its tone", () => {
    render(<BaseBadge tone="red">High</BaseBadge>);
    expect(screen.getByText("High")).toHaveAttribute("data-tone", "red");
  });

  it("defaults to the neutral tone", () => {
    render(<BaseBadge>Plain</BaseBadge>);
    expect(screen.getByText("Plain")).toHaveAttribute("data-tone", "neutral");
  });
});

describe("BaseModal", () => {
  it("renders nothing when closed", () => {
    render(
      <BaseModal open={false} title="T" onClose={() => {}}>
        body
      </BaseModal>,
    );
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("is a labelled dialog and closes on Escape and on the close button", async () => {
    const onClose = vi.fn();
    render(
      <BaseModal open title="Card" onClose={onClose}>
        <p>body</p>
      </BaseModal>,
    );
    const dialog = screen.getByRole("dialog", { name: "Card" });
    expect(dialog).toBeInTheDocument();
    expect(screen.getByText("body")).toBeInTheDocument();
    await userEvent.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalledTimes(1);
    await userEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(onClose).toHaveBeenCalledTimes(2);
  });
});

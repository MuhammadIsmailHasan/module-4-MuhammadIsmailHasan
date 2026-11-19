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
    expect(btn).toHaveClass("btn-danger", "btn-sm");
    await userEvent.click(btn);
    expect(onClick).not.toHaveBeenCalled();
  });
});

describe("BaseBadge", () => {
  it("renders its text with the tone class", () => {
    render(<BaseBadge tone="red">High</BaseBadge>);
    expect(screen.getByText("High")).toHaveClass("badge", "badge-red");
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

  it("is a labelled dialog and closes on Escape, the close button and the overlay", async () => {
    const onClose = vi.fn();
    const { container } = render(
      <BaseModal open title="Card" onClose={onClose}>
        <p>body</p>
      </BaseModal>,
    );
    const dialog = screen.getByRole("dialog", { name: "Card" });
    expect(dialog).toHaveAttribute("aria-modal", "true");
    await userEvent.keyboard("{Escape}");
    await userEvent.click(screen.getByRole("button", { name: "Close" }));
    await userEvent.click(container.querySelector(".modal-overlay") as HTMLElement);
    expect(onClose).toHaveBeenCalledTimes(3);
  });
});

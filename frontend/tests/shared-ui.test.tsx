import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseCombobox } from "@/components/shared/BaseCombobox";
import { BaseConfirm } from "@/components/shared/BaseConfirm";
import { BaseTooltip } from "@/components/shared/BaseTooltip";

const opts = (n: number) => Array.from({ length: n }, (_, i) => ({ value: `v${i}`, label: `Option ${i}` }));

function Harness({ n }: { n: number }) {
  const [v, setV] = useState("");
  return (
    <>
      <BaseCombobox label="Choice" options={opts(n)} value={v} onChange={setV} />
      <output aria-label="value">{v}</output>
    </>
  );
}

describe("BaseCombobox", () => {
  it("shows no search field for a short list and picks with the click", async () => {
    render(<Harness n={3} />);
    await userEvent.click(screen.getByRole("button", { name: /Choice/ }));
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
    await userEvent.click(screen.getByText("Option 1"));
    expect(screen.getByLabelText("value")).toHaveTextContent("v1");
    expect(screen.getByRole("button", { name: /Option 1/ })).toBeInTheDocument();
  });

  it("shows a search field from six options and filters by typing", async () => {
    render(<Harness n={8} />);
    await userEvent.click(screen.getByRole("button", { name: /Choice/ }));
    await userEvent.type(screen.getByRole("combobox"), "Option 7");
    expect(screen.getByText("Option 7")).toBeInTheDocument();
    expect(screen.queryByText("Option 2")).not.toBeInTheDocument();
  });

  it("picks with the keyboard", async () => {
    render(<Harness n={8} />);
    await userEvent.click(screen.getByRole("button", { name: /Choice/ }));
    await userEvent.keyboard("{ArrowDown}{Enter}");
    expect(screen.getByLabelText("value").textContent).not.toBe("");
  });
});

describe("BaseConfirm", () => {
  it("asks first and runs only after the danger button", async () => {
    const onConfirm = vi.fn();
    render(<BaseConfirm message="Delete this subtask?" trigger={<BaseButton>Delete</BaseButton>} onConfirm={onConfirm} />);
    await userEvent.click(screen.getByRole("button", { name: "Delete" }));
    expect(onConfirm).not.toHaveBeenCalled();
    expect(screen.getByText("Delete this subtask?")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onConfirm).not.toHaveBeenCalled();
    await userEvent.click(screen.getByRole("button", { name: "Delete" }));
    const confirm = screen.getAllByRole("button", { name: "Delete" }).find((b) => b.getAttribute("data-variant") === "danger");
    await userEvent.click(confirm!);
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });
});

describe("BaseTooltip", () => {
  it("shows its label on keyboard focus", async () => {
    render(
      <BaseTooltip label="Member One">
        <BaseButton>Avatar</BaseButton>
      </BaseTooltip>,
    );
    await userEvent.tab();
    expect((await screen.findAllByText("Member One")).length).toBeGreaterThan(0);
  });
});

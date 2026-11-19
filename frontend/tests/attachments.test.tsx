import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AttachmentList } from "@/components/card/AttachmentList";
import { CardModal } from "@/components/card/CardModal";
import { api } from "@/lib/api";
import type { Attachment, Board, Card, Column } from "@/lib/types";

const link = { id: "a1", card_id: "c1", name: "Design brief", url: "https://example.com/brief", file_url: null, mime_type: null } as unknown as Attachment;

const card = {
  id: "c1",
  column_id: "col1",
  title: "Design page",
  description: null,
  priority: "medium",
  start_date: null,
  end_date: null,
  category_id: null,
  assignee_id: null,
  order: 1,
  attachments: [link],
  subtasks: [{ id: "s1", card_id: "c1", title: "Outline", is_done: false, order: 1 }],
  comments: [],
  activity: [],
} as unknown as Card;

vi.mock("@/lib/api", () => ({
  api: {
    attachments: { addLink: vi.fn(async () => link), upload: vi.fn(), remove: vi.fn(async () => null), freshUrl: vi.fn() },
    cards: { get: vi.fn(async () => card), update: vi.fn(async () => card), remove: vi.fn(async () => null), archive: vi.fn(), activity: vi.fn(async () => []) },
    boards: { members: vi.fn(async () => []) },
    comments: { list: vi.fn(async () => []) },
    subtasks: { remove: vi.fn(async () => null), update: vi.fn(), create: vi.fn() },
  },
}));
vi.mock("@/components/shell/ShellContext", () => ({
  useShell: () => ({ session: { userId: "u1", role: "manager" } }),
}));

const noop = () => undefined;
const list = (over: Partial<React.ComponentProps<typeof AttachmentList>> = {}) => (
  <AttachmentList attachments={[link]} removedIds={[]} staged={[]} canEdit onStage={noop} onUnstage={noop} onRemove={noop} {...over} />
);

describe("AttachmentList", () => {
  beforeEach(() => vi.clearAllMocks());

  it("lists existing attachments that open in a new tab", () => {
    render(list());
    expect(screen.getByRole("link", { name: "Design brief" })).toHaveAttribute("target", "_blank");
  });

  it("shows only the chosen type: Link by default, File after the selector changes", async () => {
    render(list({ attachments: [] }));
    await userEvent.click(screen.getByRole("button", { name: "Add attachment" }));
    expect(screen.getByLabelText("Attachment link")).toBeInTheDocument();
    expect(screen.queryByLabelText("Upload file")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Type: Link/ }));
    await userEvent.click(screen.getByText("File"));
    expect(screen.getByLabelText("Upload file")).toBeInTheDocument();
    expect(screen.queryByLabelText("Attachment link")).not.toBeInTheDocument();
  });

  it("stages a link instead of sending it", async () => {
    const onStage = vi.fn();
    render(list({ attachments: [], onStage }));
    await userEvent.click(screen.getByRole("button", { name: "Add attachment" }));
    await userEvent.type(screen.getByLabelText("Attachment link"), "https://example.com/x");
    await userEvent.click(screen.getByRole("button", { name: "Add" }));
    expect(onStage).toHaveBeenCalledWith(expect.objectContaining({ kind: "link", url: "https://example.com/x" }));
    expect(api.attachments.addLink).not.toHaveBeenCalled();
  });

  it("hides a removed attachment and shows a pending one", () => {
    render(list({ removedIds: ["a1"], staged: [{ key: "k", kind: "link", url: "https://example.com/new" }] }));
    expect(screen.queryByRole("link", { name: "Design brief" })).not.toBeInTheDocument();
    expect(screen.getByText("https://example.com/new")).toBeInTheDocument();
    expect(screen.getByText("Pending")).toBeInTheDocument();
  });

  it("asks before removing, then reports the removal to the draft", async () => {
    const onRemove = vi.fn();
    render(list({ onRemove }));
    await userEvent.click(screen.getByRole("button", { name: "Remove Design brief" }));
    expect(onRemove).not.toHaveBeenCalled();
    await userEvent.click(screen.getByRole("button", { name: "Remove" }));
    expect(onRemove).toHaveBeenCalledWith("a1");
  });

  it("offers no add control or Remove to a viewer who cannot edit", () => {
    render(list({ canEdit: false }));
    expect(screen.queryByRole("button", { name: "Add attachment" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Remove/ })).not.toBeInTheDocument();
  });

  it("says so when there are no attachments", () => {
    render(list({ attachments: [], canEdit: false }));
    expect(screen.getByText("No attachments.")).toBeInTheDocument();
  });
});

const board = { id: "b1", name: "B", visibility: "private", columns: [] } as unknown as Board;
const columns = [{ id: "col1", name: "Todo", order: 1 }] as unknown as Column[];
const modal = (onClose = noop) => render(<CardModal cardId="c1" board={board} columns={columns} categories={[]} onClose={onClose} onChanged={noop} onDeleted={noop} />);

describe("CardModal drafts", () => {
  beforeEach(() => vi.clearAllMocks());

  it("sends an attachment removal only when Save changes is clicked", async () => {
    modal();
    await userEvent.click(await screen.findByRole("button", { name: "Remove Design brief" }));
    await userEvent.click(screen.getByRole("button", { name: "Remove" }));
    expect(api.attachments.remove).not.toHaveBeenCalled();
    await userEvent.click(screen.getByRole("button", { name: "Save changes" }));
    expect(api.attachments.remove).toHaveBeenCalledWith("a1");
  });

  it("asks to discard when closing with unsaved changes, and closes at once when there are none", async () => {
    const onClose = vi.fn();
    modal(onClose);
    await userEvent.click(await screen.findByRole("button", { name: "Close" }));
    expect(onClose).toHaveBeenCalledTimes(1);
    onClose.mockClear();
    await userEvent.click(screen.getByRole("button", { name: "Edit title" }));
    await userEvent.type(screen.getByLabelText("Title"), "x");
    await userEvent.click(screen.getAllByRole("button", { name: "Close" })[0]);
    expect(onClose).not.toHaveBeenCalled();
    expect(screen.getByText("Discard changes?")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Discard" }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("asks before deleting a subtask and before deleting the card", async () => {
    modal();
    await userEvent.click(await screen.findByRole("button", { name: "Delete subtask Outline" }));
    expect(api.subtasks.remove).not.toHaveBeenCalled();
    const ask = screen.getByText('Delete subtask "Outline"?').parentElement as HTMLElement;
    await userEvent.click(within(ask).getByRole("button", { name: "Delete" }));
    expect(api.subtasks.remove).toHaveBeenCalledWith("s1");

    await userEvent.click(screen.getByRole("button", { name: "Delete" }));
    expect(api.cards.remove).not.toHaveBeenCalled();
    const askCard = screen.getByText(/Delete this card\?/).parentElement as HTMLElement;
    await userEvent.click(within(askCard).getByRole("button", { name: "Delete" }));
    expect(api.cards.remove).toHaveBeenCalledWith("c1");
  });

  it("uses plain attribute rows, no column select, and the footer button roles", async () => {
    modal();
    await screen.findByRole("button", { name: "Edit title" });
    for (const name of [/^Column: Todo/, /^Label: /, /^Priority: Medium/, /^Dates: /, /^Assignee: /]) {
      expect(screen.getAllByLabelText(name).length).toBeGreaterThan(0);
    }
    expect(screen.queryByLabelText("Move to column")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Archive" })).toHaveAttribute("data-variant", "secondary");
    expect(screen.getByRole("button", { name: "Delete" })).toHaveAttribute("data-variant", "danger");
    expect(screen.getByRole("button", { name: "Save changes" })).toHaveAttribute("data-variant", "primary");
  });
});

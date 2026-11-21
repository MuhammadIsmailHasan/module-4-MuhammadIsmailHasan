"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { CardModal } from "@/components/card/CardModal";
import { BaseAlert } from "@/components/shared/BaseField";
import { useShell } from "@/components/shell/ShellContext";
import { api } from "@/lib/api";
import { ApiError } from "@/lib/http";
import { computeDropOrder, needsRebalance } from "@/lib/ordering";
import type { Board as BoardT, Card, Category, Comment, Member } from "@/lib/types";
import { Board } from "./Board";
import { BoardHeader } from "./BoardHeader";

interface BoardViewProps {
  board: BoardT;
  initialCards: Card[];
  initialCategories: Category[];
}

export function BoardView({ board, initialCards, initialCategories }: BoardViewProps) {
  const { session } = useShell();
  const columns = board.columns ?? [];
  const [cards, setCards] = useState(initialCards);
  const [categories, setCategories] = useState(initialCategories);
  const [members, setMembers] = useState<Member[]>([]);
  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState<string | null>(null);
  const [openId, setOpenId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const first = useRef(true);
  const params = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const cardParam = params.get("card");
  const [notice, setNotice] = useState<string | null>(null);
  const role = session?.role;
  const staff = role === "supervisor" || role === "manager" || role === "admin";

  // Re-fetch the categories on a board switch, never from a hard-coded list.
  useEffect(() => {
    let live = true;
    api.categories.listForBoard(board.id).then((c) => live && setCategories(c)).catch(() => undefined);
    return () => {
      live = false;
    };
  }, [board.id]);

  useEffect(() => {
    let live = true;
    api.boards.members(board.id).then((m) => live && setMembers(m)).catch(() => live && setMembers([]));
    return () => {
      live = false;
    };
  }, [board.id]);

  // A Notification link: open the Card after the Board loads, or say why it cannot be opened (Requirement 28, criteria 7 and 8).
  useEffect(() => {
    if (!cardParam) return;
    let live = true;
    setNotice(null);
    api.cards
      .get(cardParam)
      .then((c) => {
        if (!live) return;
        if (!columns.some((col) => col.id === c.column_id)) return void setNotice("This card is no longer available.");
        if (c.archived_at) return void setNotice("This card is archived.");
        setCards((all) => (all.some((x) => x.id === c.id) ? all : [...all, c]));
        setOpenId(c.id);
      })
      .catch(() => live && setNotice("This card is no longer available."));
    return () => {
      live = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cardParam, board.id]);

  function closeCard() {
    setOpenId(null);
    if (params.get("card")) router.replace(pathname);
  }

  const refetch = useCallback(async () => {
    try {
      setCards(await api.cards.listForBoard(board.id, { search: search || undefined, category: categoryId ?? undefined }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load cards.");
    }
  }, [board.id, search, categoryId]);

  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    const t = setTimeout(refetch, 250);
    return () => clearTimeout(t);
  }, [refetch]);

  async function onMove(cardId: string, columnId: string, index: number) {
    const snapshot = cards;
    const moving = cards.find((c) => c.id === cardId);
    if (!moving) return;
    const siblings = cards.filter((c) => c.column_id === columnId && c.id !== cardId).sort((a, b) => a.order - b.order);
    const order = computeDropOrder(siblings.map((s) => s.order), index);
    const prev = siblings[index - 1] ?? null;
    const next = siblings[index] ?? null;
    setError(null);
    setCards((all) => all.map((c) => (c.id === cardId ? { ...c, column_id: columnId, order } : c)));
    try {
      const saved = await api.cards.move(cardId, { column_id: columnId, prev: prev?.id ?? null, next: next?.id ?? null });
      setCards((all) => all.map((c) => (c.id === cardId ? { ...c, ...saved } : c)));
      if (needsRebalance(prev?.order ?? null, next?.order ?? null)) await refetch();
    } catch (err) {
      setCards(snapshot);
      setError(err instanceof ApiError ? err.message : "Could not move the card.");
    }
  }

  async function onCreate(columnId: string, title: string) {
    setError(null);
    try {
      const card = await api.cards.create(columnId, { title });
      setCards((all) => [...all, card]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not add the card.");
      throw err;
    }
  }

  async function createFromComment(comment: Comment) {
    const target = columns[0];
    if (!target) return;
    const card = await api.cards.create(target.id, {
      title: comment.content.slice(0, 255),
      description: comment.content,
    });
    setCards((all) => [...all, card]);
  }

  const open = cards.find((c) => c.id === openId) ?? null;

  return (
    <div className="flex h-full flex-col">
      <BoardHeader
        board={board}
        cards={cards}
        members={members}
        categories={categories}
        categoryId={categoryId}
        search={search}
        onSearch={setSearch}
        onCategory={setCategoryId}
      />
      {notice && (
        <div className="shrink-0 px-4 pt-4 lg:px-8">
          <BaseAlert tone="info">{notice}</BaseAlert>
        </div>
      )}
      {error && (
        <div className="shrink-0 px-4 pt-4 lg:px-8">
          <BaseAlert>{error}</BaseAlert>
        </div>
      )}
      <Board
        columns={columns}
        cards={cards}
        categories={categories}
        members={members}
        canMove={!!session}
        canCreate={staff}
        onOpen={(c) => setOpenId(c.id)}
        onMove={onMove}
        onCreate={onCreate}
      />
      {open && (
        <CardModal
          cardId={open.id}
          board={board}
          columns={columns}
          categories={categories}
          onClose={closeCard}
          onChanged={(card) => setCards((all) => all.map((c) => (c.id === card.id ? { ...c, ...card } : c)))}
          onDeleted={(id) => {
            setCards((all) => all.filter((c) => c.id !== id));
            closeCard();
          }}
          onCreateCardFromComment={staff ? createFromComment : undefined}
        />
      )}
    </div>
  );
}

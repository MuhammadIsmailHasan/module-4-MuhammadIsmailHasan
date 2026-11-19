import { notFound, redirect } from "next/navigation";
import { BoardView } from "@/components/board/BoardView";
import { ApiError } from "@/lib/http";
import { serverGet } from "@/lib/server";
import type { Board, Card, Category } from "@/lib/types";

export default async function BoardPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    const [board, cards, categories] = await Promise.all([
      serverGet<Board>(`/boards/${id}`),
      serverGet<Card[]>(`/boards/${id}/cards`),
      serverGet<Category[]>(`/boards/${id}/categories`),
    ]);
    return <BoardView key={board.id} board={board} initialCards={cards} initialCategories={categories} />;
  } catch (err) {
    if (err instanceof ApiError) {
      if (err.httpStatus === 404) notFound();
      if (err.httpStatus === 401) redirect("/login");
      if (err.httpStatus === 403) {
        return (
          <div className="flex flex-col items-center gap-2 px-4 py-12 text-center">
            <h2 className="text-xl font-bold">No access</h2>
            <p className="text-ink-muted">You are not a member of this board.</p>
          </div>
        );
      }
    }
    throw err;
  }
}

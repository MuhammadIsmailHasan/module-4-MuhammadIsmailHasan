import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { BoardUnavailable } from "@/components/board/BoardUnavailable";
import { BoardView } from "@/components/board/BoardView";
import { ApiError } from "@/lib/http";
import { serverGet } from "@/lib/server";
import type { Board, Card, Category } from "@/lib/types";

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  try {
    return { title: (await serverGet<Board>(`/boards/${id}`)).name };
  } catch {
    return { title: "Board" };
  }
}

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
    if (err instanceof ApiError && (err.httpStatus === 404 || err.httpStatus === 403)) return <BoardUnavailable />;
    if (err instanceof ApiError && err.httpStatus === 401) redirect("/login");
    throw err;
  }
}

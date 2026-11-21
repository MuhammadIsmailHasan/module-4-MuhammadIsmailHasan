import type { Metadata } from "next";
import { serverGet } from "@/lib/server";
import type { Board } from "@/lib/types";
import { CategoriesScreen } from "@/components/board/CategoriesScreen";

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  try {
    return { title: `Categories · ${(await serverGet<Board>(`/boards/${id}`)).name}` };
  } catch {
    return { title: "Categories" };
  }
}

export default async function CategoriesPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <CategoriesScreen boardId={id} />;
}

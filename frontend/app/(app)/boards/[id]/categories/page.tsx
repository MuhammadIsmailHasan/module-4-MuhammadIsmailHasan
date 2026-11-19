import { CategoriesScreen } from "@/components/board/CategoriesScreen";

export default async function CategoriesPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <CategoriesScreen boardId={id} />;
}

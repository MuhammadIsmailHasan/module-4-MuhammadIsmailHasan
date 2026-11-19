import { AuthForm } from "@/components/AuthForm";
import { AuthSplitLayout } from "@/components/AuthSplitLayout";

export const metadata = { title: "Log in · Kanban" };

export default function LoginPage() {
  return (
    <AuthSplitLayout>
      <AuthForm mode="login" />
    </AuthSplitLayout>
  );
}

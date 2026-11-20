import { AuthForm } from "@/components/AuthForm";
import { AuthSplitLayout } from "@/components/AuthSplitLayout";

export const metadata = { title: "Register · RevoTask" };

export default function RegisterPage() {
  return (
    <AuthSplitLayout>
      <AuthForm mode="register" />
    </AuthSplitLayout>
  );
}

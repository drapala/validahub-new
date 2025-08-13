"use client";

import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6)
});

export default function LoginPage() {
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
  });
  const router = useRouter();

  const onSubmit = async (values: z.infer<typeof schema>) => {
    try {
      await api.login(values.email, values.password);
      toast.success("Login realizado");
      router.push("/upload");
    } catch (e: any) {
      toast.error(e?.message ?? "Falha no login");
    }
  };

  return (
    <main className="container-app py-12 max-w-md">
      <h1 className="text-3xl font-semibold mb-6">Entrar</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <input className="input w-full" placeholder="Email" type="email" {...register("email")} />
        <input className="input w-full" placeholder="Senha" type="password" {...register("password")} />
        <button disabled={isSubmitting} className="btn btn-primary w-full" type="submit">
          {isSubmitting ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </main>
  );
}
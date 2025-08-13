export default function PricingPage() {
  return (
    <main className="container-app py-12">
      <h1 className="text-3xl font-semibold mb-6">Pricing</h1>
      <div className="grid gap-6 md:grid-cols-3">
        <div className="card p-6">
          <h2 className="text-xl font-medium">SMB</h2>
          <p className="text-zinc-400">Até 1k linhas por job</p>
        </div>
        <div className="card p-6">
          <h2 className="text-xl font-medium">Pro</h2>
          <p className="text-zinc-400">Volume com jobs assíncronos</p>
        </div>
        <div className="card p-6">
          <h2 className="text-xl font-medium">Enterprise</h2>
          <p className="text-zinc-400">Conectores, SLA e suporte</p>
        </div>
      </div>
    </main>
  );
}
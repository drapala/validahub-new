"use client";

export function CategoryPicker({
  marketplace,
  category,
  onChange
}: {
  marketplace: string;
  category: string;
  onChange: (mp: string, cat: string) => void;
}) {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      <select
        className="input"
        value={marketplace}
        onChange={(e) => onChange(e.target.value, category)}
      >
        <option value="">Selecione o marketplace</option>
        <option value="amazon">Amazon</option>
        <option value="mercadolivre">Mercado Livre</option>
        <option value="magalu">Magalu</option>
      </select>
      <select
        className="input"
        value={category}
        onChange={(e) => onChange(marketplace, e.target.value)}
      >
        <option value="">Selecione a categoria</option>
        <option value="electronics">Eletrônicos</option>
        <option value="fashion">Moda</option>
        <option value="home">Casa</option>
      </select>
    </div>
  );
}
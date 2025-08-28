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
        <option value="MERCADO_LIVRE">Mercado Livre</option>
        <option value="SHOPEE">Shopee</option>
        <option value="AMAZON">Amazon</option>
        <option value="MAGALU">Magalu</option>
        <option value="AMERICANAS">Americanas</option>
      </select>
      <select
        className="input"
        value={category}
        onChange={(e) => onChange(marketplace, e.target.value)}
      >
        <option value="">Selecione a categoria</option>
        <option value="ELETRONICOS">Eletrônicos</option>
        <option value="MODA">Moda</option>
        <option value="CASA">Casa e Decoração</option>
        <option value="ESPORTES">Esportes</option>
        <option value="LIVROS">Livros</option>
        <option value="BELEZA">Beleza</option>
        <option value="BRINQUEDOS">Brinquedos</option>
        <option value="ALIMENTOS">Alimentos</option>
        <option value="AUTOMOTIVO">Automotivo</option>
        <option value="OUTROS">Outros</option>
      </select>
    </div>
  );
}
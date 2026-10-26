import Link from "next/link";

export function Header() {
  return <header className="site-header"><Link className="brand" href="/login"><span className="brand-mark">M</span><span>moeda</span></Link><nav><Link href="/login">Entrar</Link><Link href="/cadastro/aluno">Aluno</Link></nav></header>;
}
